# PRD-06: SDK Architecture & Gatekeeper

**Source files used:**
- software_submission_guidelines-V3 §4 (SDK architecture), §5 (API Gatekeeper)
- software_submission_guidelines-V3 §2.4 (full project structure)

**Status:** DONE

---

## Goal

Implement the SDK layer as the single entry point for all business logic, and implement
the API Gatekeeper for centralized external call management with rate limits and logging.

---

## Background (from guidelines §4.1)

> "All business logic MUST be accessed through the SDK layer. The SDK is the single entry
> point for all logic — GUI, CLI, REST integrations with third parties and future services."

> "No business logic in GUI or CLI files — they are only view/controller layers."

The SDK enables: testability, extensibility, clear separation of concerns.

---

## Requirements

### SDK Requirements
- `BenchmarkSDK` class in `src/airllm_benchmark/sdk/sdk.py`
- Exposes public methods: `run_ollama`, `run_hf_baseline`, `run_airllm`, `compare_results`
- Internal services called only through SDK, never directly from CLI/tests
- Input validation at SDK boundary (prompt not empty, max_tokens > 0, etc.)

### Gatekeeper Requirements (from guidelines §5.1)
- `ApiGatekeeper` class handles all external calls
- Rate limit check before every call
- Retry on transient failures (configurable max retries)
- FIFO queue when rate limit reached
- Logs ALL calls (method, timestamp, latency, success/fail)
- Rate limits from `config/rate_limits.json` — never hardcoded

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/
├── sdk/
│   ├── __init__.py
│   └── sdk.py                  # BenchmarkSDK class
└── shared/
    ├── gatekeeper.py            # ApiGatekeeper class
    └── config.py                # Config loader (JSON + env vars)

config/
└── rate_limits.json             # {"version":"1.00","services":{...}}

tests/unit/
├── test_sdk/
│   └── test_sdk.py
└── test_shared/
    ├── test_gatekeeper.py
    └── test_config.py
```

---

## SDK Interface

```python
class BenchmarkSDK:
    def run_ollama(self, prompt: str, model: str, max_tokens: int) -> BenchmarkResult: ...
    def run_hf_baseline(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult: ...
    def run_airllm(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult: ...
    def compare_results(self, results: list[BenchmarkResult]) -> ComparisonReport: ...
    def run_all(self, prompt: str, max_tokens: int) -> ComparisonReport: ...
```

---

## Acceptance Criteria

- [ ] `BenchmarkSDK` exists and all 5 methods work
- [ ] `main.py` CLI calls ONLY the SDK — never calls services directly
- [ ] `ApiGatekeeper` rate limits enforced from `rate_limits.json`
- [ ] All external calls logged with timestamp and status
- [ ] SDK validates inputs — empty prompt raises `ValueError`
- [ ] Unit tests mock all services (no real model loading in SDK tests)
- [ ] Test coverage ≥ 85% for `sdk.py` and `gatekeeper.py`

---

## Tests / Checks

- `test_sdk.py`:
  - `test_run_ollama_calls_service()` — mocked service, SDK passes correct args
  - `test_run_all_returns_report()` — all 3 services mocked, report returned
  - `test_empty_prompt_raises()` — ValueError on empty string
  - `test_max_tokens_validation()` — max_tokens ≤ 0 raises ValueError

- `test_gatekeeper.py`:
  - `test_rate_limit_from_config()` — hardcoded rate_limit → test fails
  - `test_retry_on_failure()` — service raises error, gatekeeper retries
  - `test_logs_all_calls()` — verify log entries created

---

## Grading Risks

- No SDK layer → architecture violation, major deduction
- Business logic in main.py → architecture violation
- Direct service calls bypassing Gatekeeper → architecture violation
- Rate limits hardcoded → configuration violation (guidelines §7.2)
