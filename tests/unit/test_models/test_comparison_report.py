"""Tests for ComparisonReport dataclass."""
from __future__ import annotations

import json

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport


def _make(method: str, latency: float, ram: float, tps: float = 5.0,
          error: str = "") -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="m", prompt="p",
        latency_s=latency, ram_peak_mb=ram,
        tokens_generated=10, tokens_per_second=tps,
        error=error,
    )


@pytest.fixture
def three_results() -> list[BenchmarkResult]:
    return [
        _make("ollama",      latency=1.0, ram=200.0, tps=10.0),
        _make("hf_baseline", latency=5.0, ram=800.0, tps=2.0),
        _make("airllm",      latency=30.0, ram=300.0, tps=0.3),
    ]


@pytest.fixture
def report(three_results: list[BenchmarkResult]) -> ComparisonReport:
    return ComparisonReport(results=three_results)


def test_fastest_method(report: ComparisonReport) -> None:
    assert report.fastest_method == "ollama"


def test_most_memory_efficient(report: ComparisonReport) -> None:
    assert report.most_memory_efficient == "ollama"


def test_fastest_excludes_failed_results() -> None:
    results = [
        _make("ollama", latency=1.0, ram=200.0, error="fail"),
        _make("airllm", latency=30.0, ram=300.0),
    ]
    r = ComparisonReport(results=results)
    assert r.fastest_method == "airllm"


def test_fastest_method_none_when_all_failed() -> None:
    results = [_make("ollama", 1.0, 200.0, error="fail")]
    r = ComparisonReport(results=results)
    assert r.fastest_method is None


def test_summary_table_contains_all_methods(report: ComparisonReport) -> None:
    table = report.summary_table()
    assert "ollama" in table
    assert "hf_baseline" in table
    assert "airllm" in table


def test_summary_table_has_header(report: ComparisonReport) -> None:
    assert "| Method |" in report.summary_table()


def test_cost_breakdown_has_one_key_per_result(report: ComparisonReport) -> None:
    breakdown = report.cost_breakdown()
    assert set(breakdown.keys()) == {"ollama", "hf_baseline", "airllm"}


def test_recommendations_non_empty(report: ComparisonReport) -> None:
    assert len(report.recommendations()) >= 1


def test_to_markdown_contains_table(report: ComparisonReport) -> None:
    md = report.to_markdown()
    assert "|" in md
    assert "Recommendations" in md


def test_to_dict_is_json_serializable(report: ComparisonReport) -> None:
    json.dumps(report.to_dict())  # must not raise


def test_to_dict_has_results_key(report: ComparisonReport) -> None:
    d = report.to_dict()
    assert "results" in d
    assert len(d["results"]) == 3


def test_single_result_report() -> None:
    r = ComparisonReport(results=[_make("ollama", 1.0, 200.0)])
    assert r.fastest_method == "ollama"
    assert len(r.recommendations()) >= 1


def test_failed_result_appears_in_recommendations() -> None:
    results = [
        _make("ollama", 1.0, 200.0),
        _make("hf_baseline", 5.0, 800.0, error="OOM"),
    ]
    recs = ComparisonReport(results=results).recommendations()
    assert any("hf_baseline" in r for r in recs)
