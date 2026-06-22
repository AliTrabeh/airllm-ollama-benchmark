"""Tests for NotebookDataPreparer."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.visualization.notebook_data import NotebookDataPreparer


def _result(method: str, latency: float = 1.0) -> BenchmarkResult:
    return BenchmarkResult(
        method=method, model_id="test/m", prompt="hi",
        latency_s=latency, ram_peak_mb=500.0,
        tokens_generated=5, tokens_per_second=5.0,
        cost_estimate="~0.001 kWh @ 65W TDP",
    )


def _save_result(results_dir: Path, result: BenchmarkResult) -> None:
    path = results_dir / f"run_20260101T000000Z_{result.method}.json"
    path.write_text(json.dumps(result.to_dict()), encoding="utf-8")


@pytest.fixture
def preparer_with_results(tmp_path: Path) -> NotebookDataPreparer:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    for r in [_result("ollama", 1.0), _result("hf_baseline", 5.0), _result("airllm", 30.0)]:
        _save_result(results_dir, r)
    return NotebookDataPreparer(results_dir=results_dir)


def test_load_results_returns_list(preparer_with_results: NotebookDataPreparer) -> None:
    results = preparer_with_results.load_results()
    assert isinstance(results, list)
    assert len(results) == 3


def test_load_results_empty_dir(tmp_path: Path) -> None:
    preparer = NotebookDataPreparer(results_dir=tmp_path / "empty")
    assert preparer.load_results() == []


def test_summary_dataframe_has_correct_columns(preparer_with_results: NotebookDataPreparer) -> None:
    df = preparer_with_results.summary_dataframe()
    expected = {"method", "model_id", "latency_s", "ram_peak_mb", "vram_peak_mb",
                "tokens_per_second", "tokens_generated", "cost_estimate", "is_success"}
    assert expected.issubset(set(df.columns))


def test_summary_dataframe_has_three_rows(preparer_with_results: NotebookDataPreparer) -> None:
    df = preparer_with_results.summary_dataframe()
    assert len(df) == 3


def test_summary_dataframe_empty_when_no_results(tmp_path: Path) -> None:
    preparer = NotebookDataPreparer(results_dir=tmp_path / "empty")
    df = preparer.summary_dataframe()
    assert df.empty


def test_summary_dataframe_methods_correct(preparer_with_results: NotebookDataPreparer) -> None:
    methods = set(preparer_with_results.summary_dataframe()["method"].tolist())
    assert methods == {"ollama", "hf_baseline", "airllm"}


def test_hardware_profile_summary_returns_string(preparer_with_results: NotebookDataPreparer) -> None:
    summary = preparer_with_results.hardware_profile_summary()
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_hardware_profile_mentions_rtx(preparer_with_results: NotebookDataPreparer) -> None:
    summary = preparer_with_results.hardware_profile_summary()
    assert "RTX" in summary or "3060" in summary


def test_hardware_profile_mentions_airllm(preparer_with_results: NotebookDataPreparer) -> None:
    summary = preparer_with_results.hardware_profile_summary()
    assert "AirLLM" in summary or "layer paging" in summary.lower()


def test_preparer_accepts_path_object(tmp_path: Path) -> None:
    preparer = NotebookDataPreparer(results_dir=tmp_path)
    assert preparer.load_results() == []


def test_preparer_accepts_string_path(tmp_path: Path) -> None:
    preparer = NotebookDataPreparer(results_dir=str(tmp_path))
    assert preparer.load_results() == []
