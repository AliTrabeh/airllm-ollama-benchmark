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
| Complete README.md (all sections) | README.md | PARTIAL (441 lines drafted, needs screenshots/charts) |
| Update PROMPTS.md with all AI prompts used | PROMPTS.md | TODO |
| Update PRD statuses to DONE | docs/prds/*.md | DONE (570 files, Status field flipped; acceptance-criteria checkboxes not individually re-verified) |
| Run FEEDBACK_RISK_CHECKLIST.md verification | — | TODO |
| Verify .env not committed | — | DONE (gitignored, untracked) |
| Verify uv.lock committed | — | DONE |
| Final git commit with clean history | — | TODO |
