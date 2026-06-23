"""Tests for HardwareProfiler."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from airllm_benchmark.shared.hardware_profiler import HardwareProfiler


def test_detect_cpu_returns_dict_with_cpu_count() -> None:
    result = HardwareProfiler().detect_cpu()
    assert isinstance(result["cpu_count"], int)
    assert result["cpu_count"] > 0


def test_detect_ram_returns_positive_total_gb() -> None:
    result = HardwareProfiler().detect_ram()
    assert result["total_gb"] > 0


def test_detect_gpu_returns_none_when_no_gpu() -> None:
    fake_torch = MagicMock()
    fake_torch.cuda.is_available.return_value = False
    with patch.dict("sys.modules", {"torch": fake_torch}):
        assert HardwareProfiler().detect_gpu() is None


def test_detect_gpu_returns_dict_when_gpu_present() -> None:
    fake_torch = MagicMock()
    fake_torch.cuda.is_available.return_value = True
    props = MagicMock(name="RTX 3060 Ti", total_memory=8 * 1024**3)
    props.name = "RTX 3060 Ti"
    fake_torch.cuda.get_device_properties.return_value = props
    with patch.dict("sys.modules", {"torch": fake_torch}):
        result = HardwareProfiler().detect_gpu()
    assert result == {"gpu_name": "RTX 3060 Ti", "vram_gb": 8.0}


def test_get_profile_returns_dict_with_cpu_ram_gpu_keys() -> None:
    profile = HardwareProfiler().get_profile()
    assert set(profile.keys()) == {"cpu", "ram", "gpu"}


def test_get_profile_loads_from_json_when_path_provided(tmp_path: Path) -> None:
    profile_file = tmp_path / "hardware_profiles.json"
    profile_file.write_text(
        json.dumps({"target": {"cpu_threads": 8, "ram_gb": 32, "gpu": "RTX 3060 Ti", "vram_gb": 8}}),
        encoding="utf-8",
    )
    profile = HardwareProfiler(profile_path=profile_file).get_profile()
    assert profile["cpu"]["cpu_count"] == 8
    assert profile["ram"]["total_gb"] == 32
    assert profile["gpu"]["vram_gb"] == 8


def test_estimate_model_fit_7b_fp16_does_not_fit_8gb_vram(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32, "vram_gb": 8}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.estimate_model_fit(14, "fp16") is False


def test_estimate_model_fit_7b_q4_fits_8gb_vram(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32, "vram_gb": 8}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.estimate_model_fit(14, "q4") is True


def test_estimate_model_fit_falls_back_to_ram_when_no_gpu(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.estimate_model_fit(14, "fp16") is True


def test_recommend_quantization_fp16_when_model_fits_as_is(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32, "vram_gb": 8}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.recommend_quantization(6) == "fp16"


def test_recommend_quantization_q4_when_fp16_too_big(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32, "vram_gb": 8}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.recommend_quantization(14) == "q4"


def test_recommend_quantization_q2_when_q4_still_too_big(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32, "vram_gb": 8}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.recommend_quantization(40) == "q2"


def test_recommend_quantization_no_gpu_defaults_to_q2(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32}}), encoding="utf-8")
    profiler = HardwareProfiler(profile_path=profile_file)
    assert profiler.recommend_quantization(6) == "q2"


def test_to_markdown_contains_cpu_row() -> None:
    assert "CPU" in HardwareProfiler().to_markdown()


def test_to_markdown_contains_ram_row() -> None:
    assert "RAM" in HardwareProfiler().to_markdown()


def test_to_markdown_contains_gpu_row_when_no_gpu(tmp_path: Path) -> None:
    profile_file = tmp_path / "hw.json"
    profile_file.write_text(json.dumps({"target": {"ram_gb": 32}}), encoding="utf-8")
    md = HardwareProfiler(profile_path=profile_file).to_markdown()
    assert "GPU" in md
    assert "none detected" in md
