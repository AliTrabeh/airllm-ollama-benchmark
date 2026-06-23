"""OllamaService — runs inference via the local Ollama HTTP API."""
from __future__ import annotations

import requests

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.metrics_service import MetricsCollector
from airllm_benchmark.shared.config import load_config
from airllm_benchmark.shared.constants import (
    OLLAMA_BASE_URL,
    OLLAMA_GENERATE_EP,
    OLLAMA_HEALTH_EP,
)
from airllm_benchmark.shared.gatekeeper import NonRetriableError


class OllamaConnectionError(RuntimeError):
    """Ollama server is not reachable."""


class OllamaModelNotFoundError(NonRetriableError):
    """Requested model is not installed locally -- retrying changes nothing."""


class OllamaTimeoutError(RuntimeError):
    """Ollama did not respond within the configured timeout."""


class OllamaResponseError(RuntimeError):
    """Ollama returned a malformed or unexpected response."""


def _cost_estimate(latency_s: float, tdp_w: float = 200.0) -> str:
    """Rough energy estimate: wall-clock time × combined CPU+GPU TDP."""
    kwh = latency_s / 3600 * tdp_w / 1000
    return f"~{kwh:.5f} kWh @ {tdp_w:.0f}W TDP"


class OllamaService:
    """Calls the Ollama /api/generate endpoint and wraps the result in BenchmarkResult."""

    def __init__(self, config: dict | None = None, timeout: float = 120.0) -> None:
        cfg = config if config is not None else load_config()
        self._base_url: str = cfg.get("ollama_url", OLLAMA_BASE_URL).rstrip("/")
        self._timeout = timeout

    def _health_check(self) -> None:
        try:
            requests.get(f"{self._base_url}{OLLAMA_HEALTH_EP}", timeout=5)
        except requests.ConnectionError as exc:
            raise OllamaConnectionError(
                f"Ollama is not running at {self._base_url}. Start it with: ollama serve"
            ) from exc

    def _model_size_gb(self, model: str) -> float:
        try:
            resp = requests.get(f"{self._base_url}{OLLAMA_HEALTH_EP}", timeout=5)
            for m in resp.json().get("models", []):
                if m.get("name") == model:
                    return m.get("size", 0) / (1024**3)
        except (requests.RequestException, ValueError):
            pass
        return 0.0

    def run(self, prompt: str, model: str, max_tokens: int) -> BenchmarkResult:
        self._health_check()

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }

        with MetricsCollector() as mc:
            try:
                resp = requests.post(
                    f"{self._base_url}{OLLAMA_GENERATE_EP}",
                    json=payload,
                    timeout=self._timeout,
                )
            except requests.ConnectionError as exc:
                raise OllamaConnectionError(
                    f"Lost connection to Ollama at {self._base_url}"
                ) from exc
            except requests.Timeout as exc:
                raise OllamaTimeoutError(
                    f"Ollama did not respond within {self._timeout}s at {self._base_url}"
                ) from exc

        if resp.status_code == 404:
            raise OllamaModelNotFoundError(
                f"Model '{model}' not found locally. Run: ollama pull {model}"
            )
        try:
            resp.raise_for_status()
            data = resp.json()
        except (requests.HTTPError, ValueError) as exc:
            raise OllamaResponseError(f"Ollama returned an unexpected response: {exc}") from exc

        snap = mc.snapshot

        tokens_generated: int = data.get("eval_count", 0)
        eval_ns: int = data.get("eval_duration", 0)
        latency_s: float = snap.latency_s

        if eval_ns > 0:
            tps = tokens_generated / eval_ns * 1e9
        elif latency_s > 0 and tokens_generated > 0:
            tps = tokens_generated / latency_s
        else:
            tps = 0.0

        return BenchmarkResult(
            method="ollama",
            model_id=model,
            prompt=prompt,
            output=data.get("response", ""),
            latency_s=latency_s,
            ram_peak_mb=snap.ram_peak_mb,
            vram_peak_mb=snap.vram_peak_mb,
            tokens_generated=tokens_generated,
            tokens_per_second=tps,
            disk_gb=self._model_size_gb(model),
            cost_estimate=_cost_estimate(latency_s),
        )
