"""Tests for BenchmarkSDK.save_result/save_comparison/load_results.

These exist so the CLI never needs to call ResultsService directly --
"no service may be called directly" per the SDK's own docstring.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.sdk.sdk import BenchmarkSDK


def _result(method: str = "ollama") -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="m", prompt="p",
        latency_s=0.1, ram_peak_mb=100.0,
        tokens_generated=5, tokens_per_second=50.0,
    )


@pytest.fixture
def mock_results_svc(tmp_path: Path) -> MagicMock:
    svc = MagicMock()
    svc.save_result.return_value = tmp_path / "run_test.json"
    svc.save_comparison.return_value = tmp_path / "comparison_test.json"
    svc.list_results.return_value = [tmp_path / "run_a.json", tmp_path / "run_b.json"]
    svc.load_result.side_effect = [_result("ollama"), _result("hf_baseline")]
    return svc


def test_save_result_delegates_to_results_service(mock_results_svc) -> None:
    sdk = BenchmarkSDK(config={}, results_service=mock_results_svc)
    result = _result()
    path = sdk.save_result(result)
    mock_results_svc.save_result.assert_called_once_with(result)
    assert path.name == "run_test.json"


def test_save_comparison_delegates_to_results_service(mock_results_svc) -> None:
    sdk = BenchmarkSDK(config={}, results_service=mock_results_svc)
    report = ComparisonReport(results=[_result()])
    path = sdk.save_comparison(report)
    mock_results_svc.save_comparison.assert_called_once_with(report)
    assert path.name == "comparison_test.json"


def test_load_results_delegates_to_results_service(mock_results_svc) -> None:
    sdk = BenchmarkSDK(config={}, results_service=mock_results_svc)
    results = sdk.load_results()
    assert len(results) == 2
    assert results[0].method == "ollama"
    assert results[1].method == "hf_baseline"


def test_results_service_created_lazily_when_not_injected() -> None:
    sdk = BenchmarkSDK(config={"results_dir": "./results"})
    svc = sdk._results()
    assert svc.__class__.__name__ == "ResultsService"
