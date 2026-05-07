"""
Config loading tests. GPU-free. Runs in GitHub Actions CI.

Validates that YAML configs are syntactically valid and contain required keys.
New generated configs under conf/exp_*/ are auto-discovered.
"""
from __future__ import annotations

import glob
from pathlib import Path

import pytest
from omegaconf import OmegaConf

REPO_ROOT = Path(__file__).parent.parent

TEMPLATE_CONFIGS = [
    "conf/owsm_peft_lora_basic.yaml",
    "conf/owsm_peft_espnet.yaml",
    "conf/owsm_peft_adalora.yaml",
    "conf/owsm_peft_randlora.yaml",
    "conf/owsm_peft_vblora.yaml",
    "conf/owsm_peft_delora.yaml",
]

GENERATED_CONFIGS = sorted(
    str(p.relative_to(REPO_ROOT))
    for p in REPO_ROOT.glob("conf/exp_*/*.yaml")
    if "generated" not in p.parts
)

ALL_CONFIGS = TEMPLATE_CONFIGS + GENERATED_CONFIGS


@pytest.mark.parametrize("config_path", ALL_CONFIGS)
def test_config_loads(config_path):
    path = REPO_ROOT / config_path
    assert path.exists(), f"Config file not found: {path}"
    cfg = OmegaConf.load(path)
    assert cfg is not None


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_generated_config_has_lr(config_path):
    path = REPO_ROOT / config_path
    cfg = OmegaConf.to_container(OmegaConf.load(path), resolve=False)
    assert "lr" in cfg, f"Missing 'lr' in {config_path}"


@pytest.mark.parametrize("config_path", GENERATED_CONFIGS)
def test_generated_config_has_peft(config_path):
    path = REPO_ROOT / config_path
    cfg = OmegaConf.to_container(OmegaConf.load(path), resolve=False)
    assert "peft" in cfg, f"Missing 'peft' section in {config_path}"
    assert "type" in cfg["peft"], f"Missing 'peft.type' in {config_path}"
