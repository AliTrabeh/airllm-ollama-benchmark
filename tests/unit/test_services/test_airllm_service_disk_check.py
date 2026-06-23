"""Tests for AirLLMService._check_disk_space()."""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.airllm_service import AirLLMService

_CFG = {"models_dir": "./models", "hf_token": "", "airllm_max_seq_len": 128}


@pytest.fixture
def svc() -> AirLLMService:
    return AirLLMService(config=_CFG)


def _fake_usage(free_gb: float) -> MagicMock:
    usage = MagicMock()
    usage.free = free_gb * 1024**3
    return usage


def test_warns_when_insufficient_disk_space(svc, caplog) -> None:
    with patch("shutil.disk_usage", return_value=_fake_usage(5.0)), \
         caplog.at_level(logging.WARNING):
        svc._check_disk_space("mistralai/Mistral-7B-v0.1")  # needs ~28 GB (2x14)
    assert any("Mistral-7B" in r.message for r in caplog.records)


def test_silent_when_disk_space_sufficient(svc, caplog) -> None:
    with patch("shutil.disk_usage", return_value=_fake_usage(500.0)), \
         caplog.at_level(logging.WARNING):
        svc._check_disk_space("mistralai/Mistral-7B-v0.1")
    assert caplog.records == []


def test_skips_when_model_name_has_no_size(svc, caplog) -> None:
    with caplog.at_level(logging.WARNING):
        svc._check_disk_space("microsoft/Phi-3-mini-4k-instruct")
    assert caplog.records == []
