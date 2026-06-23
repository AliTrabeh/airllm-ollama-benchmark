"""ApiGatekeeper — centralized external call management with rate limits and logging."""
from __future__ import annotations

import json
import logging
import time
from collections import deque
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_RATE_LIMITS_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "config" / "rate_limits.json"
)

logger = logging.getLogger(__name__)


class NonRetriableError(RuntimeError):
    """Raised by a service when retrying the identical call could never succeed.

    ApiGatekeeper.call() re-raises these immediately, with their original message
    intact, instead of burning through max_retries attempts and burying the
    actionable message (e.g. "Run: ollama pull <model>") inside a generic
    "All N attempts failed" wrapper.
    """


def _load_rate_limits() -> dict:
    if _RATE_LIMITS_PATH.exists():
        data = json.loads(_RATE_LIMITS_PATH.read_text(encoding="utf-8"))
        return data.get("services", data)
    return {}


class ApiGatekeeper:
    """Rate-limited, retrying, logging wrapper for all external service calls."""

    def __init__(self, rate_limits: dict | None = None) -> None:
        self._limits = rate_limits if rate_limits is not None else _load_rate_limits()
        self._call_times: dict[str, deque[float]] = {}
        self._log: list[dict] = []

    def _get_limit(self, service: str) -> dict:
        return self._limits.get(
            service,
            {"requests_per_minute": 60, "max_retries": 3, "retry_delay_s": 1.0},
        )

    def _check_rate_limit(self, service: str) -> None:
        rpm: int = self._get_limit(service).get("requests_per_minute", 60)
        if service not in self._call_times:
            self._call_times[service] = deque()

        now = time.monotonic()
        times = self._call_times[service]
        # Evict entries older than 60 s
        while times and now - times[0] > 60.0:
            times.popleft()

        if len(times) >= rpm:
            wait = 60.0 - (now - times[0])
            if wait > 0:
                time.sleep(wait)

        self._call_times[service].append(time.monotonic())

    def call(self, service: str, fn: Callable[[], Any]) -> Any:
        """Execute fn under rate limiting with retry and logging."""
        limit = self._get_limit(service)
        max_retries: int = limit.get("max_retries", 3)
        retry_delay: float = limit.get("retry_delay_s", 1.0)

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            self._check_rate_limit(service)
            t0 = time.perf_counter()
            entry: dict = {
                "service": service,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "attempt": attempt,
            }
            try:
                result = fn()
                entry["latency_s"] = time.perf_counter() - t0
                entry["success"] = True
                self._log.append(entry)
                logger.debug("gatekeeper: %s OK in %.3fs", service, entry["latency_s"])
                return result
            except (NonRetriableError, ImportError):
                # ImportError (missing torch/transformers/airllm) is just as
                # non-transient as a NonRetriableError -- retrying installs nothing.
                entry["latency_s"] = time.perf_counter() - t0
                entry["success"] = False
                self._log.append(entry)
                raise
            except Exception as exc:
                entry["latency_s"] = time.perf_counter() - t0
                entry["success"] = False
                entry["error"] = str(exc)
                self._log.append(entry)
                last_exc = exc
                logger.warning("gatekeeper: %s attempt %d failed: %s", service, attempt, exc)
                if attempt < max_retries:
                    time.sleep(retry_delay)

        raise RuntimeError(
            f"All {max_retries + 1} attempts for '{service}' failed"
        ) from last_exc

    @property
    def call_log(self) -> list[dict]:
        return list(self._log)
