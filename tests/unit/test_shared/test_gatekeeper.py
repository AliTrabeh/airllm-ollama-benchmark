"""Tests for ApiGatekeeper."""
from __future__ import annotations

import pytest

from airllm_benchmark.shared.gatekeeper import ApiGatekeeper

_FAST = {"requests_per_minute": 60, "max_retries": 3, "retry_delay_s": 0.0}
_NO_RETRY = {"requests_per_minute": 60, "max_retries": 0, "retry_delay_s": 0.0}


def test_successful_call_returns_value() -> None:
    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    assert gk.call("svc", lambda: 42) == 42


def test_logs_all_calls() -> None:
    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    gk.call("svc", lambda: "a")
    gk.call("svc", lambda: "b")
    assert len(gk.call_log) == 2
    assert all(e["service"] == "svc" for e in gk.call_log)


def test_log_marks_success_true() -> None:
    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    gk.call("svc", lambda: None)
    assert gk.call_log[0]["success"] is True


def test_log_has_timestamp_and_latency() -> None:
    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    gk.call("svc", lambda: None)
    entry = gk.call_log[0]
    assert "timestamp" in entry
    assert "latency_s" in entry
    assert entry["latency_s"] >= 0.0


def test_failed_call_logged_with_error() -> None:
    def boom():
        raise ValueError("boom")

    gk = ApiGatekeeper(rate_limits={"svc": _NO_RETRY})
    with pytest.raises(RuntimeError):
        gk.call("svc", boom)
    assert gk.call_log[0]["success"] is False
    assert "boom" in gk.call_log[0]["error"]


def test_retry_on_transient_failure() -> None:
    attempts: list[int] = []

    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("transient")
        return "ok"

    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    result = gk.call("svc", flaky)
    assert result == "ok"
    assert len(attempts) == 3


def test_all_retries_exhausted_raises() -> None:
    def always_fail():
        raise ConnectionError("always")

    gk = ApiGatekeeper(rate_limits={"svc": {"requests_per_minute": 60, "max_retries": 2, "retry_delay_s": 0.0}})
    with pytest.raises(RuntimeError, match="All 3 attempts"):
        gk.call("svc", always_fail)


def test_retry_logs_each_attempt() -> None:
    def always_fail():
        raise ValueError("x")

    gk = ApiGatekeeper(rate_limits={"svc": {"requests_per_minute": 60, "max_retries": 2, "retry_delay_s": 0.0}})
    with pytest.raises(RuntimeError):
        gk.call("svc", always_fail)
    assert len(gk.call_log) == 3  # initial + 2 retries


def test_rate_limit_from_config_not_hardcoded() -> None:
    """Rate limits must come from the injected config, never hardcoded."""
    gk = ApiGatekeeper(rate_limits={"mysvc": {"requests_per_minute": 120, "max_retries": 1, "retry_delay_s": 0.0}})
    assert gk._get_limit("mysvc")["requests_per_minute"] == 120


def test_unknown_service_falls_back_to_defaults() -> None:
    gk = ApiGatekeeper(rate_limits={})
    limit = gk._get_limit("nonexistent")
    assert "requests_per_minute" in limit
    assert "max_retries" in limit


def test_call_log_is_a_copy() -> None:
    gk = ApiGatekeeper(rate_limits={"svc": _FAST})
    gk.call("svc", lambda: None)
    log = gk.call_log
    log.clear()
    assert len(gk.call_log) == 1  # internal log unaffected
