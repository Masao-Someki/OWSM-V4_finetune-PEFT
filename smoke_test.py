import os
import sys
import torch
from torch.utils.data import DataLoader

from espnet2.train.collate_fn import CommonCollateFn
from src.peft_model import OWSMFinetune
from src.data.dataset_test import FalarPortugalDataset, EuroSpeechPortugalDataset


def _print_batch(batch, title: str):
    print("\n" + "=" * 80)
    print(title)
    print("BATCH KEYS:", list(batch.keys()))
    for k, v in batch.items():
        if hasattr(v, "shape"):
            try:
                dtype = v.dtype
            except Exception:
                dtype = type(v)
            print(f"  {k:16s} shape={tuple(v.shape)} dtype={dtype}")
        else:
            if isinstance(v, list):
                preview = v[0] if len(v) else None
                if isinstance(preview, str):
                    preview = preview[:80]
                print(f"  {k:16s} list(len={len(v)}) first={preview}")
            else:
                print(f"  {k:16s} type={type(v)} value={v}")


def _assert_required_keys(batch, where: str):
    required = [
        "speech",
        "speech_lengths",
        "text",
        "text_lengths",
        "text_ctc",
        "text_ctc_lengths",
        "text_prev",
        "text_prev_lengths",
    ]
    missing = [k for k in required if k not in batch]
    if missing:
        raise KeyError(
            f"[{where}] Missing keys in batch: {missing}\n"
            f"Available keys: {list(batch.keys())}\n"
            "=> dataset/collate output does not match OWSMFinetune.forward signature.\n"
        )


@torch.no_grad()
def _forward_once(model: OWSMFinetune, batch, where: str):
    _assert_required_keys(batch, where)
    model.train()
    out = model(
        batch["speech"],
        batch["speech_lengths"],
        batch["text"],
        batch["text_lengths"],
        batch["text_ctc"],
        batch["text_ctc_lengths"],
        batch["text_prev"],
        batch["text_prev_lengths"],
    )
    print(f"[{where}] FORWARD OK. output type={type(out)}")
    return out


def _make_one_batch(ds, batch_size: int = 1):
    collate = CommonCollateFn(int_pad_value=-1)
    loader = DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate,
        num_workers=0,
        pin_memory=False,
    )
    return next(iter(loader))


def main():
    # Make caches explicit (you already exported these, but keep it robust)
    os.environ.setdefault("HF_HOME", "/work/nvme/bbjs/dyang10/hf_cache")
    os.environ.setdefault("HF_DATASETS_CACHE", "/work/nvme/bbjs/dyang10/hf_cache/datasets")
    os.environ.setdefault("TRANSFORMERS_CACHE", "/work/nvme/bbjs/dyang10/hf_cache/transformers")
    os.environ.setdefault("TMPDIR", "/tmp")

    # Load model once
    print("Loading OWSM model (first time may take a bit)...")
    model = OWSMFinetune(model_tag="espnet/owsm_v4_medium_1B", peft=None)

    # 1) FalAR
    falar_cache = "/work/nvme/bbjs/clin10/eurospeech_finetune/espnet/egs3/eurospeech_portugal/s2t1/hub"
    print("\n[FalAR] Building dataset...")
    # ds_falar = FalarPortugalDataset(data_dir=falar_cache, split="validation", ratio=0.0001)
    ds_falar = FalarPortugalDataset(data_dir=falar_cache, split="validation", smoke=True, n_samples=1)
    print(f"[FalAR] dataset length: {len(ds_falar)}")

    batch_falar = _make_one_batch(ds_falar, batch_size=1)
    _print_batch(batch_falar, "FalAR: 1-batch preview")
    _forward_once(model, batch_falar, "FalAR")

    # 2) EuroSpeech
    euro_root = "/work/nvme/bbjs/dyang10/datasets/eurospeech_portugal"
    print("\n[EuroSpeech] Building dataset...")
    # ds_euro = EuroSpeechPortugalDataset(data_dir=euro_root, split="validation", ratio=0.0001)
    ds_euro = EuroSpeechPortugalDataset(data_dir=euro_root, split="validation", n_samples=1)
    print(f"[EuroSpeech] dataset length: {len(ds_euro)}")

    batch_euro = _make_one_batch(ds_euro, batch_size=1)
    _print_batch(batch_euro, "EuroSpeech: 1-batch preview")
    _forward_once(model, batch_euro, "EuroSpeech")

    print("\n✅ ALL SMOKE TESTS PASSED (FalAR + EuroSpeech)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\n❌ SMOKE TEST FAILED:", repr(e), file=sys.stderr)
        raise

# import os
# import torch
# from torch.utils.data import DataLoader

# from src.data.dataset import FalarPortugalDataset, EuroSpeechPortugalDataset
# from espnet2.train.collate_fn import CommonCollateFn
# from src.peft_model import OWSMFinetune

# def main():
#     # (선택) 캐시 위치 고정: 이미 너는 HF_HOME은 잡혀있지만, 혹시 모를 상황 대비
#     os.environ.setdefault("HF_HOME", "/work/nvme/bbjs/dyang10/hf_cache")
#     os.environ.setdefault("HF_DATASETS_CACHE", "/work/nvme/bbjs/dyang10/hf_cache/datasets")

#     # 1) dataset: validation + tiny ratio 로 "다운로드/전처리 최소"로
#     falar_cache = "/work/nvme/bbjs/clin10/eurospeech_finetune/espnet/egs3/eurospeech_portugal/s2t1/hub"
#     ds = FalarPortugalDataset(data_dir=falar_cache, split="validation", ratio=0.0001)

#     # 2) collate: 네 default.yaml에 있는 그대로
#     collate = CommonCollateFn(int_pad_value=-1)

#     # 3) dataloader: 1 batch만
#     loader = DataLoader(ds, batch_size=1, shuffle=False, collate_fn=collate, num_workers=0)

#     batch = next(iter(loader))
#     print("BATCH KEYS:", batch.keys())
#     for k, v in batch.items():
#         if hasattr(v, "shape"):
#             print(k, v.shape, v.dtype)
#         else:
#             print(k, type(v), (v[:1] if isinstance(v, list) else ""))

#     # 4) model + forward 1번 (여기서 네 “입력 키/shape mismatch”가 바로 잡힘)
#     model = OWSMFinetune(model_tag="espnet/owsm_v4_medium_1B", peft=None)
#     model.train()

#     with torch.no_grad():
#         out = model(
#             batch["speech"],
#             batch["speech_lengths"],
#             batch["text"],
#             batch["text_lengths"],
#             batch["text_ctc"],
#             batch["text_ctc_lengths"],
#             batch["text_prev"],
#             batch["text_prev_lengths"],
#         )
#     print("FORWARD OK:", type(out))

# if __name__ == "__main__":
#     main()