"""Tests for shared/constants.py."""
from airllm_benchmark.shared.constants import (
    DEFAULT_DEVICE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_MODELS_DIR,
    DEFAULT_RESULTS_DIR,
    OLLAMA_BASE_URL,
    VALID_METHODS,
)


def test_default_max_new_tokens() -> None:
    assert DEFAULT_MAX_NEW_TOKENS == 20


def test_default_device() -> None:
    assert DEFAULT_DEVICE == "cpu"


def test_default_dirs_are_strings() -> None:
    assert isinstance(DEFAULT_MODELS_DIR, str)
    assert isinstance(DEFAULT_RESULTS_DIR, str)


def test_ollama_base_url_format() -> None:
    assert OLLAMA_BASE_URL.startswith("http")
    assert "11434" in OLLAMA_BASE_URL


def test_valid_methods_contains_all() -> None:
    assert "ollama" in VALID_METHODS
    assert "hf_baseline" in VALID_METHODS
    assert "airllm" in VALID_METHODS
    assert "all" in VALID_METHODS
