"""NotebookDataPreparer — load results and build DataFrames for notebook analysis."""
from __future__ import annotations

from pathlib import Path

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.results_service import ResultsService
from airllm_benchmark.shared.config import load_config


class NotebookDataPreparer:
    def __init__(self, results_dir: str | Path | None = None) -> None:
        cfg = load_config()
        if results_dir is not None:
            cfg["results_dir"] = str(results_dir)
        self._svc = ResultsService(config=cfg)

    def load_results(self) -> list[BenchmarkResult]:
        return [self._svc.load_result(p) for p in self._svc.list_results()]

    def summary_dataframe(self):  # -> pd.DataFrame
        import pandas as pd

        results = self.load_results()
        rows = []
        for r in results:
            rows.append(
                {
                    "method": r.method,
                    "model_id": r.model_id,
                    "latency_s": r.latency_s,
                    "ram_peak_mb": r.ram_peak_mb,
                    "vram_peak_mb": r.vram_peak_mb,
                    "tokens_per_second": r.tokens_per_second,
                    "tokens_generated": r.tokens_generated,
                    "cost_estimate": r.cost_estimate,
                    "is_success": r.is_success,
                }
            )
        return pd.DataFrame(rows)

    def hardware_profile_summary(self) -> str:
        return (
            "Hardware: Intel i7-4790K | RTX 3060 Ti 8 GB VRAM | 32 GB DDR3\n"
            "AirLLM target: Mistral-7B-v0.1 (14 GB fp16) — exceeds VRAM, runs via CPU layer paging"
        )
