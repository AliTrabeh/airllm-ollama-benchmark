"""MetricsCollector — context manager that captures timing, RAM, and VRAM during inference."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import psutil


@dataclass
class MetricsSnapshot:
    latency_s: float
    ram_start_mb: float
    ram_peak_mb: float
    ram_end_mb: float
    vram_start_mb: float
    vram_peak_mb: float


def _process_ram_mb() -> float:
    return psutil.Process().memory_info().rss / (1024 * 1024)


def _cuda_allocated_mb() -> float:
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 * 1024)
    except ImportError:
        pass
    return 0.0


def _cuda_peak_mb() -> float:
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            return torch.cuda.max_memory_allocated() / (1024 * 1024)
    except ImportError:
        pass
    return 0.0


def _cuda_reset_peak() -> None:
    try:
        import torch  # noqa: PLC0415
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except ImportError:
        pass


class MetricsCollector:
    """Samples RAM on a background thread and reads VRAM peak from CUDA counters.

    Usage::

        with MetricsCollector() as mc:
            run_inference(...)
        snap = mc.snapshot   # MetricsSnapshot with all fields populated
    """

    def __init__(self, sample_interval_s: float = 0.05) -> None:
        self._interval = sample_interval_s
        self._snapshot: MetricsSnapshot | None = None
        self._running = False
        self._peak_ram_mb: float = 0.0
        self._thread: threading.Thread | None = None
        self._t0: float = 0.0
        self._ram_start: float = 0.0
        self._vram_start: float = 0.0

    def __enter__(self) -> MetricsCollector:
        self._ram_start = _process_ram_mb()
        self._vram_start = _cuda_allocated_mb()
        _cuda_reset_peak()
        self._peak_ram_mb = self._ram_start
        self._running = True
        self._t0 = time.perf_counter()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        return self

    def _sample_loop(self) -> None:
        while self._running:
            current = _process_ram_mb()
            if current > self._peak_ram_mb:
                self._peak_ram_mb = current
            time.sleep(self._interval)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

        latency = time.perf_counter() - self._t0
        ram_end = _process_ram_mb()
        if ram_end > self._peak_ram_mb:
            self._peak_ram_mb = ram_end

        self._snapshot = MetricsSnapshot(
            latency_s=latency,
            ram_start_mb=self._ram_start,
            ram_peak_mb=self._peak_ram_mb,
            ram_end_mb=ram_end,
            vram_start_mb=self._vram_start,
            vram_peak_mb=_cuda_peak_mb(),
        )
        return False  # never suppress exceptions

    @property
    def snapshot(self) -> MetricsSnapshot | None:
        return self._snapshot
