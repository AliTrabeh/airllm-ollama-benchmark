"""BenchmarkResult dataclass — holds the output of one inference run."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BenchmarkResult:
    method: str
    model_id: str
    prompt: str
    latency_s: float
    ram_peak_mb: float
    tokens_generated: int
    tokens_per_second: float
    output: str = ""
    vram_peak_mb: float = 0.0
    disk_gb: float = 0.0
    cost_estimate: str = ""
    error: str = ""
    timestamp: str = field(default_factory=_utc_now)

    @property
    def is_success(self) -> bool:
        return self.error == ""

    def to_dict(self) -> dict:
        return {
            "method": self.method,
            "model_id": self.model_id,
            "prompt": self.prompt,
            "output": self.output,
            "latency_s": self.latency_s,
            "ram_peak_mb": self.ram_peak_mb,
            "vram_peak_mb": self.vram_peak_mb,
            "tokens_generated": self.tokens_generated,
            "tokens_per_second": self.tokens_per_second,
            "disk_gb": self.disk_gb,
            "cost_estimate": self.cost_estimate,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> BenchmarkResult:
        return cls(
            method=d["method"],
            model_id=d["model_id"],
            prompt=d["prompt"],
            output=d.get("output", ""),
            latency_s=d["latency_s"],
            ram_peak_mb=d["ram_peak_mb"],
            vram_peak_mb=d.get("vram_peak_mb", 0.0),
            tokens_generated=d["tokens_generated"],
            tokens_per_second=d["tokens_per_second"],
            disk_gb=d.get("disk_gb", 0.0),
            cost_estimate=d.get("cost_estimate", ""),
            error=d.get("error", ""),
            timestamp=d.get("timestamp", _utc_now()),
        )

    @classmethod
    def error_result(cls, method: str, model_id: str, prompt: str, error: str) -> BenchmarkResult:
        """Convenience constructor for a failed run."""
        return cls(
            method=method,
            model_id=model_id,
            prompt=prompt,
            latency_s=0.0,
            ram_peak_mb=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            error=error,
        )
