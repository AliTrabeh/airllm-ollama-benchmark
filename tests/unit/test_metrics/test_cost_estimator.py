"""Tests for CostEstimator."""
from __future__ import annotations

import json
from pathlib import Path

from airllm_benchmark.metrics.cost_estimator import CostEstimator


def test_kwh_from_tdp_formula_correctness() -> None:
    assert CostEstimator.kwh_from_tdp(95, 3600) == 0.095


def test_format_cost_string_six_decimals() -> None:
    assert CostEstimator.format_cost_string(0.123456789) == "$0.123457"


def test_estimate_cpu_cost_returns_formatted_string(tmp_path: Path) -> None:
    profile = tmp_path / "hw.json"
    data = {"target": {"cpu_tdp_w": 95}, "electricity_cost_usd_per_kwh": 0.12}
    profile.write_text(json.dumps(data), encoding="utf-8")
    cost = CostEstimator(hardware_profile_path=profile).estimate_cpu_cost(3600)
    assert cost.startswith("$")
    assert any(ch.isdigit() for ch in cost)


def test_estimate_gpu_cost_returns_formatted_string(tmp_path: Path) -> None:
    profile = tmp_path / "hw.json"
    data = {"target": {"gpu_tdp_w": 200}, "electricity_cost_usd_per_kwh": 0.12}
    profile.write_text(json.dumps(data), encoding="utf-8")
    cost = CostEstimator(hardware_profile_path=profile).estimate_gpu_cost(3600)
    assert cost.startswith("$")


def test_estimate_combined_cost_exceeds_cpu_only_when_gpu_tdp_positive(tmp_path: Path) -> None:
    profile = tmp_path / "hw.json"
    profile.write_text(
        json.dumps({"target": {"cpu_tdp_w": 95, "gpu_tdp_w": 200}, "electricity_cost_usd_per_kwh": 0.12}),
        encoding="utf-8",
    )
    estimator = CostEstimator(hardware_profile_path=profile)
    cpu_only = float(estimator.estimate_cpu_cost(3600).lstrip("$"))
    combined = float(estimator.estimate_combined_cost(3600).lstrip("$"))
    assert combined > cpu_only


def test_loads_hardware_profile_from_json(tmp_path: Path) -> None:
    profile = tmp_path / "hw.json"
    profile.write_text(json.dumps({"target": {"cpu_tdp_w": 50}, "electricity_cost_usd_per_kwh": 1.0}), encoding="utf-8")
    estimator = CostEstimator(hardware_profile_path=profile)
    assert estimator._cpu_tdp_w == 50


def test_estimate_cpu_cost_zero_latency_returns_zero_cost(tmp_path: Path) -> None:
    profile = tmp_path / "hw.json"
    profile.write_text(json.dumps({"target": {"cpu_tdp_w": 95}}), encoding="utf-8")
    assert CostEstimator(hardware_profile_path=profile).estimate_cpu_cost(0) == "$0.000000"


def test_defaults_used_when_no_profile_path_given() -> None:
    estimator = CostEstimator()
    assert estimator.estimate_cpu_cost(0) == "$0.000000"
