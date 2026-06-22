"""ChartService — generate and save benchmark comparison charts."""
from __future__ import annotations

from pathlib import Path

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.shared.config import load_config


class ChartService:
    COLOR_SCHEME = {"ollama": "#4CAF50", "hf_baseline": "#2196F3", "airllm": "#FF9800"}

    def __init__(self, config: dict | None = None) -> None:
        cfg = config if config is not None else load_config()
        self._assets_dir = Path(cfg.get("assets_dir", "./assets"))

    def _ensure_dir(self) -> None:
        self._assets_dir.mkdir(parents=True, exist_ok=True)

    def _prepare_latency_data(self, results: list[BenchmarkResult]) -> dict:
        return {r.method: r.latency_s for r in results if r.is_success}

    def _prepare_memory_data(self, results: list[BenchmarkResult]) -> dict:
        return {r.method: {"ram": r.ram_peak_mb, "vram": r.vram_peak_mb} for r in results if r.is_success}

    def _save_chart(self, fig, name: str) -> Path:
        self._ensure_dir()
        path = self._assets_dir / f"{name}.png"
        fig.savefig(path, bbox_inches="tight", dpi=150)
        return path

    def plot_latency_bar(self, results: list[BenchmarkResult]) -> Path:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        data = self._prepare_latency_data(results)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [self.COLOR_SCHEME.get(m, "#999") for m in data]
        ax.bar(list(data.keys()), list(data.values()), color=colors)
        ax.set_title("Inference Latency by Method")
        ax.set_ylabel("Latency (s)")
        ax.set_xlabel("Method")
        path = self._save_chart(fig, "latency_bar")
        plt.close(fig)
        return path

    def plot_memory_grouped_bar(self, results: list[BenchmarkResult]) -> Path:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        data = self._prepare_memory_data(results)
        methods = list(data.keys())
        x = np.arange(len(methods))
        width = 0.35
        ram_vals = [data[m]["ram"] for m in methods]
        vram_vals = [data[m]["vram"] for m in methods]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width / 2, ram_vals, width, label="RAM (MB)", color="#607D8B")
        ax.bar(x + width / 2, vram_vals, width, label="VRAM (MB)", color="#9C27B0")
        ax.set_xticks(x)
        ax.set_xticklabels(methods)
        ax.set_title("Peak Memory Usage by Method")
        ax.set_ylabel("Memory (MB)")
        ax.legend()
        path = self._save_chart(fig, "memory_grouped_bar")
        plt.close(fig)
        return path

    def plot_throughput_bar(self, results: list[BenchmarkResult]) -> Path:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        data = {r.method: r.tokens_per_second for r in results if r.is_success}
        colors = [self.COLOR_SCHEME.get(m, "#999") for m in data]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(list(data.keys()), list(data.values()), color=colors)
        ax.set_title("Token Throughput by Method")
        ax.set_ylabel("Tokens / second")
        ax.set_xlabel("Method")
        path = self._save_chart(fig, "throughput_bar")
        plt.close(fig)
        return path

    def plot_trade_off_scatter(self, results: list[BenchmarkResult]) -> Path:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        for r in results:
            if r.is_success:
                color = self.COLOR_SCHEME.get(r.method, "#999")
                ax.scatter(r.latency_s, r.ram_peak_mb, s=200, color=color, label=r.method, zorder=3)
        ax.set_title("Latency vs RAM — Trade-off Scatter")
        ax.set_xlabel("Latency (s)")
        ax.set_ylabel("RAM (MB)")
        ax.legend()
        path = self._save_chart(fig, "trade_off_scatter")
        plt.close(fig)
        return path

    def generate_all_charts(self, results: list[BenchmarkResult]) -> list[Path]:
        return [
            self.plot_latency_bar(results),
            self.plot_memory_grouped_bar(results),
            self.plot_throughput_bar(results),
            self.plot_trade_off_scatter(results),
        ]
