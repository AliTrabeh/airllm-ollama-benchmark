# Grading Rubric

**Source:** software_submission_guidelines-V3 (Table 5, §19.1) + L08-summary §9

---

## Quick Reference: Code Quality Standards Table

From software_submission_guidelines-V3 §19.1 (Table 5):

| Dimension | Check | Target |
|-----------|-------|--------|
| Code scan | SDK architecture | All logic through SDK layer |
| Code scan | OOP / no duplication | Mixins, no copy-paste |
| Code scan + tests | API Gatekeeper | All external calls via Gatekeeper |
| Config check | Rate limits from config | Config files, not in code |
| Integration check | Queue management | No direct calls under load |
| Version module | Starting version | Begins at 1.00 |
| Workflow | TDD | Red-Green-Refactor visible |
| Automated check | File size | ≤ 150 lines per file |
| Linter | Ruff errors | 0 errors |
| Coverage | pytest --cov | ≥ 85% |
| Code scan | Hardcoded values | 0 in source |
| Security scan | Secrets | .env-example + 0 secrets in code |
| Build check | Package manager | Everything via `uv` |

---

## HW05 Specific Grading Dimensions

### Dimension 1: Functional Correctness
Source: L08-summary §9.1

| Criterion | Evidence Required |
|-----------|------------------|
| Ollama runs a model successfully | Screenshot / log output showing successful inference |
| Large model fails or is too slow normally | Log showing OOM error or extreme latency |
| AirLLM runs the large model on CPU | Log showing successful completion with AirLLM |
| Measurements captured for all three | Results CSV / JSON with timestamps and memory readings |

### Dimension 2: Research Quality
Source: software_submission_guidelines-V3 §9, §17.5

| Criterion | Evidence Required |
|-----------|------------------|
| Response time measured for all scenarios | Numeric values in results |
| Memory consumption measured | RAM and VRAM readings per run |
| Comparison table exists | Table with CPU vs GPU vs AirLLM |
| Visualization with clear labels | Charts saved in results/ or assets/ |
| Interpretation provided | Written analysis, not just numbers |

### Dimension 3: Software Engineering Quality
Source: software_submission_guidelines-V3 §17

| Criterion | Evidence Required |
|-----------|------------------|
| SDK architecture followed | `src/<pkg>/sdk/sdk.py` exists and is used |
| Ruff passes with 0 errors | `uv run ruff check src/` output clean |
| Test coverage ≥ 85% | `uv run pytest --cov` report |
| pyproject.toml present | File exists with all tool configs |
| uv.lock committed | File in repo |
| No hardcoded secrets | Code review + .env-example |

### Dimension 4: Documentation
Source: software_submission_guidelines-V3 §17.1

| Criterion | Evidence Required |
|-----------|------------------|
| README.md complete | Install + run instructions work |
| PRD.md exists | docs/PRD.md (or docs/prds/ structure) |
| PLAN.md exists | docs/PLAN.md with architecture |
| Per-mechanism PRDs | docs/prds/*.md files |
| Prompt engineering log | docs/PROMPTS.md with entries |

### Dimension 5: Cost & Resource Analysis
Source: software_submission_guidelines-V3 §11 + Feedback §Costs&Pricing

| Criterion | Evidence Required |
|-----------|------------------|
| Resource usage documented | CPU time, RAM, disk space per run |
| Cost breakdown table | Comparison table with estimates |
| Optimization recommendations | Written section on AirLLM trade-offs |

### Dimension 6: UI/UX Documentation
Source: software_submission_guidelines-V3 §10 + Feedback §UI/UX

| Criterion | Evidence Required |
|-----------|------------------|
| User workflow described | Step-by-step in README |
| Screenshots / output samples | In assets/ or docs/ |
| CLI experience documented | Example commands with expected output |

### Dimension 7: Configuration & Security
Source: software_submission_guidelines-V3 §7.4 + Feedback §Configuration&Security

| Criterion | Evidence Required |
|-----------|------------------|
| .env.example present | File with placeholder values only |
| No tokens in code | Code review |
| HF_TOKEN loaded from env | `os.environ.get("HF_TOKEN")` pattern |
| .gitignore covers .env | .gitignore file |

---

## Grading Risks Summary

See `docs/FEEDBACK_RISK_CHECKLIST.md` for detailed risk items derived from
previous assignment feedback.

---

## What an Excellent Submission Looks Like

Based on software_submission_guidelines-V3 §19:

1. **Documentation first** — PRD, PLAN, and all PRDs approved before any coding
2. **Tests written with code** — not after
3. **Architecture visible** — SDK layer enforced, gatekeeper used
4. **Results reproducible** — anyone can clone and run with their own HF_TOKEN
5. **Numbers interpreted** — analysis explains WHY AirLLM is slower and WHEN it's worth it
6. **Screenshots/output** — grader doesn't need to run it to understand what happened
7. **Costs quantified** — even rough estimates show professional awareness
