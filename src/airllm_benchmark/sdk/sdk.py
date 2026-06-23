"""BenchmarkSDK — single entry point for all benchmark business logic.

CLI and tests must use this class; no service may be called directly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.models.comparison_report import ComparisonReport
from airllm_benchmark.shared.gatekeeper import ApiGatekeeper


def _validate(prompt: str, max_tokens: int) -> None:
    if not prompt or not prompt.strip():
        raise ValueError("prompt must not be empty")
    if max_tokens <= 0:
        raise ValueError(f"max_tokens must be > 0, got {max_tokens}")


class BenchmarkSDK:
    """Facade over all inference services."""

    def __init__(
        self,
        config: dict | None = None,
        gatekeeper: ApiGatekeeper | None = None,
        ollama_service: Any = None,
        hf_service: Any = None,
        airllm_service: Any = None,
        results_service: Any = None,
    ) -> None:
        if config is None:
            from airllm_benchmark.shared.config import load_config  # noqa: PLC0415
            config = load_config()
        self._config = config
        self._gk = gatekeeper if gatekeeper is not None else ApiGatekeeper()
        self._ollama_svc = ollama_service
        self._hf_svc = hf_service
        self._airllm_svc = airllm_service
        self._results_svc = results_service

    # ------------------------------------------------------------------
    # Service accessors (lazy import so unimplemented services don't crash)
    # ------------------------------------------------------------------

    def _ollama(self) -> Any:
        if self._ollama_svc is not None:
            return self._ollama_svc
        from airllm_benchmark.services.ollama_service import OllamaService  # noqa: PLC0415
        return OllamaService()

    def _hf(self) -> Any:
        if self._hf_svc is not None:
            return self._hf_svc
        from airllm_benchmark.services.hf_baseline_service import HFBaselineService  # noqa: PLC0415
        return HFBaselineService()

    def _airllm(self) -> Any:
        if self._airllm_svc is not None:
            return self._airllm_svc
        from airllm_benchmark.services.airllm_service import AirLLMService  # noqa: PLC0415
        return AirLLMService()

    def _results(self) -> Any:
        if self._results_svc is not None:
            return self._results_svc
        from airllm_benchmark.services.results_service import ResultsService  # noqa: PLC0415
        return ResultsService(config=self._config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_ollama(self, prompt: str, model: str, max_tokens: int) -> BenchmarkResult:
        _validate(prompt, max_tokens)
        svc = self._ollama()
        return self._gk.call("ollama", lambda: svc.run(prompt, model, max_tokens))

    def run_hf_baseline(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
        _validate(prompt, max_tokens)
        svc = self._hf()
        return self._gk.call("huggingface", lambda: svc.run(prompt, model_id, max_tokens))

    def run_airllm(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
        _validate(prompt, max_tokens)
        svc = self._airllm()
        return self._gk.call("airllm", lambda: svc.run(prompt, model_id, max_tokens))

    def compare_results(self, results: list[BenchmarkResult]) -> ComparisonReport:
        return ComparisonReport(results=results)

    def run_all(self, prompt: str, max_tokens: int) -> ComparisonReport:
        _validate(prompt, max_tokens)
        ollama_model = self._config.get("ollama_model", "tinyllama")
        hf_model = self._config.get("model_id", "gpt2")
        airllm_model = self._config.get("airllm_model_id", "gpt2")

        runs: list[tuple[Any, str, str]] = [
            (self.run_ollama, ollama_model, "ollama"),
            (self.run_hf_baseline, hf_model, "hf_baseline"),
            (self.run_airllm, airllm_model, "airllm"),
        ]
        results: list[BenchmarkResult] = []
        for fn, model, method_name in runs:
            try:
                results.append(fn(prompt, model, max_tokens))
            except Exception as exc:
                results.append(
                    BenchmarkResult.error_result(method_name, model, prompt, str(exc))
                )
        return ComparisonReport(results=results)

    def save_result(self, result: BenchmarkResult) -> Path:
        return self._results().save_result(result)

    def save_comparison(self, report: ComparisonReport) -> Path:
        return self._results().save_comparison(report)

    def load_results(self) -> list[BenchmarkResult]:
        svc = self._results()
        return [svc.load_result(p) for p in svc.list_results()]
