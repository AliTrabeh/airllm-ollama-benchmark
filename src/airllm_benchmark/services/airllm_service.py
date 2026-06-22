"""AirLLMService — layer-paged CPU inference for models larger than available VRAM.

AirLLM memory-maps SafeTensors model files via mmap so only the layer currently
being processed is resident in physical RAM.  This lets a 7-B model (~14 GB) run
on a machine with far less RAM/VRAM — at the cost of high latency (I/O-bound).
"""
from __future__ import annotations

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.metrics_service import MetricsCollector
from airllm_benchmark.shared.config import load_config


def _cost_estimate(latency_s: float, tdp_w: float = 65.0) -> str:
    """CPU-only TDP estimate (no GPU used in layer-paging mode)."""
    kwh = latency_s / 3600 * tdp_w / 1000
    return f"~{kwh:.5f} kWh @ {tdp_w:.0f}W TDP"


class AirLLMService:
    """Runs inference via AirLLM layer-by-layer paging on CPU."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config if config is not None else load_config()
        self._cache_dir: str = cfg.get("models_dir", "./models")
        self._hf_token: str = cfg.get("hf_token", "")
        self._max_seq_len: int = int(cfg.get("airllm_max_seq_len", 128))

    def run(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
        try:
            return self._run(prompt, model_id, max_tokens)
        except (FileNotFoundError, OSError) as exc:
            return BenchmarkResult.error_result(
                "airllm", model_id, prompt,
                f"Model file not found or disk error: {exc}",
            )

    def _run(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
        try:
            import torch  # noqa: PLC0415
            from airllm import AutoModel  # noqa: PLC0415
            from transformers import AutoTokenizer  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "airllm and transformers are required: pip install airllm transformers"
            ) from exc

        token = self._hf_token or None
        tokenizer = AutoTokenizer.from_pretrained(
            model_id, cache_dir=self._cache_dir, token=token
        )
        # device='cpu' required when torch has no CUDA build; float32 avoids fp16 instability on CPU
        model = AutoModel.from_pretrained(
            model_id,
            max_seq_len=self._max_seq_len,
            device="cpu",
            dtype=torch.float32,
        )

        with MetricsCollector() as mc:
            input_tokens = tokenizer(
                [prompt],
                return_tensors="pt",
                return_attention_mask=False,
                truncation=True,
                max_length=self._max_seq_len,
                padding=False,
            )
            # Layer paging happens inside generate() — one layer at a time, CPU-only
            out = model.generate(
                input_tokens["input_ids"],
                max_new_tokens=max_tokens,
            )
            output_text = tokenizer.decode(out[0].tolist(), skip_special_tokens=True)

        snap = mc.snapshot
        prompt_len = input_tokens["input_ids"].shape[1]
        tokens_generated = max(0, len(out[0].tolist()) - prompt_len)
        tps = tokens_generated / snap.latency_s if snap.latency_s > 0 and tokens_generated > 0 else 0.0

        return BenchmarkResult(
            method="airllm",
            model_id=model_id,
            prompt=prompt,
            output=output_text,
            latency_s=snap.latency_s,
            ram_peak_mb=snap.ram_peak_mb,
            vram_peak_mb=snap.vram_peak_mb,
            tokens_generated=tokens_generated,
            tokens_per_second=tps,
            cost_estimate=_cost_estimate(snap.latency_s),
        )
