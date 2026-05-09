import re
import inspect
import os

import torch
import torch.nn as nn
from espnet2.bin.s2t_inference_ctc import Speech2Text


def _normalize_peft_type_name(peft_type):
    if hasattr(peft_type, "value"):
        return str(peft_type.value).lower()
    return str(peft_type).lower()


def _resolve_peft_config_class(peft_type_name, config_mapping):
    normalized = peft_type_name.lower()
    for key, cls in config_mapping.items():
        if _normalize_peft_type_name(key) == normalized:
            return cls
    available = sorted(_normalize_peft_type_name(k) for k in config_mapping.keys())
    raise ValueError(
        f"Unsupported PEFT type: {peft_type_name}. "
        f"Available types from installed peft: {available}"
    )


def _resolve_task_type(task_type, task_type_enum):
    if task_type is None or task_type_enum is None:
        return task_type
    if isinstance(task_type, task_type_enum):
        return task_type
    if isinstance(task_type, str):
        upper = task_type.upper()
        if hasattr(task_type_enum, upper):
            return getattr(task_type_enum, upper)
        for member in task_type_enum:
            if str(member.value).upper() == upper:
                return member
        raise ValueError(f"Unknown task_type: {task_type}")
    return task_type


def _supports_task_type(config_cls):
    try:
        return "task_type" in inspect.signature(config_cls.__init__).parameters
    except (TypeError, ValueError):
        return False


def _build_tuner_model_mapping():
    try:
        import peft.tuners as tuners
    except Exception:
        return {}

    mapping = {}
    for attr in dir(tuners):
        if not attr.endswith("Model"):
            continue
        cls = getattr(tuners, attr, None)
        if cls is None:
            continue
        tuner_key = attr[:-5].lower()
        mapping[tuner_key] = cls
    return mapping


def _load_speech2text_from_pretrained(model_tag, **kwargs):
    cache_dir = os.getenv("ESPNET_MODEL_ZOO_CACHE", ".cache/espnet_model_zoo")
    try:
        from espnet_model_zoo.downloader import ModelDownloader
    except Exception:
        return Speech2Text.from_pretrained(model_tag, **kwargs)

    try:
        downloader = ModelDownloader(cachedir=cache_dir)
        model_kwargs = downloader.download_and_unpack(model_tag)
        model_kwargs.update(kwargs)
        return Speech2Text(**model_kwargs)
    except Exception:
        return Speech2Text.from_pretrained(model_tag, **kwargs)


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
        from peft import PeftModel, get_peft_model
        try:
            from peft.mapping import PEFT_TYPE_TO_CONFIG_MAPPING
        except Exception:
            # Fallback for PEFT versions exposing mapping elsewhere.
            from peft import PEFT_TYPE_TO_CONFIG_MAPPING
        try:
            from peft import TaskType
        except Exception:
            TaskType = None
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

        peft_type = str(peft.pop("type", "lora")).lower()
        config_cls = _resolve_peft_config_class(peft_type, PEFT_TYPE_TO_CONFIG_MAPPING)

        if _supports_task_type(config_cls):
            task_type = _resolve_task_type(peft.pop("task_type", None), TaskType)
            if task_type is None and TaskType is not None:
                task_type = (
                    TaskType.SEQ_2_SEQ_LM
                    if hasattr(model, "generate")
                    else TaskType.FEATURE_EXTRACTION
                )
            if task_type is not None:
                peft["task_type"] = task_type

        config = config_cls(**peft)

        try:
            return get_peft_model(model, config)
        except Exception:
            if hasattr(model, "prepare_inputs_for_generation") or hasattr(model, "generate"):
                raise

            tuner_cls = _build_tuner_model_mapping().get(peft_type)
            if tuner_cls is None:
                raise
            return tuner_cls(model, config, "default")

    return get_peft_model(model, peft)


class OWSMFinetune(nn.Module):
    def __init__(self, model_tag, peft=None):
        super().__init__()
        owsm_model = _load_speech2text_from_pretrained(model_tag)
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
        prefix,
        prefix_lengths,
    ):
        return self.model(
            speech=speech,
            speech_lengths=speech_lengths,
            text=text,
            text_lengths=text_lengths,
            text_prev=text_prev,
            text_prev_lengths=text_prev_lengths,
            text_ctc=text_ctc,
            text_ctc_lengths=text_ctc_lengths,
            prefix=prefix,
            prefix_lengths=prefix_lengths,
        )

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
        self.s2t = _load_speech2text_from_pretrained(
            model_tag=model_tag,
            lang_sym=lang_sym,
            device=str(device),
        )
        if checkpoint_path is not None:
            state = torch.load(checkpoint_path, map_location="cpu")["state_dict"]
            self.s2t.s2t_model.load_state_dict(
                {k.replace("model.", ""): v for k, v in state.items() if k.startswith("model.")}
            )

    def forward(self, speech, lang_sym=None):
        return {
            "text": self.s2t(speech, lang_sym=lang_sym)[0][3],
        }


def _strip_task_prefix(text: str) -> str:
    return re.sub(r"^(?:<[^>]+>)+\s*", "", text)


def owsm_output_fn(*, data, model_output, idx):
    uttid = data.get("uttid", str(idx))
    hyp = model_output['text']
    ref = data.get("text_raw", data.get("text_ctc", ""))
    out = {
        "uttid": uttid,
        "hyp": _strip_task_prefix(hyp),
        "ref": _strip_task_prefix(ref)
    }
    if "lang_sym" in data:
        out["lang_sym"] = data["lang_sym"]
    if "subset" in data:
        out["subset"] = data["subset"]
    return out
