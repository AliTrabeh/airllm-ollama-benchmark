"""Tests for MetricsCollector and MetricsSnapshot."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.metrics_service import MetricsCollector, MetricsSnapshot

# ---------------------------------------------------------------------------
# Snapshot shape
# ---------------------------------------------------------------------------

def test_snapshot_none_before_exit() -> None:
    mc = MetricsCollector()
    assert mc.snapshot is None


def test_snapshot_available_after_exit() -> None:
    with MetricsCollector() as mc:
        pass
    assert isinstance(mc.snapshot, MetricsSnapshot)


def test_snapshot_has_all_fields() -> None:
    with MetricsCollector() as mc:
        pass
    snap = mc.snapshot
    assert hasattr(snap, "latency_s")
    assert hasattr(snap, "ram_start_mb")
    assert hasattr(snap, "ram_peak_mb")
    assert hasattr(snap, "ram_end_mb")
    assert hasattr(snap, "vram_start_mb")
    assert hasattr(snap, "vram_peak_mb")


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

def test_timing_captured() -> None:
    with MetricsCollector() as mc:
        time.sleep(0.1)
    assert mc.snapshot.latency_s == pytest.approx(0.1, abs=0.05)


def test_latency_is_positive() -> None:
    with MetricsCollector() as mc:
        pass
    assert mc.snapshot.latency_s >= 0.0


# ---------------------------------------------------------------------------
# RAM
# ---------------------------------------------------------------------------

def test_ram_start_is_positive() -> None:
    with MetricsCollector() as mc:
        pass
    assert mc.snapshot.ram_start_mb > 0.0


def test_ram_peak_ge_start() -> None:
    with MetricsCollector(sample_interval_s=0.01) as mc:
        pass
    assert mc.snapshot.ram_peak_mb >= mc.snapshot.ram_start_mb


def test_ram_peak_captures_allocation() -> None:
    with MetricsCollector(sample_interval_s=0.01) as mc:
        big = bytearray(40 * 1024 * 1024)  # allocate 40 MB
        time.sleep(0.05)                    # let sampler catch it
        del big
    assert mc.snapshot.ram_peak_mb >= mc.snapshot.ram_start_mb


# ---------------------------------------------------------------------------
# VRAM — no-CUDA path (torch not installed or CUDA unavailable)
# ---------------------------------------------------------------------------

def test_no_cuda_vram_is_zero() -> None:
    with (
        patch("airllm_benchmark.services.metrics_service._cuda_allocated_mb", return_value=0.0),
        patch("airllm_benchmark.services.metrics_service._cuda_peak_mb", return_value=0.0),MetricsCollector() as mc
    ):
        pass
    assert mc.snapshot.vram_start_mb == 0.0
    assert mc.snapshot.vram_peak_mb == 0.0


def test_no_cuda_does_not_raise() -> None:
    with patch("airllm_benchmark.services.metrics_service._cuda_reset_peak"), MetricsCollector() as mc:
        pass
    assert mc.snapshot is not None


# ---------------------------------------------------------------------------
# Exception passthrough — collector must not swallow errors
# ---------------------------------------------------------------------------

def test_exception_not_suppressed() -> None:
    with pytest.raises(ValueError, match="test error"), MetricsCollector():
        raise ValueError("test error")


def test_snapshot_set_even_on_exception() -> None:
    mc = MetricsCollector()
    try:
        with mc:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert mc.snapshot is not None


# ---------------------------------------------------------------------------
# BenchmarkResult serialisation roundtrip (PRD-05 acceptance criterion)
# ---------------------------------------------------------------------------

def test_benchmark_result_json_roundtrip() -> None:
    r = BenchmarkResult(
        method="airllm",
        model_id="mistralai/Mistral-7B-v0.1",
        prompt="Hello",
        latency_s=3.14,
        ram_peak_mb=1024.0,
        tokens_generated=20,
        tokens_per_second=6.4,
        vram_peak_mb=512.0,
        cost_estimate="~0.01 kWh",
    )
    restored = BenchmarkResult.from_dict(r.to_dict())
    assert restored.latency_s == r.latency_s
    assert restored.vram_peak_mb == r.vram_peak_mb
    assert restored.cost_estimate == r.cost_estimate
    assert restored.timestamp == r.timestamp
