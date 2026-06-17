# PRD-09: Testing & Code Quality

**Source files used:**
- software_submission_guidelines-V3 §6 (TDD), §7.1 (Ruff), §6.2 (85% coverage)
- Detailed_Feedback_Report_252608 §Quality Standards (RISK-05), §Testing Quality (KEEP-03)

**Status:** TODO

---

## Goal

Achieve ≥ 85% test coverage with a TDD approach, 0 Ruff lint errors, and all quality
tooling configured and documented. This is both a grading requirement and a professional
standard explicitly praised in HW01 feedback.

---

## Requirements

### Coverage Requirement (from guidelines §6.2)
- Global coverage ≥ 85%
- Configured via `pyproject.toml` with `fail_under = 85`
- Coverage report generated automatically

### Ruff Linting (from guidelines §7.1)
- Zero errors after `uv run ruff check src/`
- Configured in `pyproject.toml`:
  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py310"

  [tool.ruff.lint]
  select = ["E","F","W","I","N","UP","B","C4","SIM"]
  ignore = ["E501"]
  ```

### TDD Approach (from guidelines §6.1)
- Tests written before or alongside code (not after)
- Red → Green → Refactor cycle
- Every module has a corresponding test file

### File Size Limit (from guidelines §3.2)
- Max 150 lines per code file
- All files checked before submission

---

## Test Plan by Module

| Module | Test File | Key Tests |
|--------|-----------|-----------|
| sdk.py | test_sdk.py | run_ollama, run_hf, run_airllm, compare, validation |
| ollama_service.py | test_ollama_service.py | success, connection_error, model_not_found |
| hf_baseline_service.py | test_hf_baseline_service.py | success, OOM, token_not_logged |
| airllm_service.py | test_airllm_service.py | success, metrics, config_paths |
| metrics_service.py | test_metrics_service.py | timing, ram, no_cuda_graceful |
| results_service.py | test_results_service.py | save_load, comparison, cost_breakdown |
| visualization_service.py | test_visualization_service.py | chart_created, labels_present |
| gatekeeper.py | test_gatekeeper.py | rate_limit, retry, logging |
| config.py | test_config.py | loads_values, missing_token_error |

---

## Files Expected to be Created or Modified

```
pyproject.toml                          # Add coverage config, ruff config, pytest config
tests/
├── conftest.py                         # Shared fixtures: mock_ollama_response, mock_model
├── unit/
│   ├── test_sdk/
│   │   └── test_sdk.py
│   ├── test_services/
│   │   ├── test_ollama_service.py
│   │   ├── test_hf_baseline_service.py
│   │   ├── test_airllm_service.py
│   │   ├── test_metrics_service.py
│   │   ├── test_results_service.py
│   │   └── test_visualization_service.py
│   ├── test_shared/
│   │   ├── test_gatekeeper.py
│   │   └── test_config.py
│   └── test_models/
│       ├── test_benchmark_result.py
│       └── test_comparison_report.py
└── integration/
    └── test_full_pipeline.py           # End-to-end with all mocks
```

---

## pyproject.toml Quality Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=85"

[tool.coverage.run]
source = ["src"]
omit = ["src/airllm_benchmark/main.py", "*/tests/*"]

[tool.coverage.report]
fail_under = 85
```

---

## Acceptance Criteria

- [ ] `uv run ruff check src/` → exit code 0, 0 errors
- [ ] `uv run pytest tests/ --cov=src` → ≥ 85% coverage, all tests pass
- [ ] Every module file has a corresponding test file
- [ ] All files in `src/` are ≤ 150 lines
- [ ] `conftest.py` contains reusable fixtures
- [ ] README documents: `uv run ruff check src/` and `uv run pytest` commands

---

## Tests / Checks (meta-tests: quality of the test suite)

- All test functions have descriptive names (`test_<what>_<when>()`)
- Tests are independent (no shared mutable state)
- External services mocked (no real model loading in unit tests)
- Each test tests ONE behavior

---

## Grading Risks

- Coverage below 85% → automatic fail (guidelines §6.2)
- Ruff errors → quality standards not met (RISK-05 from feedback)
- Tests written after code (not TDD) → visible from git history
- Files over 150 lines → fails file size check (guidelines §3.2)
- No `conftest.py` → duplicate fixture code
- Tests depend on actual models → fail in clean environment
