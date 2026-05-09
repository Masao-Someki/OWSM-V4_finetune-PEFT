from __future__ import annotations

from pathlib import Path

from src.data.dataset import FleursDataset


class Dataset(FleursDataset):
    """ESPnet3 dataset module entrypoint.

    DataOrganizer (latest espnet3) resolves dataset references via
    `dataset.Dataset(**data_src_args)`.
    """

    def __init__(self, split: str, cache_dir: str | None = None, **kwargs):
        repo_root = Path(__file__).resolve().parent.parent
        split_key = "validation" if split == "valid" else split
        if cache_dir is None:
            if split_key == "test":
                cache_dir = str(repo_root / "cache" / "fleurs_hf_test")
            else:
                cache_dir = str(repo_root / "cache" / "fleurs")

        super().__init__(split=split_key, cache_dir=cache_dir, **kwargs)

