import torch
import torch.nn as nn
from functools import lru_cache
from espnet2.bin.s2t_inference import Speech2Text

from espnet2.legacy.nets.pytorch_backend.nets_utils import th_accuracy


def _maybe_apply_peft(model, peft):
    if peft is None:
        return model

    print(f"Applying PEFT: {peft}")
    if isinstance(peft, dict):
        peft_type = peft.get("type")
        if peft_type in ("espnet_lora", "espnet2_lora", "lora_espnet"):
            try:
                from espnet2.layers.create_adapter_fn import create_lora_adapter
            except Exception as exc:
                raise ImportError(
                    "ESPnet LoRA is requested but espnet2.layers.create_adapter_fn is not available."
                ) from exc
            peft = dict(peft)
            peft.pop("type", None)
            return create_lora_adapter(model, **peft)

    try:
        from peft import (
            AdaLoraConfig,
            DeloraConfig,
            LoraConfig,
            RandLoraConfig,
            TaskType,
            VBLoRAConfig,
            XLoraConfig,
            get_peft_model,
            PeftModel,
        )
    except Exception as exc:
        raise ImportError(
            "PEFT is requested but the 'peft' package is not available. "
            "Install peft or set peft=None."
        ) from exc

    if isinstance(peft, str):
        return PeftModel.from_pretrained(model, peft)

    if isinstance(peft, dict):
        peft = dict(peft)
        if "pretrained" in peft:
            adapter_path = peft.pop("pretrained")
            return PeftModel.from_pretrained(model, adapter_path, **peft)

        peft_type = peft.pop("type", "lora")

        config_cls_map = {
            "lora": LoraConfig,
            "adalora": AdaLoraConfig,
            "delora": DeloraConfig,
            "randlora": RandLoraConfig,
            "vblora": VBLoRAConfig,
            "xlora": XLoraConfig,
        }
        config_cls = config_cls_map.get(peft_type)
        if config_cls is None:
            raise ValueError(f"Unsupported PEFT type: {peft_type}")

        task_type = peft.pop("task_type", None)
        if peft_type in ("lora", "adalora"):
            if isinstance(task_type, str):
                task_type = getattr(TaskType, task_type.upper())
            if task_type is None:
                task_type = TaskType.SEQ_2_SEQ_LM if hasattr(model, "generate") else TaskType.FEATURE_EXTRACTION
            config = config_cls(task_type=task_type, **peft)
        else:
            # Other PEFT configs do not accept task_type.
            config = config_cls(**peft)

        # For non-transformers models (e.g., ESPnet), avoid PeftModel wrappers
        # that expect generation helpers like prepare_inputs_for_generation.
        if not hasattr(model, "prepare_inputs_for_generation") and not hasattr(model, "generate"):
            from peft.tuners import (
                AdaLoraModel,
                DeloraModel,
                LoraModel,
                RandLoraModel,
                VBLoRAModel,
                XLoraModel,
            )

            tuner_cls_map = {
                "lora": LoraModel,
                "adalora": AdaLoraModel,
                "delora": DeloraModel,
                "randlora": RandLoraModel,
                "vblora": VBLoRAModel,
                "xlora": XLoraModel,
            }
            tuner_cls = tuner_cls_map[peft_type]
            return tuner_cls(model, config, "default")
        return get_peft_model(model, config)

    return get_peft_model(model, peft)


class OWSMFinetune(nn.Module):
    def __init__(self, model_tag, peft=None):
        super().__init__()
        owsm_model = Speech2Text.from_pretrained(model_tag)
        m = _maybe_apply_peft(owsm_model.s2t_model, peft)
        
        total_params = sum(p.numel() for p in owsm_model.s2t_model.parameters())
        trainable_params = sum(p.numel() for p in owsm_model.s2t_model.parameters() if p.requires_grad)
        print(f"Total parameters: {total_params}")
        print(f"Trainable parameters: {trainable_params}")

        if m is not None:
            self.model = m
        else:
            self.model = owsm_model.s2t_model

    def forward(
        self,
        speech,
        speech_lengths,
        text,
        text_lengths,
        text_ctc,
        text_ctc_lengths,
        text_prev,
        text_prev_lengths,
    ):
        return self.model(
            speech,
            speech_lengths,
            text,
            text_lengths,
            text_prev,
            text_prev_lengths,
            text_ctc,
            text_ctc_lengths,
        )

    def collect_feats(
        self,
        speech: torch.Tensor,
        speech_lengths: torch.Tensor,
        **kwargs,
    ):
        return {"feats": speech, "feats_lengths": speech_lengths}


class WhisperFinetune(nn.Module):
    def __init__(self, model_tag, peft=None):
        super().__init__()
        # get whisper model and preprocessor from transformers
        from transformers import WhisperForConditionalGeneration, AutoProcessor
        self.processor = AutoProcessor.from_pretrained(model_tag)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_tag)
        self.model = _maybe_apply_peft(self.model, peft)
        self.model = self.model.to(torch.float32)  # use float32 for stability, can be changed to bf16 later
        
        # init error calculator
        from espnet2.legacy.nets.e2e_asr_common import ErrorCalculator
        # get token_list from whisper model
        token_list = self.processor.tokenizer.get_vocab()
        token_list = sorted(token_list, key=token_list.get)
        # we will not use them. init by random
        sym_space, sym_blank = "<space>", "<blank>"
        self.error_calculator = ErrorCalculator(char_list=token_list, sym_space=sym_space, sym_blank=sym_blank, report_cer=True, report_wer=True)

    def forward(
        self,
        speech,
        speech_lengths,
        text,
        text_lengths,
        **kwargs,
    ):
        # transpose back to (B, D, T') for whisper
        speech = speech.transpose(1, 2)  # (B, D, T')
        # pad to 30 seconds (3000 frames after processing)
        speech = torch.nn.functional.pad(speech, (0, max(0, 3000 - speech.size(2))), value=0.0)[:, :, :3000]  # (B, D, 3000)
        attention_mask = torch.arange(3000).expand(len(speech_lengths), 3000).to(speech.device) < speech_lengths.unsqueeze(1)  # (B, 3000)
        
        # make decoder input ids and labels
        decoder_input_ids = text[:, :-1][:,:self.model.config.max_target_positions]  # (B, L-1)
        labels = text[:, 1:][:,:self.model.config.max_target_positions]  # (B, L-1)
        
        output = self.model(input_features=speech, attention_mask=attention_mask, decoder_input_ids=decoder_input_ids, labels=labels)
        # breakpoint()
        loss = output.loss
        acc = th_accuracy(output.logits.reshape(-1, output.logits.size(-1)), labels, ignore_label=50256)        # 50256 is ""
        cer_att, wer_att = None, None
        if not self.training:
            ys_hat = output.logits.argmax(dim=-1)
            cer_att, wer_att = self.error_calculator(ys_hat.detach().cpu().numpy(), labels.detach().cpu().numpy())
            cer_att, wer_att = torch.tensor(cer_att), torch.tensor(wer_att)
        stats = {
            "loss": loss,
            "acc": torch.tensor(acc),
            "cer_att": cer_att,
            "wer_att": wer_att,
        }
        return loss, stats, torch.tensor(speech.size(0))

    def collect_feats(
        self,
        speech: torch.Tensor,
        speech_lengths: torch.Tensor,
        **kwargs,
    ):
        return {"feats": speech, "feats_lengths": speech_lengths}


class OWSMV4BaseInferenceModel(nn.Module):
    def __init__(
        self,
        *,
        model_tag: str,
        lang_sym: str,
        checkpoint_path: str,
        device: str = "cpu",
    ) -> None:
        super().__init__()
        self.s2t = Speech2Text.from_pretrained(
            model_tag=model_tag,
            lang_sym=lang_sym,
            device=str(device),
        )
        if checkpoint_path is not None:
            state = torch.load(checkpoint_path, map_location="cpu")["state_dict"]
            # breakpoint()
            self.s2t.s2t_model.load_state_dict(
                {k.replace("model.", ""): v for k, v in state.items() if k.startswith("model.")}
            )

    def forward(self, speech):
        return self.s2t(speech)

class WhisperInferenceModel(nn.Module):
    def __init__(self, model_tag, checkpoint_path=None, device="cpu"):
        super().__init__()
        # get whisper model and preprocessor from transformers
        from transformers import WhisperForConditionalGeneration, AutoProcessor
        self.processor = AutoProcessor.from_pretrained(model_tag)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_tag)
        self.model = self.model.to(device)
        if checkpoint_path is not None:
            state = torch.load(checkpoint_path, map_location="cpu")["state_dict"]
            # breakpoint()
            # self.model.load_state_dict(
            #     {k.replace("model.model.", "model."): v for k, v in state.items() if k.startswith("model.model.")}
            # )
            self.load_state_dict(state)
        self.model = self.model.to(torch.float32)  # use float32 for stability, can be changed to bf16 later
    
    def forward(
        self,
        speech,
    ):
        # transcribe the input speech waveform (1, T) to text
        # preprocess speech
        processed = self.processor(
            speech,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True,
        )
        # pad input features to 30 seconds (3000 frames after processing)
        attention_mask = torch.arange(3000).expand(len(processed["input_features"]), 3000).to(self.model.device) < (processed["input_features"].size(2))  # (B, 3000)
        input_features = torch.nn.functional.pad(
            processed["input_features"],  # (B, D, T')
            (0, max(0, 3000 - processed["input_features"].size(2))),  # pad to 3000
            value=0.0,
        )[:, :, :3000].to(self.model.device)  # (B, D, T')
        # breakpoint()
        # generate tokens
        generated_ids = self.model.generate(input_features=input_features, attention_mask=attention_mask)  # (1, L)
        # detokenize
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        # return the first (and only) generated text
        return generated_text[0]

@lru_cache(maxsize=1)
def _get_cached_owsm_tokenizer():
    s2t = Speech2Text.from_pretrained(
            model_tag="espnet/owsm_v4_medium_1B",
            lang_sym="<por>",
            device="cpu",
        )
    tokenizer = s2t.tokenizer
    converter = s2t.converter
    return tokenizer, converter


def detokenize(ids):
    tokenizer, converter = _get_cached_owsm_tokenizer()
    return tokenizer.tokens2text(converter.ids2tokens(ids))


def owsm_output_fn(*, data, model_output, idx):
    uttid = data.get("uttid", str(idx))
    hyp = model_output[0][3]
    # remove the prefix "<por><asr><notimestamps>"
    hyp = hyp.replace("<por><asr><notimestamps>", "")
    # breakpoint()
    # ref = detokenize(
    #     data["text_raw"]
    # )
    ref = data["text_raw"]
    return {"uttid": uttid, "hyp": hyp, "ref": ref}

def whisper_output_fn(*, data, model_output, idx):
    uttid = data.get("uttid", str(idx))
    hyp = model_output
    # remove the prefix "<por><asr><notimestamps>"
    hyp = hyp.replace("<por><asr><notimestamps>", "")
    # breakpoint()
    # ref = detokenize(
    #     data["text_raw"]
    # )
    ref = data["text_raw"]
    return {"uttid": uttid, "hyp": hyp, "ref": ref}
