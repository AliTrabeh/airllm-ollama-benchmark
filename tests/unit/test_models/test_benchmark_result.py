"""Tests for BenchmarkResult dataclass."""
from __future__ import annotations

import json
from datetime import datetime

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult


@pytest.fixture
def sample() -> BenchmarkResult:
    return BenchmarkResult(
        method="ollama",
        model_id="tinyllama",
        prompt="Hello",
        latency_s=2.5,
        ram_peak_mb=512.0,
        tokens_generated=15,
        tokens_per_second=6.0,
        output="Hi there!",
        vram_peak_mb=0.0,
        cost_estimate="$0.000012",
    )


def test_creation(sample: BenchmarkResult) -> None:
    assert sample.method == "ollama"
    assert sample.model_id == "tinyllama"
    assert sample.latency_s == 2.5


def test_is_success_true(sample: BenchmarkResult) -> None:
    assert sample.is_success is True


def test_is_success_false_when_error_set(sample: BenchmarkResult) -> None:
    sample.error = "Connection refused"
    assert sample.is_success is False


def test_default_error_is_empty() -> None:
    r = BenchmarkResult("ollama", "m", "p", 1.0, 100.0, 5, 5.0)
    assert r.error == ""


def test_default_vram_is_zero() -> None:
    r = BenchmarkResult("ollama", "m", "p", 1.0, 100.0, 5, 5.0)
    assert r.vram_peak_mb == 0.0


def test_to_dict_has_all_keys(sample: BenchmarkResult) -> None:
    d = sample.to_dict()
    expected = {"method", "model_id", "prompt", "output", "latency_s",
                "ram_peak_mb", "vram_peak_mb", "tokens_generated",
                "tokens_per_second", "disk_gb", "cost_estimate", "error", "timestamp"}
    assert expected == set(d.keys())


def test_to_dict_is_json_serializable(sample: BenchmarkResult) -> None:
    json.dumps(sample.to_dict())  # must not raise


def test_from_dict_round_trip(sample: BenchmarkResult) -> None:
    restored = BenchmarkResult.from_dict(sample.to_dict())
    assert restored.method == sample.method
    assert restored.latency_s == sample.latency_s
    assert restored.output == sample.output
    assert restored.timestamp == sample.timestamp


def test_timestamp_is_iso8601(sample: BenchmarkResult) -> None:
    datetime.fromisoformat(sample.timestamp)  # must not raise


def test_error_result_constructor() -> None:
    r = BenchmarkResult.error_result("airllm", "mistral", "q?", "OOM")
    assert r.is_success is False
    assert r.error == "OOM"
    assert r.latency_s == 0.0
    assert r.tokens_generated == 0


def test_from_dict_missing_optional_fields() -> None:
    minimal = {"method": "ollama", "model_id": "m", "prompt": "p",
               "latency_s": 1.0, "ram_peak_mb": 100.0,
               "tokens_generated": 5, "tokens_per_second": 5.0}
    r = BenchmarkResult.from_dict(minimal)
    assert r.vram_peak_mb == 0.0
    assert r.error == ""
