"""ComparisonReport — aggregates multiple BenchmarkResults for comparison."""
from __future__ import annotations

import json
from dataclasses import dataclass

from airllm_benchmark.models.benchmark_result import BenchmarkResult


@dataclass
class ComparisonReport:
    results: list[BenchmarkResult]

    @property
    def _successful(self) -> list[BenchmarkResult]:
        return [r for r in self.results if r.is_success]

    @property
    def fastest_method(self) -> str | None:
        if not self._successful:
            return None
        return min(self._successful, key=lambda r: r.latency_s).method

    @property
    def most_memory_efficient(self) -> str | None:
        if not self._successful:
            return None
        return min(self._successful, key=lambda r: r.ram_peak_mb).method

    def summary_table(self) -> str:
        header = "| Method | Latency (s) | RAM (MB) | VRAM (MB) | Tokens/s | Cost |"
        sep    = "|--------|-------------|----------|-----------|----------|------|"
        rows = [header, sep]
        for r in self.results:
            note = " FAILED" if not r.is_success else ""
            rows.append(
                f"| {r.method} | {r.latency_s:.2f} | {r.ram_peak_mb:.1f} |"
                f" {r.vram_peak_mb:.1f} | {r.tokens_per_second:.2f} | {r.cost_estimate}{note} |"
            )
        return "\n".join(rows)

    def cost_breakdown(self) -> dict[str, str]:
        return {r.method: r.cost_estimate for r in self.results}

    def recommendations(self) -> list[str]:
        recs: list[str] = []
        fastest = self.fastest_method
        efficient = self.most_memory_efficient
        if fastest:
            recs.append(f"Use **{fastest}** for lowest latency.")
        if efficient and efficient != fastest:
            recs.append(f"Use **{efficient}** for lowest RAM footprint.")
        if any(r.method == "airllm" and r.is_success for r in self.results):
            recs.append("AirLLM successfully ran a model too large for normal VRAM via layer paging.")
        if any(not r.is_success for r in self.results):
            failed = [r.method for r in self.results if not r.is_success]
            recs.append(f"Methods that failed: {', '.join(failed)} — see error field for details.")
        return recs or ["No successful results to compare."]

    def to_markdown(self) -> str:
        lines = ["# Benchmark Comparison Report", "", "## Summary", "", self.summary_table(), ""]
        lines += ["## Cost Breakdown", ""]
        for method, cost in self.cost_breakdown().items():
            lines.append(f"- **{method}**: {cost or '—'}")
        lines += ["", "## Recommendations", ""]
        for rec in self.recommendations():
            lines.append(f"- {rec}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "results": [r.to_dict() for r in self.results],
            "fastest_method": self.fastest_method,
            "most_memory_efficient": self.most_memory_efficient,
            "recommendations": self.recommendations(),
            "cost_breakdown": self.cost_breakdown(),
            "summary_table": self.summary_table(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
