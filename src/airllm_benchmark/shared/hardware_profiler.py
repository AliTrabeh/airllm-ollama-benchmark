"""HardwareProfiler — detect CPU/RAM/GPU and recommend a quantization level.

Model sizes are expressed as the model's canonical FP16 size in GB (e.g. a 7B-param
model is ~14 GB at FP16). Other dtypes are derived from FP16 via QUANT_RATIOS, so the
same `model_gb` value can be reused across dtypes without the caller doing the math.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Size of a given dtype relative to FP16 (e.g. q4 is roughly a quarter the size).
QUANT_RATIOS: dict[str, float] = {"fp16": 1.0, "q4": 0.25, "q2": 0.125}
_BYTES_PER_PARAM_FP16 = 2.0


def model_gb_from_name(model_id: str) -> float | None:
    """Estimate a model's FP16 size in GB from a "...7B..." style name, if present."""
    match = re.search(r"(\d+(?:\.\d+)?)[Bb](?![a-zA-Z])", model_id)
    if not match:
        return None
    return float(match.group(1)) * _BYTES_PER_PARAM_FP16


class HardwareProfiler:
    """Detects local hardware and recommends a quantization level for a given model size."""

    def __init__(self, profile_path: str | Path | None = None) -> None:
        self._profile_path = Path(profile_path) if profile_path else None

    def detect_cpu(self) -> dict:
        import psutil  # noqa: PLC0415

        freq = psutil.cpu_freq()
        return {
            "cpu_count": psutil.cpu_count(logical=True) or 0,
            "cpu_freq_mhz": freq.current if freq else 0.0,
        }

    def detect_ram(self) -> dict:
        import psutil  # noqa: PLC0415

        vm = psutil.virtual_memory()
        return {
            "total_gb": vm.total / 1024**3,
            "available_gb": vm.available / 1024**3,
        }

    def detect_gpu(self) -> dict | None:
        try:
            import torch  # noqa: PLC0415
        except ImportError:
            return None
        if not torch.cuda.is_available():
            return None
        props = torch.cuda.get_device_properties(0)
        return {"gpu_name": props.name, "vram_gb": props.total_memory / 1024**3}

    def _profile_from_json(self) -> dict | None:
        if self._profile_path is None or not self._profile_path.exists():
            return None
        data = json.loads(self._profile_path.read_text(encoding="utf-8"))
        target = data.get("target", data)
        return {
            "cpu": {"cpu_count": target.get("cpu_threads", target.get("cpu_cores", 0))},
            "ram": {"total_gb": target.get("ram_gb", 0), "available_gb": target.get("ram_gb", 0)},
            "gpu": (
                {"gpu_name": target.get("gpu", ""), "vram_gb": target.get("vram_gb", 0)}
                if target.get("vram_gb")
                else None
            ),
        }

    def get_profile(self) -> dict:
        return self._profile_from_json() or {
            "cpu": self.detect_cpu(),
            "ram": self.detect_ram(),
            "gpu": self.detect_gpu(),
        }

    def estimate_model_fit(self, model_gb: float, dtype: str = "fp16") -> bool:
        size_gb = model_gb * QUANT_RATIOS.get(dtype, 1.0)
        profile = self.get_profile()
        gpu = profile.get("gpu")
        if gpu and gpu.get("vram_gb"):
            return size_gb <= gpu["vram_gb"]
        ram = profile.get("ram", {})
        return size_gb <= ram.get("available_gb", ram.get("total_gb", 0))

    def recommend_quantization(self, model_gb: float) -> str:
        profile = self.get_profile()
        gpu = profile.get("gpu")
        vram_gb = gpu["vram_gb"] if gpu else 0.0
        for dtype in ("fp16", "q4", "q2"):
            if model_gb * QUANT_RATIOS[dtype] <= vram_gb:
                return dtype
        return "q2"  # best effort: nothing fits, q2 is the smallest we support

    def to_markdown(self) -> str:
        profile = self.get_profile()
        cpu, ram, gpu = profile.get("cpu", {}), profile.get("ram", {}), profile.get("gpu")
        lines = [
            "| Component | Spec |",
            "|-----------|------|",
            f"| CPU | {cpu.get('cpu_count', 'unknown')} logical cores |",
            f"| RAM | {ram.get('total_gb', 0):.1f} GB total, "
            f"{ram.get('available_gb', 0):.1f} GB available |",
        ]
        if gpu:
            lines.append(f"| GPU | {gpu.get('gpu_name', 'unknown')}, {gpu.get('vram_gb', 0):.1f} GB VRAM |")
        else:
            lines.append("| GPU | none detected |")
        return "\n".join(lines)
