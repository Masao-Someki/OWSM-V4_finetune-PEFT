import numpy as np
from datasets import Audio, load_from_disk
from torch.utils.data import Dataset

PORTUGAL_DATA_DIR = "/work/nvme/bbjs/clin10/eurospeech_finetune/espnet/egs3/eurospeech_portugal/s2t1/data/portugal"

class EuroSpeechPortugalDataset(Dataset):
    def __init__(self, data_dir=PORTUGAL_DATA_DIR, split="train", ratio=1.0):
        if not (0 < ratio <= 1.0):
            raise ValueError("ratio must be in the range (0, 1].")
        
        dataset_dict = load_from_disk(data_dir)
        if split in dataset_dict:
            self.dataset = dataset_dict[split]
        else:
            raise ValueError(f"Split '{split}' not found in dataset.")

        if ratio < 1.0:
            keep = int(len(self.dataset) * ratio)
            self.dataset = self.dataset.select(range(keep))

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        transcript = item["human_transcript"]
        example = {
            "speech": item["audio"]["array"].astype(np.float32),
            "text": f"<por><asr><notimestamps> {transcript}",
            "text_ctc": transcript,
            "text_prev": "<na>",
        }
        return example


class WhisperTokenizeTransform:
    def __init__(self, model_tag, text_cleaner=None, *args, **kwargs):
        from transformers import WhisperProcessor
        self.processor = WhisperProcessor.from_pretrained(model_tag)
        self.text_cleaner = TextCleaner(text_cleaner) if text_cleaner else None

    def tokenize(self, text):
        if self.text_cleaner:
            text = self.text_cleaner(text)
        tokens = self.processor.tokenizer.encode(text, return_tensors="np")
        return tokens.flatten()

    def __call__(self, data):
        example = data

        # preprocessing and calculate new speech_lengths
        # pad to 30 seconds (3000 frames after processing)
        # devide speech_lengths by 160, and build attention_mask
        # convert speech to list of numpy arrays for processor
        # speech = [s.detach().cpu().numpy() for s in speech]  # list of (T,)
        processed = self.processor(
            example['speech'],
            sampling_rate=16000,
            return_tensors="np",
            padding=True,
        )
        speech = np.transpose(np.squeeze(processed.input_features, axis=0), (1, 0))  # (B, D, T') --> (T', D)
        # pad to 30 seconds (3000 frames after processing)
        # speech = torch.nn.functional.pad(speech, (0, max(0, 3000 - speech.size(2))), value=0.0)[:, :, :3000]  # (B, D, 3000)
        # speech_lengths = torch.tensor([min(l // 160, 3000) for l in speech_lengths])  # (B,)

        ret = dict(
            speech=speech,
            text=self.tokenize(example['text']),
            text_ctc=self.tokenize(example['text_ctc']),
            text_prev=self.tokenize(example['text_prev']),
        )
        return ret
