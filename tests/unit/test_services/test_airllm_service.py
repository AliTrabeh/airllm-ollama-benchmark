"""Tests for AirLLMService — airllm and transformers are mocked."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.airllm_service import AirLLMService

_CFG = {"models_dir": "./models", "hf_token": "", "airllm_max_seq_len": 128}
_MODEL = "mistralai/Mistral-7B-v0.1"


def _build_mocks(fail_on_generate: bool = False) -> tuple:
    """Return (airllm_mock, tf_mock, model_mock, tokenizer_mock)."""
    # output: 8 tokens total (5 prompt + 3 generated)
    out_0 = MagicMock()
    out_0.tolist.return_value = list(range(8))

    out = MagicMock()
    out.__getitem__ = MagicMock(return_value=out_0)

    model = MagicMock()
    if fail_on_generate:
        model.generate.side_effect = RuntimeError("mmap read error")
    else:
        model.generate.return_value = out

    AutoModel = MagicMock()  # noqa: N806
    AutoModel.from_pretrained.return_value = model
    airllm_mock = MagicMock()
    airllm_mock.AutoModel = AutoModel

    input_ids = MagicMock()
    input_ids.shape = (1, 5)

    tokenizer = MagicMock()
    tokenizer.return_value = {"input_ids": input_ids}
    tokenizer.decode.return_value = "AirLLM generated text."

    AutoTokenizer = MagicMock()  # noqa: N806
    AutoTokenizer.from_pretrained.return_value = tokenizer
    tf_mock = MagicMock()
    tf_mock.AutoTokenizer = AutoTokenizer

    return airllm_mock, tf_mock, model, tokenizer


@pytest.fixture
def mocks():
    al, tf, model, tok = _build_mocks()
    torch_m = MagicMock()
    torch_m.cuda.is_available.return_value = False
    with patch.dict(sys.modules, {"airllm": al, "transformers": tf, "torch": torch_m}):
        yield al, tf, model, tok


@pytest.fixture
def svc() -> AirLLMService:
    return AirLLMService(config=_CFG)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_successful_run_returns_benchmark_result(svc, mocks) -> None:
    result = svc.run("Hello", _MODEL, 20)
    assert isinstance(result, BenchmarkResult)
    assert result.method == "airllm"
    assert result.is_success
    assert result.output == "AirLLM generated text."


def test_latency_captured(svc, mocks) -> None:
    result = svc.run("Hello", _MODEL, 20)
    assert result.latency_s > 0


def test_ram_captured(svc, mocks) -> None:
    result = svc.run("Hello", _MODEL, 20)
    assert result.ram_peak_mb > 0


def test_tokens_generated_calculated(svc, mocks) -> None:
    result = svc.run("Hello", _MODEL, 20)
    assert result.tokens_generated == 3   # len(out_0.tolist()) - prompt_len = 8 - 5
    assert result.tokens_per_second > 0


def test_cost_estimate_uses_cpu_tdp(svc, mocks) -> None:
    result = svc.run("Hello", _MODEL, 20)
    assert "kWh" in result.cost_estimate
    assert "65W" in result.cost_estimate  # CPU-only TDP, not 200W GPU


def test_model_path_from_config_not_hardcoded() -> None:
    svc = AirLLMService(config={**_CFG, "models_dir": "/custom/path"})
    assert svc._cache_dir == "/custom/path"


def test_max_seq_len_from_config() -> None:
    svc = AirLLMService(config={**_CFG, "airllm_max_seq_len": 256})
    assert svc._max_seq_len == 256


def test_small_tokens_default_is_safe() -> None:
    """max_new_tokens is passed by caller; default seq_len is small (128)."""
    svc = AirLLMService(config=_CFG)
    assert svc._max_seq_len == 128


def test_generate_called_without_cuda(svc, mocks) -> None:
    """AirLLM runs on CPU — input_ids must NOT have .cuda() called."""
    _, _, model_mock, _ = mocks
    al, tf, model_mock, _ = mocks
    svc.run("Hello", _MODEL, 20)
    call_args = model_mock.generate.call_args
    input_arg = call_args[0][0]   # first positional arg to generate()
    input_arg.cuda.assert_not_called()


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------

def test_file_not_found_returns_error_result() -> None:
    al, tf, model, _ = _build_mocks()
    al.AutoModel.from_pretrained.side_effect = FileNotFoundError("model dir missing")
    torch_m = MagicMock()
    torch_m.cuda.is_available.return_value = False
    svc = AirLLMService(config=_CFG)
    with patch.dict(sys.modules, {"airllm": al, "transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", _MODEL, 20)
    assert not result.is_success
    assert "not found" in result.error.lower()


def test_missing_library_raises_import_error(svc) -> None:
    with patch.dict(sys.modules, {"airllm": None, "transformers": None}), pytest.raises((ImportError, TypeError)):
        svc.run("Hello", _MODEL, 20)
