"""Unit tests for ChartService — matplotlib mocked except test_generate_all_files_exist."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as _np
import pytest

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.visualization.chart_service import ChartService


def _r(method, latency=1.0, ram=500.0, vram=100.0, tps=10.0, error="") -> BenchmarkResult:
    return BenchmarkResult(method=method, model_id="test/model", prompt="hello",
                           latency_s=latency, ram_peak_mb=ram, vram_peak_mb=vram,
                           tokens_generated=10, tokens_per_second=tps, error=error)


def _three() -> list[BenchmarkResult]:
    return [_r("ollama", 1.0, 400.0, 200.0, 20.0),
            _r("hf_baseline", 2.5, 800.0, 400.0, 8.0),
            _r("airllm", 5.0, 1200.0, 0.0, 3.0)]


def _mock_mpl(tmp_path: Path) -> dict:
    plt = MagicMock()
    fig, ax = MagicMock(), MagicMock()
    plt.subplots.return_value = (fig, ax)
    def _save(path, **kw):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).touch()
    fig.savefig.side_effect = _save
    mpl = MagicMock()
    mpl.pyplot = plt
    np = MagicMock()
    np.arange.side_effect = _np.arange
    return {"matplotlib": mpl, "matplotlib.pyplot": plt, "numpy": np}


def test_ensure_dir_creates_directory(tmp_path: Path) -> None:
    target = tmp_path / "charts"
    ChartService(config={"assets_dir": str(target)})._ensure_dir()
    assert target.is_dir()


def test_prepare_latency_data_extracts_correct_values() -> None:
    data = ChartService(config={"assets_dir": "."})._prepare_latency_data(_three())
    assert data == {"ollama": 1.0, "hf_baseline": 2.5, "airllm": 5.0}


def test_prepare_latency_data_excludes_failed() -> None:
    data = ChartService(config={"assets_dir": "."})._prepare_latency_data(
        [_r("ollama"), _r("airllm", error="OOM")])
    assert "ollama" in data and "airllm" not in data


def test_prepare_memory_data_extracts_ram_and_vram() -> None:
    data = ChartService(config={"assets_dir": "."})._prepare_memory_data([_r("ollama", ram=500.0, vram=200.0)])
    assert data == {"ollama": {"ram": 500.0, "vram": 200.0}}


@pytest.mark.parametrize("method,name", [
    ("plot_latency_bar",        "latency_bar.png"),
    ("plot_memory_grouped_bar", "memory_grouped_bar.png"),
    ("plot_throughput_bar",     "throughput_bar.png"),
    ("plot_trade_off_scatter",  "trade_off_scatter.png"),
])
def test_plot_method_returns_named_png(method: str, name: str, tmp_path: Path) -> None:
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, _mock_mpl(tmp_path)):
        assert getattr(svc, method)(_three()).name == name


def test_generate_all_charts_returns_4_paths(tmp_path: Path) -> None:
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, _mock_mpl(tmp_path)):
        assert len(svc.generate_all_charts(_three())) == 4


def test_generate_all_charts_all_files_exist(tmp_path: Path) -> None:
    paths = ChartService(config={"assets_dir": str(tmp_path)}).generate_all_charts(_three())
    assert len(paths) == 4 and all(p.exists() for p in paths)


def test_save_chart_returns_path_to_png(tmp_path: Path) -> None:
    result = ChartService(config={"assets_dir": str(tmp_path)})._save_chart(MagicMock(), "my_chart")
    assert isinstance(result, Path) and result.name == "my_chart.png"


def test_color_scheme_has_all_three_methods() -> None:
    assert {"ollama", "hf_baseline", "airllm"}.issubset(ChartService.COLOR_SCHEME)


def test_chartservice_uses_config_assets_dir(tmp_path: Path) -> None:
    assert ChartService(config={"assets_dir": str(tmp_path)})._assets_dir == tmp_path
