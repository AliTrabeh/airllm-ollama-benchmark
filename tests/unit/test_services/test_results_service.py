"""Tests for ResultsService — save/load/compare BenchmarkResult files."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.services.results_service import ResultsService


def _r(method: str = "ollama", latency: float = 1.0) -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="test-model", prompt="hello",
        latency_s=latency, ram_peak_mb=200.0,
        tokens_generated=10, tokens_per_second=10.0,
        cost_estimate="~0.001 kWh @ 65W TDP",
    )


@pytest.fixture
def svc(tmp_path: Path) -> ResultsService:
    return ResultsService(config={"results_dir": str(tmp_path)})


@pytest.fixture
def three_results() -> list[BenchmarkResult]:
    return [_r("ollama", 1.0), _r("hf_baseline", 5.0), _r("airllm", 30.0)]


# ---------------------------------------------------------------------------
# save / load single result
# ---------------------------------------------------------------------------

def test_save_and_load_result_roundtrip(svc) -> None:
    r = _r("ollama")
    path = svc.save_result(r)
    loaded = svc.load_result(path)
    assert loaded.method == r.method
    assert loaded.latency_s == r.latency_s
    assert loaded.ram_peak_mb == r.ram_peak_mb
    assert loaded.timestamp == r.timestamp


def test_save_result_filename_contains_method(svc) -> None:
    path = svc.save_result(_r("airllm"))
    assert "run_" in path.name
    assert "airllm" in path.name
    assert path.suffix == ".json"


def test_save_result_is_valid_json(svc) -> None:
    path = svc.save_result(_r("ollama"))
    data = json.loads(path.read_text())
    assert data["method"] == "ollama"
    assert "latency_s" in data
    assert "ram_peak_mb" in data


# ---------------------------------------------------------------------------
# comparison report
# ---------------------------------------------------------------------------

def test_comparison_report_generated(svc, three_results) -> None:
    report = svc.generate_comparison(three_results)
    assert isinstance(report, ComparisonReport)
    table = report.summary_table()
    assert "ollama" in table
    assert "hf_baseline" in table
    assert "airllm" in table


def test_cost_breakdown_present(svc, three_results) -> None:
    report = svc.generate_comparison(three_results)
    breakdown = report.cost_breakdown()
    assert set(breakdown.keys()) == {"ollama", "hf_baseline", "airllm"}


def test_recommendations_present(svc, three_results) -> None:
    report = svc.generate_comparison(three_results)
    assert len(report.recommendations()) >= 1


def test_save_comparison_includes_cost_breakdown(svc, three_results) -> None:
    report = svc.generate_comparison(three_results)
    path = svc.save_comparison(report)
    data = json.loads(path.read_text())
    assert "cost_breakdown" in data
    assert "summary_table" in data
    assert "recommendations" in data


def test_load_comparison_roundtrip(svc, three_results) -> None:
    report = svc.generate_comparison(three_results)
    path = svc.save_comparison(report)
    loaded = svc.load_comparison(path)
    assert len(loaded.results) == 3
    assert loaded.fastest_method == report.fastest_method
    assert loaded.most_memory_efficient == report.most_memory_efficient


# ---------------------------------------------------------------------------
# directory / listing
# ---------------------------------------------------------------------------

def test_results_dir_created_if_missing(tmp_path) -> None:
    new_dir = tmp_path / "subdir" / "results"
    svc = ResultsService(config={"results_dir": str(new_dir)})
    svc.save_result(_r("ollama"))
    assert new_dir.exists()


def test_list_results_returns_all_saved(svc) -> None:
    svc.save_result(_r("ollama"))
    svc.save_result(_r("airllm"))
    assert len(svc.list_results()) == 2


def test_list_comparisons(svc, three_results) -> None:
    svc.save_comparison(svc.generate_comparison(three_results))
    assert len(svc.list_comparisons()) == 1


def test_list_results_empty_before_any_save(tmp_path) -> None:
    svc = ResultsService(config={"results_dir": str(tmp_path / "nonexistent")})
    assert svc.list_results() == []
    assert svc.list_comparisons() == []
