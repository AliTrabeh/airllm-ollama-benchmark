"""Integration tests — full pipeline: SDK → ResultsService → ChartService (services mocked)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.results_service import ResultsService
from airllm_benchmark.visualization.chart_service import ChartService


def _result(method: str, latency: float = 1.0, error: str = "") -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="test/m", prompt="hi",
        latency_s=latency, ram_peak_mb=500.0,
        tokens_generated=5, tokens_per_second=5.0,
        error=error,
    )


@pytest.fixture
def three_results() -> list[BenchmarkResult]:
    return [_result("ollama", 1.0), _result("hf_baseline", 5.0), _result("airllm", 30.0)]


@pytest.fixture
def mock_sdk(three_results: list[BenchmarkResult]) -> BenchmarkSDK:
    gk = MagicMock()
    gk.call.side_effect = lambda svc, fn: fn()
    ollama = MagicMock()
    ollama.run.return_value = three_results[0]
    hf = MagicMock()
    hf.run.return_value = three_results[1]
    airllm = MagicMock()
    airllm.run.return_value = three_results[2]
    return BenchmarkSDK(gatekeeper=gk, ollama_service=ollama, hf_service=hf, airllm_service=airllm)


# ---------------------------------------------------------------------------

def test_sdk_run_all_produces_comparison_report(mock_sdk: BenchmarkSDK) -> None:
    report = mock_sdk.run_all("hello", 20)
    assert isinstance(report, ComparisonReport)
    assert len(report.results) == 3


def test_results_service_save_load_roundtrip(tmp_path: Path, three_results: list) -> None:
    svc = ResultsService(config={"results_dir": str(tmp_path)})
    for r in three_results:
        svc.save_result(r)
    path = svc.save_comparison(svc.generate_comparison(three_results))
    loaded = svc.load_comparison(path)
    assert len(loaded.results) == 3
    assert loaded.fastest_method == "ollama"


def test_chart_service_generates_four_png_files(tmp_path: Path, three_results: list) -> None:
    paths = ChartService(config={"assets_dir": str(tmp_path)}).generate_all_charts(three_results)
    assert len(paths) == 4
    assert all(p.exists() and p.suffix == ".png" for p in paths)


def test_full_pipeline_sdk_to_storage_to_charts(tmp_path: Path, mock_sdk: BenchmarkSDK) -> None:
    results_dir = tmp_path / "results"
    assets_dir  = tmp_path / "assets"

    report = mock_sdk.run_all("hello", 20)

    svc = ResultsService(config={"results_dir": str(results_dir)})
    for r in report.results:
        svc.save_result(r)
    cmp_path = svc.save_comparison(report)

    data = json.loads(cmp_path.read_text())
    assert "results" in data and len(data["results"]) == 3

    loaded = svc.load_comparison(cmp_path)
    chart_paths = ChartService(config={"assets_dir": str(assets_dir)}).generate_all_charts(loaded.results)
    assert len(chart_paths) == 4 and all(p.exists() for p in chart_paths)


def test_comparison_report_markdown_contains_all_sections(three_results: list) -> None:
    md = ComparisonReport(results=three_results).to_markdown()
    assert all(s in md for s in ("ollama", "hf_baseline", "airllm", "Recommendations"))


def test_comparison_report_fastest_method(three_results: list) -> None:
    report = ComparisonReport(results=three_results)
    assert report.fastest_method == "ollama"
    assert report.most_memory_efficient == "ollama"


def test_failed_result_excluded_from_fastest() -> None:
    results = [
        _result("ollama", error="connection refused"),
        _result("hf_baseline", 5.0),
        _result("airllm", 30.0),
    ]
    assert ComparisonReport(results=results).fastest_method == "hf_baseline"
