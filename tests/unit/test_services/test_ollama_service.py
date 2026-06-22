"""Tests for OllamaService."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.services.ollama_service import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaService,
)

_GOOD_RESP = {
    "model": "tinyllama",
    "response": "Hello there!",
    "done": True,
    "eval_count": 5,
    "eval_duration": 500_000_000,  # 0.5 s → 10 tokens/s
}

_CFG = {"ollama_url": "http://localhost:11434"}


def _post_mock(data: dict, status: int = 200) -> MagicMock:
    m = MagicMock()
    m.status_code = status
    m.json.return_value = data
    if status >= 400:
        m.raise_for_status.side_effect = requests.HTTPError(response=m)
    else:
        m.raise_for_status.return_value = None
    return m


def _get_ok() -> MagicMock:
    m = MagicMock()
    m.status_code = 200
    return m


@pytest.fixture
def svc() -> OllamaService:
    return OllamaService(config=_CFG)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_successful_inference_returns_benchmark_result(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    assert isinstance(result, BenchmarkResult)
    assert result.method == "ollama"
    assert result.model_id == "tinyllama"
    assert result.output == "Hello there!"
    assert result.is_success


def test_metrics_captured(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    assert result.latency_s > 0
    assert result.ram_peak_mb > 0
    assert result.tokens_generated == 5


def test_tokens_per_second_from_eval_duration(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    # eval_count=5, eval_duration=500_000_000 ns → 10 tps
    assert result.tokens_per_second == pytest.approx(10.0, abs=0.1)


def test_cost_estimate_populated(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    assert "kWh" in result.cost_estimate
    assert result.cost_estimate != ""


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------

def test_ollama_not_running_raises_connection_error() -> None:
    svc = OllamaService(config=_CFG)
    with patch("requests.get", side_effect=requests.ConnectionError("refused")), \
         pytest.raises(OllamaConnectionError, match="ollama serve"):
        svc.run("Hello", "tinyllama", 20)


def test_model_not_found_raises_with_pull_hint(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock({}, status=404)), \
         pytest.raises(OllamaModelNotFoundError, match="ollama pull"):
        svc.run("Hello", "missing-model", 20)


def test_http_error_propagates(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock({}, status=500)), pytest.raises(requests.HTTPError):
        svc.run("Hello", "tinyllama", 20)


# ---------------------------------------------------------------------------
# Config / URL
# ---------------------------------------------------------------------------

def test_url_comes_from_config_not_hardcoded() -> None:
    svc = OllamaService(config={"ollama_url": "http://myhost:9999"})
    assert "myhost:9999" in svc._base_url


def test_default_url_falls_back_to_constant() -> None:
    svc = OllamaService(config={})
    assert "11434" in svc._base_url


def test_eval_duration_zero_falls_back_to_wall_clock(svc) -> None:
    resp_no_eval = {**_GOOD_RESP, "eval_duration": 0}
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=_post_mock(resp_no_eval)):
        result = svc.run("Hello", "tinyllama", 20)
    assert result.tokens_per_second > 0
