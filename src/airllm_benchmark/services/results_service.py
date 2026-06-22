"""ResultsService — persist BenchmarkResult and ComparisonReport to JSON files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.shared.config import load_config


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class ResultsService:
    """Saves and loads benchmark results; generates comparison reports."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config if config is not None else load_config()
        self._results_dir = Path(cfg.get("results_dir", "./results"))

    def save_result(self, result: BenchmarkResult) -> Path:
        """Write one BenchmarkResult to results/run_<ts>_<method>.json."""
        self._results_dir.mkdir(parents=True, exist_ok=True)
        path = self._results_dir / f"run_{_ts()}_{result.method}.json"
        path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        return path

    def save_comparison(self, report: ComparisonReport) -> Path:
        """Write a ComparisonReport to results/comparison_<ts>.json."""
        self._results_dir.mkdir(parents=True, exist_ok=True)
        path = self._results_dir / f"comparison_{_ts()}.json"
        path.write_text(report.to_json(), encoding="utf-8")
        return path

    def load_result(self, path: Path) -> BenchmarkResult:
        return BenchmarkResult.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def load_comparison(self, path: Path) -> ComparisonReport:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ComparisonReport(
            results=[BenchmarkResult.from_dict(r) for r in data["results"]]
        )

    def generate_comparison(self, results: list[BenchmarkResult]) -> ComparisonReport:
        return ComparisonReport(results=results)

    def list_results(self) -> list[Path]:
        if not self._results_dir.exists():
            return []
        return sorted(self._results_dir.glob("run_*.json"))

    def list_comparisons(self) -> list[Path]:
        if not self._results_dir.exists():
            return []
        return sorted(self._results_dir.glob("comparison_*.json"))
