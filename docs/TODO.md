# TODO — airllm-ollama-benchmark

**Source:** software_submission_guidelines-V3 §2.2

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| PRD-01 | Environment & Project Skeleton | DONE |
| PRD-02 | Ollama Baseline Runner | DONE |
| PRD-03 | HuggingFace Model Selection & Baseline | DONE |
| PRD-04 | AirLLM CPU Runner | DONE |
| PRD-05 | Metrics Collection Service | DONE |
| PRD-06 | SDK Architecture & Gatekeeper | DONE |
| PRD-07 | Results Storage & Comparison Report | DONE |
| PRD-08 | Visualization & Results Analysis | DONE |
| PRD-09 | Testing & Code Quality | DONE |
| PRD-10 | README & Submission Docs | DONE |

---

## Implementation Tasks

### Infrastructure (PRD-01) — DONE
- [x] pyproject.toml with uv, ruff, pytest, coverage configured
- [x] .env.example with all variables and comments
- [x] .gitignore covering secrets, models, results, assets
- [x] config/setup.json with all non-secret settings
- [x] config/rate_limits.json for API Gatekeeper
- [x] GitHub Actions CI (lint + test)
- [x] Python 3.11 pinned in .python-version

### Models (PRD-02) — DONE
- [x] BenchmarkResult dataclass with all fields + to_dict/from_dict
- [x] ComparisonReport dataclass with summary_table, recommendations, to_markdown

### Services (PRD-02 through PRD-05) — DONE
- [x] OllamaService — HTTP client, health check, MetricsCollector, error types
- [x] HFBaselineService — lazy torch/transformers import, OOM handling, GPU→CPU fallback
- [x] AirLLMService — CPU-only mmap layer paging, 65W TDP cost estimate
- [x] MetricsCollector — background thread RAM polling + torch VRAM peak

### SDK & Gatekeeper (PRD-06) — DONE
- [x] BenchmarkSDK — single entry point, dependency injection, run_all
- [x] ApiGatekeeper — sliding-window rate limit, retry + delay, per-call logging

### Results Storage (PRD-07) — DONE
- [x] ResultsService — save/load BenchmarkResult and ComparisonReport as JSON
- [x] Timestamped filenames: run_<ts>_<method>.json, comparison_<ts>.json

### Visualization (PRD-08) — DONE
- [x] ChartService — 4 chart types (latency bar, memory grouped bar, throughput bar, scatter)
- [x] NotebookDataPreparer — pandas DataFrame builder, hardware profile summary
- [x] notebooks/results_analysis.ipynb — 8-section notebook

### CLI (PRD-10) — DONE
- [x] main.py — parse_args, dispatch to SDK, save results, print summary

### Testing (PRD-09) — DONE
- [x] 148 unit + integration tests
- [x] 94.96% coverage (≥ 85% required)
- [x] ruff 0 errors
- [x] All source files ≤ 150 lines
- [x] Integration test: full SDK → ResultsService → ChartService pipeline

### Documentation (PRD-10) — DONE
- [x] README.md — complete with usage, config, cost table, extension guide
- [x] docs/PLAN.md — C4 architecture, ADRs
- [x] docs/ARCHITECTURE.md — detailed architecture
- [x] docs/MODEL_SELECTION.md — model choice rationale
- [x] docs/PRD_INDEX.md — links to all epic PRDs
- [x] docs/prds/PRD_01 through PRD_09 — epic PRD files
- [x] docs/PROMPTS.md — AI prompt engineering log
- [x] docs/FEEDBACK_RISK_CHECKLIST.md — risk mitigation from HW01 feedback

---

## Post-Implementation (run manually)

- [ ] Start Ollama: `ollama serve` + `ollama pull tinyllama`
- [ ] Install ML deps: `uv sync --group ml`
- [ ] Run benchmark: `uv run airllm-benchmark --method all`
- [ ] Verify charts saved to assets/
- [ ] Commit results + charts
- [ ] Take terminal screenshot for assets/

---

## Definition of Done

A phase is DONE when:
1. All code is implemented and passes ruff check
2. All tests for that phase pass
3. Coverage remains ≥ 85%
4. No file exceeds 150 lines
5. Committed to git with a descriptive commit message
