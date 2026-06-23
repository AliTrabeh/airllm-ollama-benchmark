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
| Update PRD statuses to DONE | docs/prds/*.md | PARTIAL — 25 files genuinely TODO, see note below |
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
  (`.github/workflows/ci.yml`) and a `Makefile` with lint/test/run targets — neither exists.
- **`12_docs` (7 files)** — `docs/HARDWARE_PROFILES.md`, `LICENSE` (MIT), `CHANGELOG.md` — none exist.

Everything else in the 570-file flip was checked against the filesystem too: most "missing
target file" hits were PRDs pointing at stale planned filenames that got consolidated/renamed
during implementation (e.g. planned `hf_service.py` → actual `hf_baseline_service.py`; planned
`metrics/metrics_collector.py` + `metrics/cost_estimator.py` → consolidated into
`services/metrics_service.py`; planned per-method integration test files → consolidated into
`tests/integration/test_full_pipeline.py`). Those are legitimately DONE — same functionality,
different file layout than the original micro-PRD plan.
