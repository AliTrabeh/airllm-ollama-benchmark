"""Tests for OllamaService's Timeout and malformed/non-200-response handling."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from airllm_benchmark.services.ollama_service import (
    OllamaResponseError,
    OllamaService,
    OllamaTimeoutError,
)

_CFG = {"ollama_url": "http://localhost:11434"}


def _get_ok() -> MagicMock:
    m = MagicMock()
    m.status_code = 200
    return m


@pytest.fixture
def svc() -> OllamaService:
    return OllamaService(config=_CFG)


def test_request_timeout_raises_ollama_timeout_error(svc) -> None:
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", side_effect=requests.Timeout("timed out")), \
         pytest.raises(OllamaTimeoutError):
        svc.run("Hello", "tinyllama", 20)


def test_malformed_json_raises_ollama_response_error(svc) -> None:
    bad_resp = MagicMock()
    bad_resp.status_code = 200
    bad_resp.raise_for_status.return_value = None
    bad_resp.json.side_effect = ValueError("not json")
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=bad_resp), \
         pytest.raises(OllamaResponseError):
        svc.run("Hello", "tinyllama", 20)


def test_non_404_http_error_raises_ollama_response_error(svc) -> None:
    bad_resp = MagicMock()
    bad_resp.status_code = 500
    bad_resp.raise_for_status.side_effect = requests.HTTPError("server error")
    with patch("requests.get", return_value=_get_ok()), \
         patch("requests.post", return_value=bad_resp), \
         pytest.raises(OllamaResponseError):
        svc.run("Hello", "tinyllama", 20)
