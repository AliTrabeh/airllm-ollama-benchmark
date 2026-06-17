"""Tests for shared/config.py."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from airllm_benchmark.shared.config import (
    get_models_dir,
    get_results_dir,
    load_config,
    require_hf_token,
)
from airllm_benchmark.shared.constants import DEFAULT_DEVICE, DEFAULT_MAX_NEW_TOKENS


def test_load_config_defaults(tmp_path: Path) -> None:
    nonexistent = tmp_path / "no_setup.json"
    with patch("airllm_benchmark.shared.config._CONFIG_PATH", nonexistent):
        with patch.dict(os.environ, {"HF_TOKEN": "", "MODEL_ID": "", "DEVICE": "",
                                      "MAX_NEW_TOKENS": str(DEFAULT_MAX_NEW_TOKENS),
                                      "AIRLLM_MODEL_ID": "", "OLLAMA_MODEL": "",
                                      "MODELS_DIR": "", "RESULTS_DIR": ""}):
            config = load_config()
    assert config["device"] == DEFAULT_DEVICE
    assert config["max_new_tokens"] == DEFAULT_MAX_NEW_TOKENS


def test_load_config_reads_json(tmp_path: Path) -> None:
    setup = tmp_path / "setup.json"
    setup.write_text(json.dumps({"model_id": "json-model", "device": "cuda"}), encoding="utf-8")
    with patch("airllm_benchmark.shared.config._CONFIG_PATH", setup):
        with patch.dict(os.environ, {"MODEL_ID": "", "DEVICE": ""}):
            config = load_config()
    assert config["model_id"] == "json-model"
    assert config["device"] == "cuda"


def test_env_overrides_json(tmp_path: Path) -> None:
    setup = tmp_path / "setup.json"
    setup.write_text(json.dumps({"model_id": "json-model"}), encoding="utf-8")
    with patch("airllm_benchmark.shared.config._CONFIG_PATH", setup):
        with patch.dict(os.environ, {"MODEL_ID": "env-model"}):
            config = load_config()
    assert config["model_id"] == "env-model"


def test_require_hf_token_success() -> None:
    assert require_hf_token({"hf_token": "hf_abc"}) == "hf_abc"


def test_require_hf_token_empty_raises() -> None:
    with pytest.raises(ValueError, match="HF_TOKEN is required"):
        require_hf_token({"hf_token": ""})


def test_require_hf_token_missing_key_raises() -> None:
    with pytest.raises(ValueError, match="HF_TOKEN is required"):
        require_hf_token({})


def test_get_models_dir_returns_path() -> None:
    cfg = {"models_dir": "./custom_models"}
    assert get_models_dir(cfg) == Path("./custom_models")


def test_get_results_dir_returns_path() -> None:
    cfg = {"results_dir": "./custom_results"}
    assert get_results_dir(cfg) == Path("./custom_results")
