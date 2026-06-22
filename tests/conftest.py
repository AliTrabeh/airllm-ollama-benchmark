"""Shared pytest fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

# Pre-import torch so it lands in sys.modules before any test uses patch.dict to
# mock it.  unittest.mock._patch_dict._unpatch_dict calls _clear_dict(sys.modules)
# on teardown, which wipes every entry and only restores keys that were present
# in the snapshot captured at patch entry.  If torch wasn't imported yet when
# the first patch.dict runs, it won't be in that snapshot; subsequent plain
# `import torch` calls then re-execute torch/__init__.py against an already-
# loaded C extension, raising "ValueError: module functions cannot set
# METH_CLASS or METH_STATIC".
try:
    import torch as _torch  # noqa: F401
    _torch.cuda.is_available()  # ensure torch.cuda submodule is registered too
    del _torch
except Exception:
    pass


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
