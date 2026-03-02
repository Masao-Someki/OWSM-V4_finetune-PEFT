import numpy as np
from datasets import Audio, concatenate_datasets, load_dataset, load_from_disk
from torch.utils.data import Dataset

from espnet2.bin.s2t_inference import Speech2Text
from espnet2.text.cleaner import TextCleaner

class EuroSpeechPortugalDataset(Dataset):
    def __init__(self, data_dir, split, ratio=1.0):
        if not (0 < ratio <= 1.0):
            raise ValueError("ratio must be in the range (0, 1].")

        dataset_dict = load_from_disk(data_dir)
        if split in dataset_dict:
            self.dataset = dataset_dict[split]
        else:
            raise ValueError(f"Split '{split}' not found in dataset.")

        self.dataset = self.dataset.cast_column("audio", Audio())
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
            # "text_raw": transcript,
        }
        return example

class FleursPortugalDataset(Dataset):
    def __init__(self, data_dir, split, ratio=1.0):
        if not (0 < ratio <= 1.0):
            raise ValueError("ratio must be in the range (0, 1].")

        dataset_dict = load_from_disk(data_dir)
        if split in dataset_dict:
            self.dataset = dataset_dict[split]
        else:
            raise ValueError(f"Split '{split}' not found in dataset.")

        self.dataset = self.dataset.cast_column("audio", Audio())
        if ratio < 1.0:
            keep = int(len(self.dataset) * ratio)
            self.dataset = self.dataset.select(range(keep))

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        transcript = str(item["transcription"]).strip()
        example = {
            "speech": item["audio"]["array"].astype(np.float32),
            "text": f"<por><asr><notimestamps> {transcript}",
            "text_ctc": transcript,
            "text_prev": "<na>",
            # "text_raw": transcript,
        }
        return example
# src/data/dataset.py
        
class FalarPortugalDataset(Dataset):
    def __init__(self, data_dir, split, ratio=1.0):
        if not (0 < ratio <= 1.0):
            raise ValueError("ratio must be in the range (0, 1].")

        cache_dir = str(data_dir) if data_dir else None

        if split == "train":
            train_splits = [
                load_dataset(
                    "inesc-id/FalAR",
                    split=f"train_{i}",
                    cache_dir=cache_dir,
                    trust_remote_code=True,
                )
                for i in range(16)
            ]
            self.dataset = concatenate_datasets(train_splits)
        else:
            hf_split = "dev" if split == "validation" else split
            self.dataset = load_dataset(
                "inesc-id/FalAR",
                split=hf_split,
                cache_dir=cache_dir,
                trust_remote_code=True,
            )

        self.dataset = self.dataset.cast_column("audio", Audio())
        if ratio < 1.0:
            keep = int(len(self.dataset) * ratio)
            self.dataset = self.dataset.select(range(keep))

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        transcript = str(item["transcription"]).strip()

        example = {
            "speech": item["wav"]["array"].astype(np.float32),
            "text": f"<por><asr><notimestamps> {transcript}",
            "text_ctc": transcript,
            "text_prev": "<na>",
        }
        return example

class FalarPortugalWhisperDataset(FalarPortugalDataset):
    def __init__(self, split, model_tag, data_dir=None ratio=1.0, text_cleaner=None):
        super().__init__(data_dir=data_dir, split=split, ratio=ratio)
        self.transform = WhisperTokenizeTransform(model_tag=model_tag, text_cleaner=text_cleaner)

    def __getitem__(self, idx):
        ex = super().__getitem__(idx)   # {"speech": waveform, "text": "...", ...}
        return self.transform(ex)       # {"speech": (T,80), "speech_lengths": T, "text": ids, ...}

class OWSMTokenizeTransform:
    def __init__(self, model_tag, text_cleaner=None, *args, **kwargs):
        owsm_model = Speech2Text.from_pretrained(model_tag)
        self.tokenizer = owsm_model.tokenizer
        self.converter = owsm_model.converter
        self.text_cleaner = TextCleaner(text_cleaner) if text_cleaner else None


    def tokenize(self, text):
        if self.text_cleaner:
            text = self.text_cleaner(text)
        return np.array(self.converter.tokens2ids(self.tokenizer.text2tokens(text)))

    def __call__(self, data):
        example = data
        ret = dict(
            speech=example['speech'],
            text=self.tokenize(example['text']),
            text_ctc=self.tokenize(example['text_ctc']),
            text_prev=self.tokenize(example['text_prev']),
        )
        return ret

# class WhisperTokenizeTransform:
#     def __init__(self, model_tag, text_cleaner=None, *args, **kwargs):
#         from transformers import WhisperProcessor
#         self.processor = WhisperProcessor.from_pretrained(model_tag)
#         self.text_cleaner = TextCleaner(text_cleaner) if text_cleaner else None

#     def tokenize(self, text):
#         if self.text_cleaner:
#             text = self.text_cleaner(text)
#         tokens = self.processor.tokenizer.encode(text, return_tensors="np")
#         return tokens.flatten()

#     def __call__(self, data):
#         example = data

#         # preprocessing and calculate new speech_lengths
#         # pad to 30 seconds (3000 frames after processing)
#         # devide speech_lengths by 160, and build attention_mask
#         # convert speech to list of numpy arrays for processor
#         # speech = [s.detach().cpu().numpy() for s in speech]  # list of (T,)
#         processed = self.processor(
#             example['speech'],
#             sampling_rate=16000,
#             return_tensors="np",
#             padding=True,
#         )
#         speech = np.transpose(np.squeeze(processed.input_features, axis=0), (1, 0))  # (B, D, T') --> (T', D)
#         # pad to 30 seconds (3000 frames after processing)
#         # speech = torch.nn.functional.pad(speech, (0, max(0, 3000 - speech.size(2))), value=0.0)[:, :, :3000]  # (B, D, 3000)
#         # speech_lengths = torch.tensor([min(l // 160, 3000) for l in speech_lengths])  # (B,)

#         ret = dict(
#             speech=speech,
#             text=self.tokenize(example['text']),
#             text_ctc=self.tokenize(example['text_ctc']),
#             text_prev=self.tokenize(example['text_prev']),
#         )
#         return ret

# add dahee
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
            padding=False,
        )
        feat = processed.input_features[0]   # (80, T')
        T = feat.shape[1]
        speech = feat.T                      # (T', 80)  

        # pad to 30 seconds (3000 frames after processing)
        # speech = torch.nn.functional.pad(speech, (0, max(0, 3000 - speech.size(2))), value=0.0)[:, :, :3000]  # (B, D, 3000)
        # speech_lengths = torch.tensor([min(l // 160, 3000) for l in speech_lengths])  # (B,)
 
        ret = dict(
            speech=speech.astype(np.float32),
            speech_lengths=np.array(T, dtype=np.int64),
            text=self.tokenize(example["text"]),
            text_ctc=self.tokenize(example["text_ctc"]),
            text_prev=self.tokenize(example["text_prev"]),
        )
        return ret
