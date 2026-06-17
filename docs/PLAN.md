# Technical Plan — airllm-ollama-benchmark

**Source:** software_submission_guidelines-V3 §2.2, §4, §5

---

## Project Goal

Benchmark and compare three LLM inference methods on local hardware:

1. **Ollama** — fast, small model, verifies the full pipeline works
2. **Standard HuggingFace** — normal model loading, establishes GPU/CPU baseline
3. **AirLLM** — virtual-memory paging approach, demonstrates large model on CPU

**Hypothesis:** A model too large to fit in VRAM/RAM normally can run via AirLLM,
at the cost of higher latency. This experiment proves (or disproves) the hypothesis
with real measurements.

---

## Architecture Overview (C4 Level 2)

```
┌─────────────────────────────────────────────────────────┐
│                    External Consumers                     │
│              CLI (main.py) / Notebooks                    │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    SDK Layer                              │
│              src/airllm_benchmark/sdk/sdk.py              │
│  Single entry point for ALL benchmark operations          │
└───────┬──────────────┬──────────────┬───────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────┐   ┌──────────────┐   ┌──────────────────────┐
│ Ollama   │   │ HF Baseline  │   │  AirLLM Runner       │
│ Service  │   │ Service      │   │  Service             │
└──────────┘   └──────────────┘   └──────────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Shared Infrastructure                    │
│  gatekeeper.py │ config.py │ metrics.py │ constants.py   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  External Systems                         │
│  Ollama (localhost:11434) │ HuggingFace Hub │ Disk Cache │
└─────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### src/airllm_benchmark/sdk/sdk.py
Single entry point. Exposes:
- `run_ollama_benchmark(prompt, model, max_tokens) -> BenchmarkResult`
- `run_hf_baseline(prompt, model_id, max_tokens) -> BenchmarkResult`
- `run_airllm_benchmark(prompt, model_id, max_tokens) -> BenchmarkResult`
- `compare_results(results: list[BenchmarkResult]) -> ComparisonReport`

### src/airllm_benchmark/services/
- `ollama_service.py` — calls Ollama API, measures latency and memory
- `hf_baseline_service.py` — loads HF model normally, measures VRAM/RAM
- `airllm_service.py` — uses AirLLM library, measures RAM and latency
- `metrics_service.py` — captures timing, memory, and token counts

### src/airllm_benchmark/shared/
- `gatekeeper.py` — wraps all external calls, rate limiting, retries, logging
- `config.py` — loads config/setup.json and environment variables
- `constants.py` — enums, fixed strings, default values
- `version.py` — project version (starts at 1.00)

### src/airllm_benchmark/models/
- `benchmark_result.py` — dataclass: method, model, latency, ram, vram, tokens, output
- `comparison_report.py` — dataclass: list of results, summary statistics

### src/airllm_benchmark/main.py
CLI entry point. Parses arguments, calls SDK, saves results.

---

## Data Flow

```
User runs CLI
    → main.py parses args
    → SDK.run_*_benchmark(prompt, model, max_tokens)
    → Gatekeeper.execute(service_call)
    → Service runs inference
    → MetricsService captures timing + memory
    → Returns BenchmarkResult
    → Results saved to results/results_<timestamp>.json
    → SDK.compare_results() generates ComparisonReport
    → Report saved to results/report_<timestamp>.json
    → Notebook reads results/ and generates plots
```

---

## Configuration Architecture

Source: software_submission_guidelines-V3 §7.3

```
config/
├── setup.json          # Non-secret settings (model IDs, max_tokens, etc.)
└── rate_limits.json    # Gatekeeper rate limit config

.env                    # Secrets (git-ignored)
.env.example            # Placeholder template (committed)
pyproject.toml          # Build, lint, test, coverage settings
src/.../constants.py    # Immutable defaults
```

No value may be hardcoded in source files. All from `cfg.get()` or `os.environ.get()`.

---

## Test Architecture

Source: software_submission_guidelines-V3 §6

```
tests/
├── conftest.py          # Shared fixtures (mock model, mock Ollama response)
├── unit/
│   ├── test_sdk/
│   │   └── test_sdk.py
│   ├── test_services/
│   │   ├── test_ollama_service.py
│   │   ├── test_hf_baseline_service.py
│   ├── test_shared/
│   │   ├── test_gatekeeper.py
│   │   ├── test_config.py
│   │   └── test_metrics_service.py
│   └── test_models/
│       └── test_benchmark_result.py
└── integration/
    └── test_full_pipeline.py   # Mocked end-to-end
```

**Strategy:** Unit tests use mocks for model loading (no actual download).
Integration tests mock external services. Actual model runs produce results saved to `results/`.

---

## Architecture Decision Records (ADRs)

### ADR-001: Use SDK Pattern
**Decision:** All benchmark logic accessed through sdk.py
**Rationale:** Guidelines §4.1 require SDK layer. Enables testability and extensibility.
**Trade-off:** Slightly more boilerplate but much cleaner separation of concerns.

### ADR-002: Use SafeTensors Models for AirLLM
**Decision:** Select models in SafeTensors format for AirLLM experiments
**Rationale:** AirLLM uses mmap which requires SafeTensors (not pickle-based .bin files).
The lecture (L08-summary §4.3) explicitly states SafeTensors enables mmap loading.
**Trade-off:** Fewer model choices but required for AirLLM to function.

### ADR-003: Use uv for Package Management
**Decision:** All package operations via uv exclusively
**Rationale:** Mandatory per guidelines §8.4. No pip, python -m, or venv allowed.
**Trade-off:** Requires uv installation, but provides reproducible lockfile.

### ADR-004: Mock Model Loading in Unit Tests
**Decision:** Unit tests mock all model loading; actual models only loaded in result runs
**Rationale:** Avoid multi-GB downloads during CI and test runs. Tests verify logic, not models.
**Trade-off:** Integration tests don't catch model API changes, but keeps tests fast.

### ADR-005: Small Model First Strategy
**Decision:** Pipeline verified with a small (1-3B) model before attempting large models
**Rationale:** Assignment tips (L08-summary §9.1) explicitly recommend this approach.
**Trade-off:** Extra step, but prevents wasted time debugging on a slow large model.

---

## Extension Points

How to add a new inference method (e.g., llama.cpp, vLLM):

1. Create `src/airllm_benchmark/services/new_method_service.py`
2. Implement `run(prompt, model_id, max_tokens) -> BenchmarkResult`
3. Add `run_new_method_benchmark()` to `sdk.py`
4. Add config entry in `config/setup.json`
5. Add tests in `tests/unit/test_services/test_new_method_service.py`
6. Update README with new CLI option

No existing files need to be modified except `sdk.py` (add one method).
