"""Tests for OllamaService's disk-size lookup via the /api/tags endpoint."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from airllm_benchmark.services.ollama_service import OllamaService

_GOOD_RESP = {
    "model": "tinyllama",
    "response": "Hello there!",
    "done": True,
    "eval_count": 5,
    "eval_duration": 500_000_000,
}

_CFG = {"ollama_url": "http://localhost:11434"}


def _post_mock(data: dict, status: int = 200) -> MagicMock:
    m = MagicMock()
    m.status_code = status
    m.json.return_value = data
    m.raise_for_status.return_value = None
    return m


def _get_ok() -> MagicMock:
    m = MagicMock()
    m.status_code = 200
    return m


@pytest.fixture
def svc() -> OllamaService:
    return OllamaService(config=_CFG)


def test_disk_gb_populated_from_tags_endpoint(svc) -> None:
    tags_resp = _get_ok()
    tags_resp.json.return_value = {
        "models": [{"name": "tinyllama", "size": 2 * 1024**3}]
    }
    with patch("requests.get", return_value=tags_resp), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    assert result.disk_gb == pytest.approx(2.0)


def test_disk_gb_zero_when_tags_endpoint_fails(svc) -> None:
    with patch("requests.get", side_effect=[_get_ok(), requests.RequestException("boom")]), \
         patch("requests.post", return_value=_post_mock(_GOOD_RESP)):
        result = svc.run("Hello", "tinyllama", 20)
    assert result.disk_gb == 0.0
