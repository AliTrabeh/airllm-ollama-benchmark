"""Tests for ResultsService.load_by_method() / load_latest()."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
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


def test_load_by_method_filters_correctly(svc) -> None:
    timestamps = ["20260101T000000Z", "20260101T000001Z", "20260101T000002Z"]
    with patch("airllm_benchmark.services.results_service._ts", side_effect=timestamps):
        svc.save_result(_r("ollama"))
        svc.save_result(_r("airllm"))
        svc.save_result(_r("ollama"))
    assert len(svc.load_by_method("ollama")) == 2
    assert all(r.method == "ollama" for r in svc.load_by_method("ollama"))


def test_load_latest_returns_newest(svc) -> None:
    timestamps = ["20260101T000000Z", "20260101T000001Z"]
    with patch("airllm_benchmark.services.results_service._ts", side_effect=timestamps):
        svc.save_result(_r("ollama", latency=1.0))
        svc.save_result(_r("ollama", latency=2.0))
    assert svc.load_latest().latency_s == 2.0


def test_load_latest_filters_by_method(svc) -> None:
    timestamps = ["20260101T000000Z", "20260101T000001Z"]
    with patch("airllm_benchmark.services.results_service._ts", side_effect=timestamps):
        svc.save_result(_r("ollama", latency=1.0))
        svc.save_result(_r("airllm", latency=2.0))
    assert svc.load_latest(method="ollama").latency_s == 1.0


def test_load_latest_returns_none_on_empty_dir(tmp_path) -> None:
    svc = ResultsService(config={"results_dir": str(tmp_path)})
    assert svc.load_latest() is None
