"""Load configuration from .env and config/setup.json.

Env vars always override setup.json values.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from airllm_benchmark.shared.constants import (
    DEFAULT_DEVICE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_MODELS_DIR,
    DEFAULT_RESULTS_DIR,
    OLLAMA_BASE_URL,
)

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "setup.json"


def _load_json_config() -> dict:
    if _CONFIG_PATH.exists():
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def load_config() -> dict:
    """Return merged config: setup.json defaults + env overrides."""
    load_dotenv()
    app = _load_json_config()
    return {
        "hf_token": os.getenv("HF_TOKEN", ""),
        "model_id": os.getenv("MODEL_ID") or app.get("model_id", ""),
        "airllm_model_id": os.getenv("AIRLLM_MODEL_ID") or app.get("airllm_model_id", ""),
        "ollama_model": os.getenv("OLLAMA_MODEL") or app.get("ollama_model", ""),
        "max_new_tokens": int(
            os.getenv("MAX_NEW_TOKENS") or app.get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)
        ),
        "device": os.getenv("DEVICE") or app.get("device", DEFAULT_DEVICE),
        "models_dir": os.getenv("MODELS_DIR") or app.get("models_dir", DEFAULT_MODELS_DIR),
        "results_dir": os.getenv("RESULTS_DIR") or app.get("results_dir", DEFAULT_RESULTS_DIR),
        "ollama_url": os.getenv("OLLAMA_URL") or app.get("ollama_url", OLLAMA_BASE_URL),
        "airllm_max_seq_len": int(
            os.getenv("AIRLLM_MAX_SEQ_LEN") or app.get("airllm_max_seq_len", 128)
        ),
    }


def require_hf_token(config: dict) -> str:
    """Return HF_TOKEN or raise a clear ValueError if missing."""
    token = config.get("hf_token", "")
    if not token:
        raise ValueError(
            "HF_TOKEN is required but not set. "
            "Copy .env.example to .env and set HF_TOKEN=your_token_here"
        )
    return token


def get_models_dir(config: dict) -> Path:
    return Path(config.get("models_dir", DEFAULT_MODELS_DIR))


def get_results_dir(config: dict) -> Path:
    return Path(config.get("results_dir", DEFAULT_RESULTS_DIR))
