"""Tests for main.py CLI entry point."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.main import _model_gb_from_name, main, parse_args
from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport


def _result(method: str = "ollama") -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="m", prompt="p",
        latency_s=0.5, ram_peak_mb=100.0,
        tokens_generated=5, tokens_per_second=10.0,
    )


@pytest.fixture
def mock_sdk() -> MagicMock:
    report = ComparisonReport(results=[_result("ollama"), _result("hf_baseline"), _result("airllm")])
    sdk = MagicMock()
    sdk.run_all.return_value = report
    sdk.run_ollama.return_value = _result("ollama")
    sdk.run_hf_baseline.return_value = _result("hf_baseline")
    sdk.run_airllm.return_value = _result("airllm")
    return sdk


@pytest.fixture
def mock_svc(tmp_path: Path) -> MagicMock:
    svc = MagicMock()
    svc.save_result.return_value = tmp_path / "run_test.json"
    svc.save_comparison.return_value = tmp_path / "comparison_test.json"
    return svc


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

def test_parse_args_defaults() -> None:
    args = parse_args([])
    assert args.method == "all"
    assert args.max_tokens == 20
    assert not args.verbose


def test_parse_args_method_ollama() -> None:
    args = parse_args(["--method", "ollama"])
    assert args.method == "ollama"


def test_parse_args_method_airllm() -> None:
    args = parse_args(["--method", "airllm"])
    assert args.method == "airllm"


def test_parse_args_max_tokens() -> None:
    args = parse_args(["--max-tokens", "50"])
    assert args.max_tokens == 50


def test_parse_args_verbose() -> None:
    args = parse_args(["--verbose"])
    assert args.verbose


def test_parse_args_invalid_method() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--method", "invalid"])


# ---------------------------------------------------------------------------
# main() integration (services mocked)
# ---------------------------------------------------------------------------

def test_main_returns_zero(mock_sdk, mock_svc) -> None:
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=mock_sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        assert main([]) == 0


def test_main_ollama_returns_zero(mock_sdk, mock_svc) -> None:
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=mock_sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        assert main(["--method", "ollama"]) == 0


def test_main_airllm_returns_zero(mock_sdk, mock_svc) -> None:
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=mock_sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        assert main(["--method", "airllm"]) == 0


def test_main_error_returns_one(mock_svc) -> None:
    sdk = MagicMock()
    sdk.run_all.side_effect = RuntimeError("connection failed")
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        assert main([]) == 1


def test_main_all_saves_comparison(mock_sdk, mock_svc) -> None:
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=mock_sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        main([])
    mock_svc.save_comparison.assert_called_once()


def test_main_single_saves_result(mock_sdk, mock_svc) -> None:
    with patch("airllm_benchmark.main.BenchmarkSDK", return_value=mock_sdk), \
         patch("airllm_benchmark.main.ResultsService", return_value=mock_svc):
        main(["--method", "ollama"])
    mock_svc.save_result.assert_called_once()


# ---------------------------------------------------------------------------
# _model_gb_from_name
# ---------------------------------------------------------------------------

def test_model_gb_from_name_parses_7b() -> None:
    assert _model_gb_from_name("mistralai/Mistral-7B-v0.1") == 14.0


def test_model_gb_from_name_parses_lowercase_b() -> None:
    assert _model_gb_from_name("llama3.2:3b") == 6.0


def test_model_gb_from_name_returns_none_when_no_size_in_name() -> None:
    assert _model_gb_from_name("microsoft/Phi-3-mini-4k-instruct") is None
