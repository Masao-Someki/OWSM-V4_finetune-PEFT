"""
Search space validation tests. GPU-free. Runs in GitHub Actions CI.

Ensures Claudeが生成したconfigの値が prompts/search_space.md の許容範囲内であること。
search_space.md を更新したら ALLOWED_* 定数も合わせて更新すること。
"""
from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import pytest
from omegaconf import OmegaConf

REPO_ROOT = Path(__file__).parent.parent

# --- 許容値 (prompts/search_space.md と同期させること) ---
ALLOWED_LRS = {1e-5, 3e-5, 5e-5, 1e-4, 2e-4}
ALLOWED_MAX_EPOCHS = {1, 2, 3, 4, 6}
ALLOWED_PEFT_TYPES = {"lora", "espnet_lora", "adalora", "randlora", "vblora", "delora"}
ALLOWED_WARMUP_STEPS = {1000, 3000, 6000, 10000}

LORA_ALLOWED_R = {8, 16, 32}
LORA_ALLOWED_ALPHA = {8, 16, 32}
ADALORA_ALLOWED_INIT_R = {8, 12, 16}
ADALORA_ALLOWED_TARGET_R = {4, 8, 12}
RANDLORA_ALLOWED_R = {16, 32, 64}
VBLORA_ALLOWED_R = {2, 4, 8}
VBLORA_ALLOWED_TOPK = {1, 2, 4}

GENERATED_CONFIGS = sorted(
    str(p.relative_to(REPO_ROOT))
    for p in REPO_ROOT.glob("conf/exp_*/*.yaml")
    if "generated" not in p.parts
)


def _get(d: Any, dotted: str, default: Any = None) -> Any:
    cur = d
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _load(config_path: str) -> dict:
    return OmegaConf.to_container(OmegaConf.load(REPO_ROOT / config_path), resolve=False)


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_lr_in_search_space(config_path):
    lr = _get(_load(config_path), "lr")
    if lr is None:
        pytest.skip("lr not set (inherits from default)")
    assert float(lr) in ALLOWED_LRS, f"{config_path}: lr={lr} not in {ALLOWED_LRS}"


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_peft_type_in_search_space(config_path):
    peft_type = _get(_load(config_path), "peft.type")
    if peft_type is None:
        pytest.skip("peft.type not set")
    assert peft_type in ALLOWED_PEFT_TYPES, (
        f"{config_path}: peft.type={peft_type!r} not in {ALLOWED_PEFT_TYPES}"
    )


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_max_epochs_in_search_space(config_path):
    max_epochs = _get(_load(config_path), "trainer.max_epochs")
    if max_epochs is None:
        pytest.skip("trainer.max_epochs not set")
    assert int(max_epochs) in ALLOWED_MAX_EPOCHS, (
        f"{config_path}: trainer.max_epochs={max_epochs} not in {ALLOWED_MAX_EPOCHS}"
    )


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_warmup_steps_in_search_space(config_path):
    steps = _get(_load(config_path), "scheduler.warmup_steps")
    if steps is None:
        pytest.skip("scheduler.warmup_steps not set")
    assert int(steps) in ALLOWED_WARMUP_STEPS, (
        f"{config_path}: warmup_steps={steps} not in {ALLOWED_WARMUP_STEPS}"
    )


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_lora_r_in_search_space(config_path):
    cfg = _load(config_path)
    peft_type = _get(cfg, "peft.type")
    if peft_type != "lora":
        pytest.skip("not lora")
    r = _get(cfg, "peft.r")
    if r is None:
        pytest.skip("peft.r not set")
    assert int(r) in LORA_ALLOWED_R, f"{config_path}: peft.r={r} not in {LORA_ALLOWED_R}"


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_adalora_r_constraint(config_path):
    cfg = _load(config_path)
    peft_type = _get(cfg, "peft.type")
    if peft_type != "adalora":
        pytest.skip("not adalora")
    init_r = _get(cfg, "peft.init_r")
    target_r = _get(cfg, "peft.target_r")
    if init_r is not None:
        assert int(init_r) in ADALORA_ALLOWED_INIT_R, (
            f"{config_path}: peft.init_r={init_r} not in {ADALORA_ALLOWED_INIT_R}"
        )
    if target_r is not None:
        assert int(target_r) in ADALORA_ALLOWED_TARGET_R, (
            f"{config_path}: peft.target_r={target_r} not in {ADALORA_ALLOWED_TARGET_R}"
        )
    if init_r is not None and target_r is not None:
        assert int(target_r) <= int(init_r), (
            f"{config_path}: target_r={target_r} must be <= init_r={init_r}"
        )


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_array_txt_references_config(config_path):
    """対応するarray_conf/{exp_name}/array.txt がこのconfigを参照していること。"""
    path = Path(config_path)
    exp_name = path.parent.name  # conf/{exp_name}/config.yaml → {exp_name}
    array_txt = REPO_ROOT / ".autoresearch" / "array_conf" / exp_name / "array.txt"
    if not array_txt.exists():
        pytest.skip(f"array.txt not found: {array_txt}")
    lines = [l.strip() for l in array_txt.read_text().splitlines()
             if l.strip() and not l.strip().startswith("#")]
    assert config_path in lines, (
        f"{config_path} not listed in {array_txt}\nListed: {lines}"
    )
