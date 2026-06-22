"""HFBaselineService — standard HuggingFace inference to establish a normal-loading baseline.

Loads the full model into RAM then moves it to the GPU.  For a 7-B fp16 model (~14 GB)
on an 8-GB card this will raise a CUDA OOM, which is caught and returned as an error
BenchmarkResult so metrics (timing, peak RAM) are still recorded.
"""
from __future__ import annotations

import contextlib
import gc

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.metrics_service import MetricsCollector
from airllm_benchmark.shared.config import load_config


def _cost_estimate(latency_s: float, tdp_w: float = 200.0) -> str:
    kwh = latency_s / 3600 * tdp_w / 1000
    return f"~{kwh:.5f} kWh @ {tdp_w:.0f}W TDP"


class HFBaselineService:
    """Loads HuggingFace models the standard (non-paged) way."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config if config is not None else load_config()
        self._device: str = cfg.get("device", "cuda")
        self._cache_dir: str = cfg.get("models_dir", "./models")
        self._hf_token: str = cfg.get("hf_token", "")

    def run(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
        return self._run(prompt, model_id, max_tokens)

    def _run(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:  # noqa: PLR0914
        try:
            import torch  # noqa: PLC0415
            from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "transformers and torch are required: pip install transformers torch"
            ) from exc

        token = self._hf_token or None
        device = self._device
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"

        tokenizer = AutoTokenizer.from_pretrained(
            model_id, cache_dir=self._cache_dir, token=token
        )

        model = None
        output_text = ""
        tokens_generated = 0
        error_msg = ""
        _torch = torch  # keep reference alive for finally block

        with MetricsCollector() as mc:
            try:
                torch_dtype = torch.float16 if device == "cuda" else torch.float32
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    cache_dir=self._cache_dir,
                    token=token,
                    torch_dtype=torch_dtype,
                    low_cpu_mem_usage=True,
                )
                model = model.to(device)  # OOM happens here for large models on GPU
                if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
                    formatted = tokenizer.apply_chat_template(
                        [{"role": "user", "content": prompt}],
                        tokenize=False, add_generation_prompt=True,
                    )
                    inputs = tokenizer(formatted, return_tensors="pt")
                else:
                    inputs = tokenizer(prompt, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}
                out = model.generate(**inputs, max_new_tokens=max_tokens)
                prompt_len = inputs["input_ids"].shape[1]
                tokens_generated = out.shape[1] - prompt_len
                output_text = tokenizer.decode(out[0][prompt_len:], skip_special_tokens=True)
            except (RuntimeError, MemoryError) as exc:
                error_msg = str(exc)
                if self._hf_token:
                    error_msg = error_msg.replace(self._hf_token, "***")
            finally:
                if model is not None:
                    del model
                gc.collect()
                with contextlib.suppress(AttributeError, RuntimeError):
                    _torch.cuda.empty_cache()

        snap = mc.snapshot
        tps = tokens_generated / snap.latency_s if snap.latency_s > 0 and tokens_generated > 0 else 0.0

        if error_msg:
            return BenchmarkResult(
                method="hf_baseline",
                model_id=model_id,
                prompt=prompt,
                latency_s=snap.latency_s,
                ram_peak_mb=snap.ram_peak_mb,
                vram_peak_mb=snap.vram_peak_mb,
                tokens_generated=0,
                tokens_per_second=0.0,
                error=error_msg,
            )

        return BenchmarkResult(
            method="hf_baseline",
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
