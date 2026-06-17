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

## Phase 1: PRD-01 — Environment Setup

| Task | File | Status |
|------|------|--------|
| Create pyproject.toml with uv, ruff, pytest, coverage | pyproject.toml | TODO |
| Initialize uv project (`uv init`) | pyproject.toml, uv.lock | TODO |
| Create src/airllm_benchmark/__init__.py | src/airllm_benchmark/__init__.py | TODO |
| Create src/airllm_benchmark/shared/version.py (1.00) | shared/version.py | TODO |
| Create src/airllm_benchmark/shared/constants.py | shared/constants.py | TODO |
| Create src/airllm_benchmark/shared/config.py | shared/config.py | TODO |
| Create src/airllm_benchmark/main.py (CLI skeleton) | main.py | TODO |
| Create config/setup.json | config/setup.json | TODO |
| Create config/rate_limits.json | config/rate_limits.json | TODO |
| Create tests/conftest.py | tests/conftest.py | TODO |
| Create tests/unit/test_shared/test_config.py | test_config.py | TODO |
| Verify: uv sync works | — | TODO |
| Verify: ruff check src/ → 0 errors | — | TODO |
| Verify: pytest tests/ → passes | — | TODO |

---

## Phase 2: PRD-06 — SDK Architecture & Gatekeeper

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/sdk/__init__.py | sdk/__init__.py | TODO |
| Create src/airllm_benchmark/sdk/sdk.py (BenchmarkSDK) | sdk/sdk.py | TODO |
| Create src/airllm_benchmark/shared/gatekeeper.py | gatekeeper.py | TODO |
| Update config/rate_limits.json | rate_limits.json | TODO |
| Write tests/unit/test_sdk/test_sdk.py | test_sdk.py | TODO |
| Write tests/unit/test_shared/test_gatekeeper.py | test_gatekeeper.py | TODO |
| Verify: coverage ≥ 85% for sdk.py + gatekeeper.py | — | TODO |

---

## Phase 3: PRD-05 — Metrics Collection

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/models/benchmark_result.py | benchmark_result.py | TODO |
| Create src/airllm_benchmark/models/comparison_report.py | comparison_report.py | TODO |
| Create src/airllm_benchmark/services/metrics_service.py | metrics_service.py | TODO |
| Write tests/unit/test_services/test_metrics_service.py | test_metrics_service.py | TODO |
| Write tests/unit/test_models/test_benchmark_result.py | test_benchmark_result.py | TODO |

---

## Phase 4: PRD-02 — Ollama Baseline

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/services/ollama_service.py | ollama_service.py | TODO |
| Update config/setup.json with ollama_url, ollama_model | setup.json | TODO |
| Write tests/unit/test_services/test_ollama_service.py | test_ollama_service.py | TODO |
| Manually verify: ollama pull tiny model + run | — | TODO |
| Record actual results in results/ | results/ | TODO |

---

## Phase 5: PRD-03 — HuggingFace Baseline

| Task | File | Status |
|------|------|--------|
| Choose models, document in docs/MODEL_SELECTION.md | MODEL_SELECTION.md | TODO |
| Create src/airllm_benchmark/services/hf_baseline_service.py | hf_baseline_service.py | TODO |
| Update config/setup.json with model IDs | setup.json | TODO |
| Write tests/unit/test_services/test_hf_baseline_service.py | test_hf_baseline_service.py | TODO |
| Run small model — verify pipeline works | — | TODO |
| Run large model — demonstrate OOM/slowness | — | TODO |
| Record results | results/ | TODO |

---

## Phase 6: PRD-04 — AirLLM Runner

| Task | File | Status |
|------|------|--------|
| Add airllm to pyproject.toml dependencies | pyproject.toml | TODO |
| Create src/airllm_benchmark/services/airllm_service.py | airllm_service.py | TODO |
| Update config/setup.json with airllm settings | setup.json | TODO |
| Write tests/unit/test_services/test_airllm_service.py | test_airllm_service.py | TODO |
| Run large model via AirLLM — verify success | — | TODO |
| Record results | results/ | TODO |

---

## Phase 7: PRD-07 — Results Storage & Comparison

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/services/results_service.py | results_service.py | TODO |
| Create results/.gitkeep | results/.gitkeep | TODO |
| Write tests/unit/test_services/test_results_service.py | test_results_service.py | TODO |
| Generate comparison report from all runs | results/comparison_*.json | TODO |
| Verify cost_breakdown populated | — | TODO |

---

## Phase 8: PRD-08 — Visualization

| Task | File | Status |
|------|------|--------|
| Create src/airllm_benchmark/services/visualization_service.py | visualization_service.py | TODO |
| Create notebooks/results_analysis.ipynb | results_analysis.ipynb | TODO |
| Generate Chart 1: Latency comparison | assets/chart_latency.png | TODO |
| Generate Chart 2: Memory comparison | assets/chart_memory.png | TODO |
| Generate Chart 3: Throughput comparison | assets/chart_throughput.png | TODO |
| Generate Chart 4: Trade-off scatter | assets/chart_tradeoff.png | TODO |
| Write interpretation sections in notebook | results_analysis.ipynb | TODO |
| Add screenshots to README | README.md | TODO |

---

## Phase 9: PRD-09 — Testing & Quality

| Task | File | Status |
|------|------|--------|
| Write integration test | tests/integration/test_full_pipeline.py | TODO |
| Run full test suite: uv run pytest --cov=src | — | TODO |
| Fix any coverage gaps to reach ≥ 85% | — | TODO |
| Run ruff: uv run ruff check src/ | — | TODO |
| Fix any lint errors | — | TODO |
| Verify all files ≤ 150 lines | — | TODO |

---

## Phase 10: Final Submission Preparation

| Task | File | Status |
|------|------|--------|
| Complete README.md (all sections) | README.md | TODO |
| Update PROMPTS.md with all AI prompts used | PROMPTS.md | TODO |
| Update PRD statuses to DONE | docs/prds/*.md | TODO |
| Run FEEDBACK_RISK_CHECKLIST.md verification | — | TODO |
| Verify .env not committed | — | TODO |
| Verify uv.lock committed | — | TODO |
| Final git commit with clean history | — | TODO |
