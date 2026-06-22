"""Unit tests for ChartService — all matplotlib calls mocked except test_10."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as _np  # used only to make a real ndarray for the mock

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.visualization.chart_service import ChartService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _result(
    method: str,
    latency: float = 1.0,
    ram: float = 500.0,
    vram: float = 100.0,
    tps: float = 10.0,
    error: str = "",
) -> BenchmarkResult:
    return BenchmarkResult(
        method=method,
        model_id="test/model",
        prompt="hello",
        latency_s=latency,
        ram_peak_mb=ram,
        vram_peak_mb=vram,
        tokens_generated=10,
        tokens_per_second=tps,
        error=error,
    )


def _three_results() -> list[BenchmarkResult]:
    return [
        _result("ollama", latency=1.0, ram=400.0, vram=200.0, tps=20.0),
        _result("hf_baseline", latency=2.5, ram=800.0, vram=400.0, tps=8.0),
        _result("airllm", latency=5.0, ram=1200.0, vram=0.0, tps=3.0),
    ]


def _make_mocked_plt_modules(tmp_path: Path):
    """Return a sys.modules patch dict that intercepts matplotlib imports.

    fig.savefig touches the target path so _save_chart returns a real Path.
    """
    mock_plt = MagicMock()
    fig = MagicMock()
    ax = MagicMock()
    mock_plt.subplots.return_value = (fig, ax)

    def fake_savefig(path, **kwargs):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).touch()

    fig.savefig.side_effect = fake_savefig

    mock_mpl = MagicMock()
    mock_mpl.pyplot = mock_plt

    mock_np = MagicMock()
    # Return a real ndarray so arithmetic (x - width/2) works in the method body.
    mock_np.arange.side_effect = _np.arange

    return {
        "matplotlib": mock_mpl,
        "matplotlib.pyplot": mock_plt,
        "numpy": mock_np,
    }


# ---------------------------------------------------------------------------
# Test 1 — _ensure_dir creates directory
# ---------------------------------------------------------------------------


def test_ensure_dir_creates_directory(tmp_path: Path) -> None:
    target = tmp_path / "charts"
    svc = ChartService(config={"assets_dir": str(target)})
    assert not target.exists()
    svc._ensure_dir()
    assert target.is_dir()


# ---------------------------------------------------------------------------
# Test 2 — _prepare_latency_data extracts correct values
# ---------------------------------------------------------------------------


def test_prepare_latency_data_extracts_correct_values() -> None:
    results = _three_results()
    svc = ChartService(config={"assets_dir": "./assets"})
    data = svc._prepare_latency_data(results)
    assert data == {"ollama": 1.0, "hf_baseline": 2.5, "airllm": 5.0}


# ---------------------------------------------------------------------------
# Test 3 — _prepare_latency_data excludes failed results
# ---------------------------------------------------------------------------


def test_prepare_latency_data_excludes_failed() -> None:
    results = [
        _result("ollama", latency=1.0),
        _result("airllm", latency=5.0, error="OOM"),
    ]
    svc = ChartService(config={"assets_dir": "./assets"})
    data = svc._prepare_latency_data(results)
    assert "ollama" in data
    assert "airllm" not in data


# ---------------------------------------------------------------------------
# Test 4 — _prepare_memory_data extracts ram and vram
# ---------------------------------------------------------------------------


def test_prepare_memory_data_extracts_ram_and_vram() -> None:
    results = [_result("ollama", ram=500.0, vram=200.0)]
    svc = ChartService(config={"assets_dir": "./assets"})
    data = svc._prepare_memory_data(results)
    assert data == {"ollama": {"ram": 500.0, "vram": 200.0}}


# ---------------------------------------------------------------------------
# Tests 5-8 — plot_* methods return correct filename (mocked matplotlib)
# ---------------------------------------------------------------------------


def test_plot_latency_bar_creates_png_file(tmp_path: Path) -> None:
    mods = _make_mocked_plt_modules(tmp_path)
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, mods):
        path = svc.plot_latency_bar(_three_results())
    assert path.name == "latency_bar.png"


def test_plot_memory_grouped_bar_creates_png_file(tmp_path: Path) -> None:
    mods = _make_mocked_plt_modules(tmp_path)
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, mods):
        path = svc.plot_memory_grouped_bar(_three_results())
    assert path.name == "memory_grouped_bar.png"


def test_plot_throughput_bar_creates_png_file(tmp_path: Path) -> None:
    mods = _make_mocked_plt_modules(tmp_path)
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, mods):
        path = svc.plot_throughput_bar(_three_results())
    assert path.name == "throughput_bar.png"


def test_plot_trade_off_scatter_creates_png_file(tmp_path: Path) -> None:
    mods = _make_mocked_plt_modules(tmp_path)
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, mods):
        path = svc.plot_trade_off_scatter(_three_results())
    assert path.name == "trade_off_scatter.png"


# ---------------------------------------------------------------------------
# Test 9 — generate_all_charts returns exactly 4 paths (mocked)
# ---------------------------------------------------------------------------


def test_generate_all_charts_returns_4_paths(tmp_path: Path) -> None:
    mods = _make_mocked_plt_modules(tmp_path)
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    with patch.dict(sys.modules, mods):
        paths = svc.generate_all_charts(_three_results())
    assert len(paths) == 4


# ---------------------------------------------------------------------------
# Test 10 — generate_all_charts all files exist (REAL matplotlib write)
# ---------------------------------------------------------------------------


def test_generate_all_charts_all_files_exist(tmp_path: Path) -> None:
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    paths = svc.generate_all_charts(_three_results())
    assert len(paths) == 4
    for p in paths:
        assert p.exists(), f"Expected file at {p}"


# ---------------------------------------------------------------------------
# Test 11 — _save_chart returns a Path with .png suffix
# ---------------------------------------------------------------------------


def test_save_chart_returns_path_to_png(tmp_path: Path) -> None:
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    fig = MagicMock()
    fig.savefig.return_value = None
    result = svc._save_chart(fig, "my_chart")
    assert isinstance(result, Path)
    assert result.suffix == ".png"
    assert result.name == "my_chart.png"


# ---------------------------------------------------------------------------
# Test 12 — COLOR_SCHEME has all three methods
# ---------------------------------------------------------------------------


def test_color_scheme_has_all_three_methods() -> None:
    keys = set(ChartService.COLOR_SCHEME.keys())
    assert {"ollama", "hf_baseline", "airllm"}.issubset(keys)


# ---------------------------------------------------------------------------
# Test 13 — ChartService uses config assets_dir
# ---------------------------------------------------------------------------


def test_chartservice_uses_config_assets_dir(tmp_path: Path) -> None:
    svc = ChartService(config={"assets_dir": str(tmp_path)})
    assert svc._assets_dir == tmp_path
