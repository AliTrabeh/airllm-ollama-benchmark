# TODO — airllm-ollama-benchmark

**Source:** software_submission_guidelines-V3 §2.2 (TODO.md requirements)

Implementation order follows dependency graph. Mark status as work progresses.

---

## Phase 0: Planning & Documentation (DONE — this session)

| Task | File | Status |
|------|------|--------|
| Read all 3 source PDFs | — | DONE |
| Create docs/ASSIGNMENT_ANALYSIS.md | docs/ASSIGNMENT_ANALYSIS.md | DONE |
| Create docs/GUIDELINES_REQUIREMENTS.md | docs/GUIDELINES_REQUIREMENTS.md | DONE |
| Create docs/GRADING_RUBRIC.md | docs/GRADING_RUBRIC.md | DONE |
| Create docs/FEEDBACK_RISK_CHECKLIST.md | docs/FEEDBACK_RISK_CHECKLIST.md | DONE |
| Create docs/PLAN.md | docs/PLAN.md | DONE |
| Create docs/ARCHITECTURE.md | docs/ARCHITECTURE.md | DONE |
| Create docs/PRD_INDEX.md | docs/PRD_INDEX.md | DONE |
| Create docs/PROMPTS.md | docs/PROMPTS.md | DONE |
| Create all 9 PRD files in docs/prds/ | docs/prds/*.md | DONE |
| Create TODO.md (this file) | TODO.md | DONE |
| Create README.md skeleton | README.md | DONE |
| Create .gitignore | .gitignore | DONE |
| Create .env.example | .env.example | DONE |

---

## Phase 1: PRD-01 — Environment Setup (DONE)

| Task | File | Status |
|------|------|--------|
| Create pyproject.toml with uv, ruff, pytest, coverage | pyproject.toml | DONE |
| Initialize uv project (`uv init`) | pyproject.toml, uv.lock | DONE |
| Create src/airllm_benchmark/__init__.py | src/airllm_benchmark/__init__.py | DONE |
| Create src/airllm_benchmark/shared/version.py (1.00) | shared/version.py | DONE |
| Create src/airllm_benchmark/shared/constants.py | shared/constants.py | DONE |
| Create src/airllm_benchmark/shared/config.py | shared/config.py | DONE |
| Create src/airllm_benchmark/main.py (CLI skeleton) | main.py | DONE |
| Create config/setup.json | config/setup.json | DONE |
| Create config/rate_limits.json | config/rate_limits.json | DONE |
| Create tests/conftest.py | tests/conftest.py | DONE |
| Create tests/unit/test_shared/test_config.py | test_config.py | DONE |
| Verify: uv sync works | — | DONE |
| Verify: ruff check src/ → 0 errors | — | DONE |
| Verify: pytest tests/ → passes (159 tests) | — | DONE |

---

## Phase 2: PRD-06 — SDK Architecture & Gatekeeper (DONE)

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/sdk/__init__.py | sdk/__init__.py | DONE |
| Create src/airllm_benchmark/sdk/sdk.py (BenchmarkSDK) | sdk/sdk.py | DONE |
| Create src/airllm_benchmark/shared/gatekeeper.py | gatekeeper.py | DONE |
| Update config/rate_limits.json | rate_limits.json | DONE |
| Write tests/unit/test_sdk/test_sdk.py | test_sdk.py | DONE |
| Write tests/unit/test_shared/test_gatekeeper.py | test_gatekeeper.py | DONE |
| Verify: coverage ≥ 85% for sdk.py + gatekeeper.py | — | DONE |

---

## Phase 3: PRD-05 — Metrics Collection (DONE)

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/models/benchmark_result.py | benchmark_result.py | DONE |
| Create src/airllm_benchmark/models/comparison_report.py | comparison_report.py | DONE |
| Create src/airllm_benchmark/services/metrics_service.py | metrics_service.py | DONE |
| Write tests/unit/test_services/test_metrics_service.py | test_metrics_service.py | DONE |
| Write tests/unit/test_models/test_benchmark_result.py | test_benchmark_result.py | DONE |

---

## Phase 4: PRD-02 — Ollama Baseline (DONE)

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/services/ollama_service.py | ollama_service.py | DONE |
| Update config/setup.json with ollama_url, ollama_model | setup.json | DONE |
| Write tests/unit/test_services/test_ollama_service.py | test_ollama_service.py | DONE |
| Manually verify: ollama pull tiny model + run | — | DONE |
| Record actual results in results/ | results/run_*_ollama.json | DONE |

---

## Phase 5: PRD-03 — HuggingFace Baseline (DONE)

| Task | File | Status |
|------|------|--------|
| Choose models, document in docs/MODEL_SELECTION.md | MODEL_SELECTION.md | DONE |
| Create src/airllm_benchmark/services/hf_baseline_service.py | hf_baseline_service.py | DONE |
| Update config/setup.json with model IDs | setup.json | DONE |
| Write tests/unit/test_services/test_hf_baseline_service.py | test_hf_baseline_service.py | DONE |
| Run small model — verify pipeline works | — | DONE |
| Run large model — demonstrate OOM/slowness | — | DONE |
| Record results | results/run_*_hf_baseline.json | DONE |

---

## Phase 6: PRD-04 — AirLLM Runner (DONE)

| Task | File | Status |
|------|------|--------|
| Add airllm to pyproject.toml dependencies | pyproject.toml | DONE |
| Create src/airllm_benchmark/services/airllm_service.py | airllm_service.py | DONE |
| Update config/setup.json with airllm settings | setup.json | DONE |
| Write tests/unit/test_services/test_airllm_service.py | test_airllm_service.py | DONE |
| Run large model via AirLLM — verify success | — | DONE |
| Record results | results/run_*_airllm.json | DONE |

---

## Phase 7: PRD-07 — Results Storage & Comparison (DONE)

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/services/results_service.py | results_service.py | DONE |
| Create results/.gitkeep | results/.gitkeep | DONE |
| Write tests/unit/test_services/test_results_service.py | test_results_service.py | DONE |
| Generate comparison report from all runs | results/comparison_*.json | DONE |
| Verify cost_breakdown populated | — | DONE |

---

## Phase 8: PRD-08 — Visualization (DONE)

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/visualization/chart_service.py | chart_service.py | DONE |
| Create src/airllm_benchmark/visualization/notebook_data.py | notebook_data.py | DONE |
| Create notebooks/results_analysis.ipynb | results_analysis.ipynb | DONE |
| Generate Chart 1: Latency comparison | assets/latency_bar.png | DONE |
| Generate Chart 2: Memory comparison | assets/memory_grouped_bar.png | DONE |
| Generate Chart 3: Throughput comparison | assets/throughput_bar.png | DONE |
| Generate Chart 4: Trade-off scatter | assets/trade_off_scatter.png | DONE |
| Write interpretation sections in notebook | results_analysis.ipynb | DONE (data-driven conclusions cell, executed in place) |
| Add screenshots to README | README.md | DONE (assets/*.png is git-ignored by design; README documents filenames + regen command instead of embedding) |

---

## Phase 9: PRD-09 — Testing & Quality (DONE)

| Task | File | Status |
|------|------|--------|
| Write integration test | tests/integration/test_full_pipeline.py | DONE |
| Run full test suite: uv run pytest --cov=src | — | DONE (159 tests pass, re-verified post-GPU changes) |
| Fix any coverage gaps to reach ≥ 85% | — | DONE (95.62% total coverage) |
| Run ruff: uv run ruff check src/ | — | DONE (re-verified post-GPU changes) |
| Fix any lint errors | — | DONE (0 errors) |
| Verify all files ≤ 150 lines | — | DONE (max 120 lines) |

---

## Phase 10: Final Submission Preparation

| Task | File | Status |
|------|------|--------|
| Complete README.md (all sections) | README.md | DONE (terminal sample + COSTS.md linked, stale test-count stat fixed) |
| Update PROMPTS.md with all AI prompts used | PROMPTS.md | DONE (Session 2 reconstructed from git history; Session 3 recorded verbatim from this conversation) |
| Update PRD statuses to DONE | docs/prds/*.md | PARTIAL — 17 files genuinely TODO, see note below |
| Run FEEDBACK_RISK_CHECKLIST.md verification | — | DONE (caught + fixed a real RISK-03 hardcoded-path violation; created docs/COSTS.md and assets/terminal_output_sample.txt; fresh-clone smoke test verified) |
| Verify .env not committed | — | DONE (gitignored, untracked) |
| Verify uv.lock committed | — | DONE |
| Final git commit with clean history | — | DONE (working tree clean, all changes landed in scoped commits) |

**Correction (2026-06-23):** The initial bulk PRD flip (570 files) was verified against only a
sample of groups, not every group. A systematic check (every PRD's `Target file:` against the
actual filesystem) found **48 files across 4 groups genuinely never implemented** — reverted
back to `TODO`:

- **`13_hardware` (23 files)** — an entire `HardwareProfiler` class was planned (CPU/RAM/GPU
  detection, `estimate_model_fit()`, **`recommend_quantization(model_gb) -> 'fp16'|'q4'|'q2'`**)
  and never built. This is the actual answer to "where was quantization" — it was *planned* as
  a hardware-aware recommendation feature, not as something applied to any benchmark run. The
  only quantization in the project today is incidental: Ollama's `llama3.2:3b` ships pre-quantized
  (Q4_K_M GGUF) by Ollama itself, not by any code in this repo.
  **Update (2026-06-23): implemented.** `src/airllm_benchmark/shared/hardware_profiler.py` now
  exists (`detect_cpu/ram/gpu`, `get_profile`, `estimate_model_fit`, `recommend_quantization`,
  `to_markdown`), with 16 tests (`tests/unit/test_shared/test_hardware_profiler.py`). Wired into
  `main.py`: every run prints a live hardware profile, plus a quantization recommendation for
  any configured model whose name encodes a param count (e.g. `Mistral-7B-v0.1` → "recommend q4").
  This 23-file group is back to `DONE`; `docs/HARDWARE_PROFILES.md` (group `12_docs`, separate
  scope) remains `TODO`.
- **`11_quality` (14 files) + `00_infrastructure` (4 files)** — GitHub Actions CI workflow
  and Makefile. **Update (2026-06-23): implemented.** `.github/workflows/ci.yml` (checkout,
  setup-python 3.11, install uv, `uv sync --all-groups`, ruff, pytest+coverage, upload coverage
  artifact) and `Makefile` (lint/test/run-ollama/run-hf/run-airllm/run-all/clean targets, tab
  indentation verified) both now exist. Back to `DONE`.
- **`12_docs` (7 files)** — `docs/HARDWARE_PROFILES.md`, `LICENSE` (MIT), `CHANGELOG.md`.
  **Update (2026-06-23): implemented.** All three created — `HARDWARE_PROFILES.md` documents the
  *actual* hardware used (i7-4790K, matching `config/hardware_profiles.json`) rather than the
  stale i7-2700K the original PRD text named, plus the AirLLM-vs-HF-baseline analysis. Back to `DONE`.

**Second pass (2026-06-23):** Re-verified every "missing target file" hit individually rather
than assuming rename = equivalent. Most were legitimate consolidations (e.g. planned
`hf_service.py` → actual `hf_baseline_service.py`, same class, equivalent tests — kept `DONE`).
Three more genuine gaps were found; two are now fixed, one deliberately left open:

- **`CostEstimator` class (06_metrics, 13 files: 014-020, 033-039)** — was never built; only a
  duplicated inline formula existed. **Fixed:** `src/airllm_benchmark/metrics/cost_estimator.py`
  now exists (hardware-profile-aware, `estimate_cpu_cost`/`estimate_gpu_cost`/
  `estimate_combined_cost`/`kwh_from_tdp`/`format_cost_string`), with 7 tests. Deliberately
  produces a bare USD string (`"$0.000123"`) rather than replacing the existing
  `"~X kWh @ YW TDP"` format used throughout `BenchmarkResult.cost_estimate` — switching that
  established, tested, documented format now would be disruptive for no real benefit. The
  per-service `_cost_estimate()` duplication therefore still exists by choice, not oversight.
  Back to `DONE`.
- **`ResultsStorage.load_by_method()` / `load_latest()` (08_storage, 5 files: 010, 011, 023-025)**
  — **Fixed:** both methods added to `ResultsService`, with 4 new tests. Back to `DONE`.
- **True end-to-end integration tests against live services (16 files: 03_ollama 042-049,
  04_hf_baseline 043-045, 05_airllm 043-047)** — what exists (`test_full_pipeline.py`)
  integration-tests the SDK→ResultsService→ChartService wiring with all three services *mocked*.
  **Deliberately left as `TODO`**, not fixed: adding real Ollama calls / multi-GB HF downloads /
  AirLLM runs to the automated test suite would make the just-added CI pipeline slow, flaky, and
  dependent on a locally-running Ollama daemon + GPU — directly counter to why CI exists. The
  mocked integration test is the correct trade-off here.
- **`models/.gitkeep` (00_044)** — reverted for honesty (file doesn't exist, models/ moved
  off-repo to a configurable drive), though this one is a non-issue in practice: the directory
  is created on demand by whichever downloader writes to it.

Everything else in the 570-file flip was checked against the filesystem: the remaining "missing
target file" hits are legitimate consolidations (`metrics/metrics_collector.py` →
`services/metrics_service.py`, same `MetricsCollector` class; `storage/report_generator.py` →
methods on `ComparisonReport` instead of a separate class — verified the planned methods
`generate_markdown_table`/`generate_cost_section`/`generate_recommendations`/`generate_full_report`
all have equivalents). Those remain `DONE` — same functionality, different file layout than the
original micro-PRD plan. This second pass spot-checked the highest-risk consolidation claims
rather than re-deriving all ~570 files line-by-line; if something else turns up missing later,
treat it the same way — verify against the filesystem before trusting a `DONE` status.

**Third pass (2026-06-23):** Re-verified the `04_hf_baseline` consolidation claim
(`hf_service.py` → `hf_baseline_service.py`) method-by-method instead of trusting the earlier
"equivalent class" judgment. Found two PRDs that were marked `DONE` by that consolidation
decision while the actual described behavior did not exist:

- **PRD-04-005 / PRD-04-047 (`_check_memory_before_load`)** — no proactive memory check existed
  at all; the service only reacted to OOM after attempting to load. **Fixed:** added
  `HFBaselineService._check_memory_before_load()`, using the already-built `HardwareProfiler`
  + a new shared `model_gb_from_name()` helper (moved out of `main.py`, which had its own
  private copy — now both share one implementation). Logs a `logging.warning` when a model's
  estimated size exceeds available RAM/VRAM for the resolved device.
- **PRD-04-014 / PRD-04-015 (missing-token / 404 errors)** — confirmed via `huggingface_hub`'s
  actual exception hierarchy that `GatedRepoError`/`RepositoryNotFoundError` subclass `OSError`,
  not `RuntimeError`/`MemoryError` — the only exceptions the service caught. A gated-model or
  invalid-model-id run would have crashed uncaught instead of returning a clean
  `BenchmarkResult.error`. **Fixed:** `HFBaselineService.run()` now wraps `_run()` in a top-level
  `except OSError`, matching the pattern `AirLLMService.run()` already used correctly. Token is
  sanitized from the error message; a missing-token hint is added when the failure looks
  auth-related.

Both are now genuinely covered, with real tests (`test_hf_baseline_service_robustness.py`) —
not just inherited from the original `test_hf_baseline_service.py`. 200 tests passing, 96.28%
coverage. This confirms the second pass's own caveat: a "legitimate consolidation" verdict at
the class level does not guarantee every individual planned behavior survived the consolidation
— each one needs checking, not just the file/class mapping.
