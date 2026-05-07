import logging
import numpy as np
import os
import hashlib
import json
import io
import soundfile as sf
from datasets import Audio, concatenate_datasets, get_dataset_config_names, load_dataset, load_from_disk
from pathlib import Path
from torch.utils.data import Dataset

from espnet2.bin.s2t_inference import Speech2Text
from espnet2.text.cleaner import TextCleaner

logger = logging.getLogger(__name__)
# Avoid noisy Hugging Face transport logs at INFO.
logging.getLogger("httpx").setLevel(logging.WARNING)


ISO6391_TO_3 = {
    "aa": "aar", "ab": "abk", "ae": "ave", "af": "afr", "ak": "aka", "am": "amh",
    "an": "arg", "ar": "ara", "as": "asm", "av": "ava", "ay": "aym", "az": "aze",
    "ba": "bak", "be": "bel", "bg": "bul", "bh": "bih", "bi": "bis", "bm": "bam",
    "bn": "ben", "bo": "bod", "br": "bre", "bs": "bos", "ca": "cat", "ce": "che",
    "ch": "cha", "co": "cos", "cr": "cre", "cs": "ces", "cu": "chu", "cv": "chv",
    "cy": "cym", "da": "dan", "de": "deu", "dv": "div", "dz": "dzo", "ee": "ewe",
    "el": "ell", "en": "eng", "eo": "epo", "es": "spa", "et": "est", "eu": "eus",
    "fa": "fas", "ff": "ful", "fi": "fin", "fj": "fij", "fo": "fao", "fr": "fra",
    "fy": "fry", "ga": "gle", "gd": "gla", "gl": "glg", "gn": "grn", "gu": "guj",
    "gv": "glv", "ha": "hau", "he": "heb", "hi": "hin", "ho": "hmo", "hr": "hrv",
    "ht": "hat", "hu": "hun", "hy": "hye", "hz": "her", "ia": "ina", "id": "ind",
    "ie": "ile", "ig": "ibo", "ii": "iii", "ik": "ipk", "io": "ido", "is": "isl",
    "it": "ita", "iu": "iku", "ja": "jpn", "jv": "jav", "ka": "kat", "kg": "kon",
    "ki": "kik", "kj": "kua", "kk": "kaz", "kl": "kal", "km": "khm", "kn": "kan",
    "ko": "kor", "kr": "kau", "ks": "kas", "ku": "kur", "kv": "kom", "kw": "cor",
    "ky": "kir", "la": "lat", "lb": "ltz", "lg": "lug", "li": "lim", "ln": "lin",
    "lo": "lao", "lt": "lit", "lu": "lub", "lv": "lav", "mg": "mlg", "mh": "mah",
    "mi": "mri", "mk": "mkd", "ml": "mal", "mn": "mon", "mr": "mar", "ms": "msa",
    "mt": "mlt", "my": "mya", "na": "nau", "nb": "nob", "nd": "nde", "ne": "nep",
    "ng": "ndo", "nl": "nld", "nn": "nno", "no": "nor", "nr": "nbl", "nv": "nav",
    "ny": "nya", "oc": "oci", "oj": "oji", "om": "orm", "or": "ori", "os": "oss",
    "pa": "pan", "pi": "pli", "pl": "pol", "ps": "pus", "pt": "por", "qu": "que",
    "rm": "roh", "rn": "run", "ro": "ron", "ru": "rus", "rw": "kin", "sa": "san",
    "sc": "srd", "sd": "snd", "se": "sme", "sg": "sag", "si": "sin", "sk": "slk",
    "sl": "slv", "sm": "smo", "sn": "sna", "so": "som", "sq": "sqi", "sr": "srp",
    "ss": "ssw", "st": "sot", "su": "sun", "sv": "swe", "sw": "swa", "ta": "tam",
    "te": "tel", "tg": "tgk", "th": "tha", "ti": "tir", "tk": "tuk", "tl": "tgl",
    "tn": "tsn", "to": "ton", "tr": "tur", "ts": "tso", "tt": "tat", "tw": "twi",
    "ty": "tah", "ug": "uig", "uk": "ukr", "ur": "urd", "uz": "uzb", "ve": "ven",
    "vi": "vie", "vo": "vol", "wa": "wln", "wo": "wol", "xh": "xho", "yi": "yid",
    "yo": "yor", "za": "zha", "zh": "zho", "zu": "zul",
}


class FleursDataset(Dataset):
    def __init__(
        self,
        split,
        hf_repo="google/fleurs",
        hf_subset="en_us",
        hf_subsets=None,
        data_dir=None,
        ratio=1.0,
        max_samples_per_subset=None,
        lang_sym="<eng>",
        lang_sym_mode="fixed",
        lang_sym_overrides=None,
        text_field="transcription",
        audio_field="audio",
        shuffle=True,
        seed=2024,
        return_lang_sym=False,
        trust_remote_code=True,
        cache_dir=None,
        use_cache=True,
    ):
        if not (0 < ratio <= 1.0):
            raise ValueError("ratio must be in the range (0, 1].")
        if max_samples_per_subset is not None:
            max_samples_per_subset = int(max_samples_per_subset)
            if max_samples_per_subset <= 0:
                raise ValueError("max_samples_per_subset must be > 0 when provided.")

        subsets = self._resolve_subsets(
            hf_repo=hf_repo,
            hf_subset=hf_subset,
            hf_subsets=hf_subsets,
            trust_remote_code=True,
        )
        lang_sym_overrides = lang_sym_overrides or {}

        dataset = None
        cache_path = self._build_cache_path(
            cache_dir=cache_dir,
            use_cache=use_cache,
            split=split,
            hf_repo=hf_repo,
            subsets=subsets,
            ratio=ratio,
            max_samples_per_subset=max_samples_per_subset,
            audio_field=audio_field,
            lang_sym_overrides=lang_sym_overrides,
            shuffle=shuffle,
            seed=seed,
            trust_remote_code=trust_remote_code,
        )
        if cache_path is not None and cache_path.exists():
            logger.info("Loading cached FLEURS dataset from %s", cache_path)
            dataset = load_from_disk(str(cache_path))
            dataset = dataset.cast_column(audio_field, Audio(decode=False))
        else:
            shards = []
            for subset in subsets:
                shard = self._load_single_subset(
                    split=split,
                    hf_repo=hf_repo,
                    subset=subset,
                    data_dir=data_dir,
                    audio_field=audio_field,
                    max_samples_per_subset=max_samples_per_subset,
                    trust_remote_code=trust_remote_code,
                )

                if ratio < 1.0:
                    keep = int(len(shard) * ratio)
                    shard = shard.select(range(keep))
                if max_samples_per_subset is not None and len(shard) > max_samples_per_subset:
                    shard = shard.select(range(max_samples_per_subset))

                shard = shard.add_column("_subset", [subset] * len(shard))
                shard_lang_sym = self._subset_to_lang_sym(subset, overrides=lang_sym_overrides)
                shard = shard.add_column("_lang_sym", [shard_lang_sym] * len(shard))
                shards.append(shard)

            if not shards:
                raise ValueError("No FLEURS subsets were loaded.")

            if len(shards) == 1:
                dataset = shards[0]
            else:
                dataset = concatenate_datasets(shards)
                if shuffle:
                    dataset = dataset.shuffle(seed=seed)

            if cache_path is not None:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info("Saving FLEURS dataset cache to %s", cache_path)
                dataset.save_to_disk(str(cache_path))

        self.dataset = dataset
        self.lang_sym = lang_sym
        self.lang_sym_mode = lang_sym_mode
        self.text_field = text_field
        self.audio_field = audio_field
        self.return_lang_sym = bool(return_lang_sym)
        self.trust_remote_code = bool(trust_remote_code)

    @staticmethod
    def _resolve_subsets(hf_repo, hf_subset, hf_subsets, trust_remote_code):
        if hf_subsets is None:
            return [hf_subset]

        if isinstance(hf_subsets, str):
            if hf_subsets == "all":
                configs = sorted(get_dataset_config_names(hf_repo, trust_remote_code=trust_remote_code))
                # FLEURS may expose meta configs like "all"/"default"; skip them.
                return [c for c in configs if c not in {"all", "default"}]
            return [hf_subsets]

        if isinstance(hf_subsets, list):
            return [c for c in hf_subsets if c not in {"all", "default"}]

        raise TypeError("hf_subsets must be None, a string, or a list of strings.")

    @staticmethod
    def _build_cache_path(
        *,
        cache_dir,
        use_cache,
        split,
        hf_repo,
        subsets,
        ratio,
        max_samples_per_subset,
        audio_field,
        lang_sym_overrides,
        shuffle,
        seed,
        trust_remote_code,
    ):
        if not use_cache or not cache_dir:
            return None
        key_obj = {
            "split": split,
            "hf_repo": hf_repo,
            "subsets": list(subsets),
            "ratio": ratio,
            "max_samples_per_subset": max_samples_per_subset,
            "audio_field": audio_field,
            "lang_sym_overrides": lang_sym_overrides,
            "shuffle": bool(shuffle),
            "seed": int(seed),
            "trust_remote_code": bool(trust_remote_code),
        }
        key = hashlib.sha1(json.dumps(key_obj, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        return Path(cache_dir) / f"fleurs_{key}"

    @staticmethod
    def _load_single_subset(
        split,
        hf_repo,
        subset,
        data_dir,
        audio_field,
        max_samples_per_subset,
        trust_remote_code,
    ):
        if data_dir:
            loaded = load_from_disk(data_dir)
            key = f"{subset}:{split}"
            if key in loaded:
                dataset = loaded[key]
            elif split in loaded:
                dataset = loaded[split]
            else:
                raise ValueError(f"Split '{split}' not found in dataset at {data_dir}.")
        else:
            load_split = split
            if max_samples_per_subset is not None:
                # In quick/debug runs, avoid loading full subset then selecting.
                # HF split slicing fetches only the required head samples.
                load_split = f"{split}[:{max_samples_per_subset}]"
            logger.info(
                "Loading FLEURS subset=%s split=%s (requested=%s)",
                subset,
                load_split,
                split,
            )
            dataset = load_dataset(
                hf_repo,
                subset,
                split=load_split,
                trust_remote_code=trust_remote_code,
            )

        return dataset.cast_column(audio_field, Audio(decode=False))

    @staticmethod
    def _subset_to_lang_sym(subset, overrides):
        if subset in overrides:
            return overrides[subset]

        code = str(subset).split("_")[0].lower()
        if len(code) == 2:
            code = ISO6391_TO_3.get(code, code)
        return f"<{code}>"

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        transcript = str(item[self.text_field]).strip()

        if self.lang_sym_mode == "fixed":
            lang_prefix = self.lang_sym
        else:
            lang_prefix = item.get("_lang_sym", self.lang_sym)

        audio_info = item[self.audio_field]
        if not isinstance(audio_info, dict):
            raise ValueError(f"Unexpected audio payload type in '{self.audio_field}': {type(audio_info)}")

        audio_path = audio_info.get("path")
        audio_bytes = audio_info.get("bytes")
        if audio_path and os.path.exists(audio_path):
            speech, _ = sf.read(audio_path, dtype="float32", always_2d=False)
        elif audio_bytes is not None:
            speech, _ = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
        else:
            raise ValueError(f"Audio source is unavailable in field '{self.audio_field}'")

        if speech.ndim == 2:
            speech = speech.mean(axis=1)

        sample = {
            "speech": speech.astype(np.float32),
            "text": f"{lang_prefix}<asr><notimestamps> {transcript}",
            "text_ctc": transcript,
            "text_prev": "<na>",
        }
        if self.return_lang_sym:
            sample["lang_sym"] = lang_prefix
            sample["subset"] = str(item.get("_subset", ""))
        return sample


class OWSMTokenizeTransform:
    def __init__(self, model_tag, text_cleaner=None, *args, **kwargs):
        cache_dir = os.getenv("ESPNET_MODEL_ZOO_CACHE", ".cache/espnet_model_zoo")
        try:
            from espnet_model_zoo.downloader import ModelDownloader
            downloader = ModelDownloader(cachedir=cache_dir)
            model_kwargs = downloader.download_and_unpack(model_tag)
            owsm_model = Speech2Text(**model_kwargs)
        except Exception:
            owsm_model = Speech2Text.from_pretrained(model_tag)
        self.tokenizer = owsm_model.tokenizer
        self.converter = owsm_model.converter
        self.text_cleaner = TextCleaner(text_cleaner) if text_cleaner else None

    def tokenize(self, text):
        if self.text_cleaner:
            text = self.text_cleaner(text)
        return np.array(self.converter.tokens2ids(self.tokenizer.text2tokens(text)))

    def __call__(self, data):
        return {
            "speech": data["speech"],
            "text": self.tokenize(data["text"]),
            "text_ctc": self.tokenize(data["text_ctc"]),
            "text_prev": self.tokenize(data["text_prev"]),
        }
