"""CostEstimator — electricity-cost-from-TDP math, loaded from a hardware profile.

Produces a bare USD string (e.g. "$0.000123"). This is intentionally separate from
each service's BenchmarkResult.cost_estimate field, which uses an established
"~X.XXXXX kWh @ YW TDP" format already documented throughout README/COSTS.md/results
JSON — changing that format now would be a disruptive, low-value break. CostEstimator
exists as the genuinely reusable USD-cost utility the original design called for,
available for anything that wants a plain dollar figure (e.g. summarizing a whole run).
"""
from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_CPU_TDP_W = 95.0
_DEFAULT_GPU_TDP_W = 200.0
_DEFAULT_USD_PER_KWH = 0.12


class CostEstimator:
    def __init__(self, hardware_profile_path: str | Path | None = None) -> None:
        self._cpu_tdp_w = _DEFAULT_CPU_TDP_W
        self._gpu_tdp_w = _DEFAULT_GPU_TDP_W
        self._usd_per_kwh = _DEFAULT_USD_PER_KWH
        path = Path(hardware_profile_path) if hardware_profile_path else None
        if path and path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            target = data.get("target", data)
            self._cpu_tdp_w = target.get("cpu_tdp_w", self._cpu_tdp_w)
            self._gpu_tdp_w = target.get("gpu_tdp_w", self._gpu_tdp_w)
            self._usd_per_kwh = data.get("electricity_cost_usd_per_kwh", self._usd_per_kwh)

    @staticmethod
    def kwh_from_tdp(tdp_w: float, seconds: float) -> float:
        return tdp_w * seconds / 3_600_000

    @staticmethod
    def format_cost_string(usd: float) -> str:
        return f"${usd:.6f}"

    def estimate_cpu_cost(self, latency_s: float) -> str:
        kwh = self.kwh_from_tdp(self._cpu_tdp_w, latency_s)
        return self.format_cost_string(kwh * self._usd_per_kwh)

    def estimate_gpu_cost(self, latency_s: float) -> str:
        kwh = self.kwh_from_tdp(self._gpu_tdp_w, latency_s)
        return self.format_cost_string(kwh * self._usd_per_kwh)

    def estimate_combined_cost(self, latency_s: float) -> str:
        kwh = self.kwh_from_tdp(self._cpu_tdp_w, latency_s) + self.kwh_from_tdp(self._gpu_tdp_w, latency_s)
        return self.format_cost_string(kwh * self._usd_per_kwh)
