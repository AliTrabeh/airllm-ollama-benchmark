"""Shared pytest fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_setup_json(tmp_path: Path) -> Path:
    """Write a minimal setup.json to a temp dir and return its path."""
    cfg = tmp_path / "setup.json"
    cfg.write_text(
        json.dumps({
            "model_id": "test-small",
            "airllm_model_id": "test-large",
            "ollama_model": "tinyllama",
            "max_new_tokens": 10,
            "device": "cpu",
            "models_dir": str(tmp_path / "models"),
            "results_dir": str(tmp_path / "results"),
        }),
        encoding="utf-8",
    )
    return cfg


@pytest.fixture
def minimal_config() -> dict:
    return {
        "hf_token": "hf_test_token",
        "model_id": "test-small",
        "airllm_model_id": "test-large",
        "ollama_model": "tinyllama",
        "max_new_tokens": 10,
        "device": "cpu",
        "models_dir": "./models",
        "results_dir": "./results",
    }
