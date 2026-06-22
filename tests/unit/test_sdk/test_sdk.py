"""Tests for BenchmarkSDK."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.shared.gatekeeper import ApiGatekeeper


def _result(method: str = "ollama", model: str = "test") -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id=model, prompt="hi",
        latency_s=0.1, ram_peak_mb=100.0,
        tokens_generated=5, tokens_per_second=50.0,
        output="hello",
    )


@pytest.fixture
def passthrough_gk() -> ApiGatekeeper:
    gk = MagicMock(spec=ApiGatekeeper)
    gk.call.side_effect = lambda service, fn: fn()
    return gk


@pytest.fixture
def mock_ollama() -> MagicMock:
    svc = MagicMock()
    svc.run.return_value = _result("ollama")
    return svc


@pytest.fixture
def mock_hf() -> MagicMock:
    svc = MagicMock()
    svc.run.return_value = _result("hf_baseline")
    return svc


@pytest.fixture
def mock_airllm() -> MagicMock:
    svc = MagicMock()
    svc.run.return_value = _result("airllm")
    return svc


def test_run_ollama_calls_service(passthrough_gk, mock_ollama) -> None:
    sdk = BenchmarkSDK(gatekeeper=passthrough_gk, ollama_service=mock_ollama)
    result = sdk.run_ollama("hello", "tinyllama", 20)
    mock_ollama.run.assert_called_once_with("hello", "tinyllama", 20)
    assert result.method == "ollama"


def test_run_hf_baseline_calls_service(passthrough_gk, mock_hf) -> None:
    sdk = BenchmarkSDK(gatekeeper=passthrough_gk, hf_service=mock_hf)
    result = sdk.run_hf_baseline("hello", "gpt2", 20)
    mock_hf.run.assert_called_once_with("hello", "gpt2", 20)
    assert result.method == "hf_baseline"


def test_run_airllm_calls_service(passthrough_gk, mock_airllm) -> None:
    sdk = BenchmarkSDK(gatekeeper=passthrough_gk, airllm_service=mock_airllm)
    result = sdk.run_airllm("hello", "llama2", 20)
    mock_airllm.run.assert_called_once_with("hello", "llama2", 20)
    assert result.method == "airllm"


def test_run_all_returns_report(passthrough_gk, mock_ollama, mock_hf, mock_airllm) -> None:
    sdk = BenchmarkSDK(
        gatekeeper=passthrough_gk,
        ollama_service=mock_ollama,
        hf_service=mock_hf,
        airllm_service=mock_airllm,
    )
    report = sdk.run_all("hello", 20)
    assert isinstance(report, ComparisonReport)
    assert len(report.results) == 3


def test_run_all_calls_all_three_services(passthrough_gk, mock_ollama, mock_hf, mock_airllm) -> None:
    sdk = BenchmarkSDK(
        gatekeeper=passthrough_gk,
        ollama_service=mock_ollama,
        hf_service=mock_hf,
        airllm_service=mock_airllm,
    )
    sdk.run_all("hello", 20)
    mock_ollama.run.assert_called_once()
    mock_hf.run.assert_called_once()
    mock_airllm.run.assert_called_once()


def test_compare_results_returns_report() -> None:
    sdk = BenchmarkSDK()
    results = [_result("ollama"), _result("airllm")]
    report = sdk.compare_results(results)
    assert isinstance(report, ComparisonReport)
    assert len(report.results) == 2


def test_empty_prompt_raises_run_ollama() -> None:
    sdk = BenchmarkSDK()
    with pytest.raises(ValueError, match="prompt"):
        sdk.run_ollama("", "tinyllama", 20)


def test_whitespace_only_prompt_raises_run_all() -> None:
    sdk = BenchmarkSDK()
    with pytest.raises(ValueError, match="prompt"):
        sdk.run_all("   ", 10)


def test_max_tokens_zero_raises_run_hf() -> None:
    sdk = BenchmarkSDK()
    with pytest.raises(ValueError, match="max_tokens"):
        sdk.run_hf_baseline("hello", "gpt2", 0)


def test_max_tokens_negative_raises_run_airllm() -> None:
    sdk = BenchmarkSDK()
    with pytest.raises(ValueError, match="max_tokens"):
        sdk.run_airllm("hello", "llama2", -5)


def test_run_all_captures_service_error_as_failed_result(
    passthrough_gk, mock_ollama, mock_hf, mock_airllm
) -> None:
    mock_ollama.run.side_effect = RuntimeError("Connection refused")
    sdk = BenchmarkSDK(
        gatekeeper=passthrough_gk,
        ollama_service=mock_ollama,
        hf_service=mock_hf,
        airllm_service=mock_airllm,
    )
    report = sdk.run_all("hello", 20)
    assert len(report.results) == 3
    ollama_r = next(r for r in report.results if r.method == "ollama")
    assert not ollama_r.is_success
    assert "Connection refused" in ollama_r.error


def test_run_all_uses_config_model_ids(passthrough_gk, mock_ollama, mock_hf, mock_airllm) -> None:
    cfg = {
        "ollama_model": "custom-ollama",
        "model_id": "custom-hf",
        "airllm_model_id": "custom-airllm",
    }
    sdk = BenchmarkSDK(
        config=cfg,
        gatekeeper=passthrough_gk,
        ollama_service=mock_ollama,
        hf_service=mock_hf,
        airllm_service=mock_airllm,
    )
    sdk.run_all("hello", 20)
    mock_ollama.run.assert_called_once_with("hello", "custom-ollama", 20)
    mock_hf.run.assert_called_once_with("hello", "custom-hf", 20)
    mock_airllm.run.assert_called_once_with("hello", "custom-airllm", 20)
