"""Tests for HFBaselineService's memory-check warning and gated-repo error handling."""
from __future__ import annotations

import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from airllm_benchmark.services.hf_baseline_service import HFBaselineService

_CFG = {"device": "cpu", "models_dir": "./models", "hf_token": ""}


@pytest.fixture
def svc() -> HFBaselineService:
    return HFBaselineService(config=_CFG)


# ---------------------------------------------------------------------------
# Gated-repo / auth errors (OSError subclasses) -> graceful error, not a crash
# ---------------------------------------------------------------------------

def test_gated_repo_error_returns_error_result_not_crash(svc) -> None:
    tf = MagicMock()
    tf.AutoTokenizer.from_pretrained.side_effect = OSError("401 Client Error: gated repo")
    torch_m = MagicMock()
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", "meta-llama/some-gated-model", 5)
    assert not result.is_success
    assert "HF_TOKEN" in result.error


def test_token_sanitized_when_present_on_os_error() -> None:
    secret = "hf_super_secret_abc123"
    tf = MagicMock()
    tf.AutoTokenizer.from_pretrained.side_effect = OSError(f"403 Forbidden, token={secret}")
    torch_m = MagicMock()
    svc = HFBaselineService(config={**_CFG, "hf_token": secret})
    with patch.dict(sys.modules, {"transformers": tf, "torch": torch_m}):
        result = svc.run("Hello", "org/model", 5)
    assert secret not in result.error


# ---------------------------------------------------------------------------
# Proactive memory check
# ---------------------------------------------------------------------------

def test_check_memory_warns_when_model_exceeds_available_ram(svc, caplog) -> None:
    fake_profile = {"ram": {"available_gb": 1.0}, "gpu": None}
    with patch(
        "airllm_benchmark.services.hf_baseline_service.HardwareProfiler.get_profile",
        return_value=fake_profile,
    ), caplog.at_level(logging.WARNING):
        svc._check_memory_before_load("mistralai/Mistral-7B-v0.1", "cpu")
    assert any("Mistral-7B" in r.message for r in caplog.records)


def test_check_memory_silent_when_model_fits(svc, caplog) -> None:
    fake_profile = {"ram": {"available_gb": 64.0}, "gpu": None}
    with patch(
        "airllm_benchmark.services.hf_baseline_service.HardwareProfiler.get_profile",
        return_value=fake_profile,
    ), caplog.at_level(logging.WARNING):
        svc._check_memory_before_load("mistralai/Mistral-7B-v0.1", "cpu")
    assert caplog.records == []


def test_check_memory_skips_when_model_name_has_no_size(svc, caplog) -> None:
    with caplog.at_level(logging.WARNING):
        svc._check_memory_before_load("microsoft/Phi-3-mini-4k-instruct", "cuda")
    assert caplog.records == []
