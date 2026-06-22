"""Tests for HFBaselineService — all transformers/torch calls are mocked."""
from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.hf_baseline_service import HFBaselineService

_CFG = {"device": "cpu", "models_dir": "./models", "hf_token": ""}
_SMALL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
_LARGE = "mistralai/Mistral-7B-v0.1"


def _build_mocks(oom_on_to: bool = False, oom_on_generate: bool = False) -> tuple:
    """Return (tf_mock, torch_mock, model_mock, tokenizer_mock)."""
    torch_mock = MagicMock()
    torch_mock.float16 = "float16"
    torch_mock.cuda.empty_cache.return_value = None

    input_ids = MagicMock()
    input_ids.shape = (1, 5)
    input_ids.to.return_value = input_ids

    tokenizer = MagicMock()
    tokenizer.return_value = {"input_ids": input_ids}  # real dict so .items() works
    tokenizer.decode.return_value = "Generated text."

    out = MagicMock()
    out.shape = (1, 8)  # 5 prompt + 3 new tokens

    model = MagicMock()
    if oom_on_to:
        model.to.side_effect = RuntimeError("CUDA out of memory.")
    else:
        model.to.return_value = model
    model.generate.side_effect = RuntimeError("CUDA out of memory.") if oom_on_generate else None
    model.generate.return_value = out

    AutoTokenizer = MagicMock()
    AutoTokenizer.from_pretrained.return_value = tokenizer
    AutoModelForCausalLM = MagicMock()
    AutoModelForCausalLM.from_pretrained.return_value = model

    tf = MagicMock()
    tf.AutoTokenizer = AutoTokenizer
    tf.AutoModelForCausalLM = AutoModelForCausalLM

    return tf, torch_mock, model, tokenizer


@pytest.fixture
def mocks():
    tf, torch_m, model, tokenizer = _build_mocks()
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        yield tf, torch_m, model, tokenizer


@pytest.fixture
def svc() -> HFBaselineService:
    return HFBaselineService(config=_CFG)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_small_model_inference_returns_result(svc, mocks) -> None:
    result = svc.run("Hello", _SMALL, 20)
    assert isinstance(result, BenchmarkResult)
    assert result.method == "hf_baseline"
    assert result.is_success
    assert result.output == "Generated text."


def test_tokens_generated_calculated_correctly(svc, mocks) -> None:
    result = svc.run("Hello", _SMALL, 20)
    assert result.tokens_generated == 3   # out.shape[1] - input_ids.shape[1] = 8 - 5
    assert result.tokens_per_second > 0


def test_metrics_captured_on_success(svc, mocks) -> None:
    result = svc.run("Hello", _SMALL, 20)
    assert result.latency_s > 0
    assert result.ram_peak_mb > 0


def test_cost_estimate_populated(svc, mocks) -> None:
    result = svc.run("Hello", _SMALL, 20)
    assert "kWh" in result.cost_estimate


# ---------------------------------------------------------------------------
# OOM / error paths
# ---------------------------------------------------------------------------

def test_oom_on_model_to_returns_error_not_crash() -> None:
    tf, torch_m, _, _ = _build_mocks(oom_on_to=True)
    svc = HFBaselineService(config=_CFG)
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", _LARGE, 20)
    assert not result.is_success
    assert "memory" in result.error.lower()


def test_oom_on_generate_returns_error_result() -> None:
    tf, torch_m, _, _ = _build_mocks(oom_on_generate=True)
    svc = HFBaselineService(config=_CFG)
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", _LARGE, 20)
    assert not result.is_success


def test_memory_captured_on_oom() -> None:
    tf, torch_m, _, _ = _build_mocks(oom_on_to=True)
    svc = HFBaselineService(config=_CFG)
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", _LARGE, 20)
    assert result.latency_s > 0
    assert result.ram_peak_mb > 0


# ---------------------------------------------------------------------------
# Token security
# ---------------------------------------------------------------------------

def test_token_sanitized_in_error_field() -> None:
    secret = "hf_super_secret_token_abc123"
    tf, torch_m, model, _ = _build_mocks()
    model.to.side_effect = RuntimeError(f"auth failed with token {secret}")
    svc = HFBaselineService(config={**_CFG, "hf_token": secret})
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", "gpt2", 5)
    assert secret not in result.error
    assert result.error != ""


def test_token_not_in_log_output(caplog, svc, mocks) -> None:
    token = "hf_my_private_token_xyz"
    svc._hf_token = token
    with caplog.at_level(logging.DEBUG):
        svc.run("Hello", _SMALL, 5)
    assert token not in caplog.text
