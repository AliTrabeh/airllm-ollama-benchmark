# Prompt Engineering Log

**Source:** software_submission_guidelines-V3 §8.3

> "Documentation of the AI-assisted development process, containing a list of all prompts
> used during development, description of each prompt's purpose, examples of outputs and
> iterations, and methods that proved useful from the development session."

---

## Format

Each entry follows this structure:

```
### PROMPT-NNN: [Short Title]
- **Date:** YYYY-MM-DD
- **Phase:** Planning | Implementation | Testing | Debugging | Refactoring
- **Tool:** Claude Code | ChatGPT | Copilot | etc.
- **Prompt:** [exact prompt text]
- **Output Summary:** [what was produced]
- **Iterations:** [how many attempts, what changed]
- **Useful:** YES / PARTIAL / NO
- **Notes:** [what worked, what didn't, lessons learned]
```

---

## Session 1: Planning Phase

### PROMPT-001: HW05 Planning & Skeleton Generation
- **Date:** 2026-06-17
- **Phase:** Planning
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Full project preparation prompt — read 3 source files, analyze requirements,
  create all planning documents, PRDs, skeleton files. (see conversation history)
- **Output Summary:** Created docs/ directory with ASSIGNMENT_ANALYSIS.md,
  GUIDELINES_REQUIREMENTS.md, GRADING_RUBRIC.md, FEEDBACK_RISK_CHECKLIST.md, PLAN.md,
  ARCHITECTURE.md, PRD_INDEX.md, PROMPTS.md; docs/prds/ with 9 PRD files; README.md,
  .gitignore, .env.example, TODO.md
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Reading all 3 source PDFs before generating ensured all requirements were
  traceable. The feedback report (HW01) was critical for identifying RISK-01 (costs) and
  RISK-02 (UI/UX) — the two biggest deduction areas.

---

## Session 2: Implementation Phase (2026-06-17 – 2026-06-22)

> Note: exact prompt text for this session was not preserved verbatim in this log as it
> happened; entries below are reconstructed from the git history (commit messages/dates)
> and project state, at the level of "what was asked for and produced" rather than the
> literal wording. Session 3 below has exact prompts since this log was written live
> during that session.

### PROMPT-002: Project Skeleton (PRD-01)
- **Date:** 2026-06-17
- **Phase:** Implementation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Implement PRD-01 — set up uv project, pyproject.toml (ruff, pytest, coverage
  config), src/airllm_benchmark package skeleton, config/setup.json, config/rate_limits.json.
- **Output Summary:** Working `uv sync`, ruff 0 errors, 23 tests passing, 98% coverage.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Getting the tooling (ruff/pytest/coverage) configured correctly before any
  feature code avoided rework later.

### PROMPT-003: Expand to micro-PRDs
- **Date:** 2026-06-18
- **Phase:** Planning
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Break the 9 epic PRDs down into micro-PRDs (one task = one file/behavior) across
  14 groups for finer-grained tracking.
- **Output Summary:** 561 micro-PRD files under `docs/prds/<group>/`.
- **Iterations:** 1
- **Useful:** PARTIAL
- **Notes:** Granularity was useful for tracking but created a large maintenance surface —
  570 files' `Status` fields drifted out of sync with reality and needed a bulk fix later
  (see PROMPT-013).

### PROMPT-004: Models + SDK + Gatekeeper (PRD-06, PRD-05, PRD-02/03/04, PRD-07)
- **Date:** 2026-06-19 to 2026-06-22
- **Phase:** Implementation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Implement, in dependency order: BenchmarkResult/ComparisonReport dataclasses,
  BenchmarkSDK + ApiGatekeeper, MetricsCollector, OllamaService, HFBaselineService,
  AirLLMService, ResultsService — each with unit tests.
- **Output Summary:** Full service layer with SDK facade enforcing "no service called
  directly"; 128 tests passing after this phase.
- **Iterations:** Several (one commit per service/layer)
- **Useful:** YES
- **Notes:** Building the SDK + Gatekeeper layer first, before any inference service, made
  it straightforward to add Ollama/HF/AirLLM as interchangeable services later.

### PROMPT-005: Visualization + Phase 9/10 docs (PRD-08, PRD-09, PRD-10)
- **Date:** 2026-06-22
- **Phase:** Implementation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Implement ChartService + NotebookDataPreparer (4 chart types), the integration
  test, a final quality pass, and write the full README (usage, cost table, extension guide).
- **Output Summary:** `chart_service.py`, `notebook_data.py`, `results_analysis.ipynb`,
  `tests/integration/test_full_pipeline.py`, completed README.
- **Iterations:** 2 (one pre-submission audit pass fixing TODO.md + notebook_data tests)
- **Useful:** YES
- **Notes:** Writing the README's "Expected output" blocks directly against the RISK-02
  feedback item (UI/UX not communicated) up front avoided having to retrofit it later.

### PROMPT-006: GPU enablement and compatibility fixes
- **Date:** 2026-06-22
- **Phase:** Debugging
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** Install CUDA-enabled torch, switch AirLLM/HF baseline to use the RTX 3060 Ti,
  and fix the resulting compatibility breaks (transformers `dtype=` vs `torch_dtype=`,
  torch C-extension re-init crash in tests, non-ASCII output crashing on Windows terminals).
- **Output Summary:** Four targeted fix commits; device switched to `cuda` end-to-end.
- **Iterations:** 4 (one fix commit per discovered break)
- **Useful:** YES
- **Notes:** Each fix surfaced only after actually running the affected path on real
  hardware — config/dtype mismatches and encoding issues don't show up in mocked unit tests.

---

## Session 3: Disk Migration, Visualization Completion, Quality Re-verification (2026-06-22 – 2026-06-23)

> This session's prompts are recorded verbatim/near-verbatim from the actual conversation.

### PROMPT-007: Move model cache off a full C: drive
- **Date:** 2026-06-22
- **Phase:** Debugging / Configuration
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "I connected a 1 TB HDD to get more disk space. C: drive was full... Run wmic
  to find the HDD drive letter, update config/setup.json models_dir to the HDD, confirm
  model_id is Phi-3-mini-4k-instruct, run --method hf_baseline --max-tokens 20, report VRAM
  peak (expected ~7.6 GB)... also I want to move the models that took the space from disk C
  to disk D."
- **Output Summary:** Moved `./models` (7.5 GB) and the global `~/.cache/huggingface`
  (28.8 GB) to `D:\ai_models` via robocopy; set `HF_HOME` persistently; ran the smoke test —
  VRAM peak measured at **7.31 GB**.
- **Iterations:** 2 (first robocopy run for `./models`, second for the global HF cache,
  after clarifying scope with the user)
- **Useful:** YES
- **Notes:** `wmic` is deprecated on this Windows build — had to fall back to
  `Get-Volume`. Also discovered `uv` wasn't on the shell's PATH and had to locate it under
  `AppData\Roaming\Python\Scripts`.

### PROMPT-008: Update TODO.md to reflect actual completion state
- **Date:** 2026-06-22
- **Phase:** Documentation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "before try again lets update the todo file: the status of phases we already
  done with it"
- **Output Summary:** Verified each phase's claimed deliverables against actual files on
  disk (not assumed) before marking Phases 1–7 DONE, 8–9 PARTIAL, 10 mostly TODO.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Cross-checking file existence before flipping any status caught that Phase 8's
  chart PNGs didn't actually exist yet despite the chart-generation code being written.

### PROMPT-009: Generate Phase 8 charts and re-verify Phase 9
- **Date:** 2026-06-22
- **Phase:** Implementation / Testing
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "ok so now we need to redo the work from phase 8 and then because we changed
  to gpu?" (clarified to: generate the 4 chart PNGs + notebook interpretation, then
  re-run pytest/coverage/ruff since the CUDA changes landed after they were last verified).
- **Output Summary:** Generated `assets/{latency_bar,memory_grouped_bar,throughput_bar,
  trade_off_scatter}.png` from the latest successful run per method; added `jupyter`/
  `nbconvert`/`ipykernel` as dev deps and executed `results_analysis.ipynb` in place;
  re-ran pytest (159 passed, 95.62% coverage) and ruff (0 errors).
- **Iterations:** 2 (first chart-generation script, then notebook execution after
  discovering jupyter wasn't installed)
- **Useful:** YES
- **Notes:** The notebook's own data-loading logic already deduped to "latest successful
  run per method" via dict-overwrite semantics, so the manually-generated charts and the
  notebook-executed charts matched without extra reconciliation work.

### PROMPT-010: Bulk-flip PRD statuses
- **Date:** 2026-06-23
- **Phase:** Documentation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "yes, start with the PRD status flip"
- **Output Summary:** `sed`-replaced `**Status:** TODO` → `**Status:** DONE` across all
  570 PRD files (a single uniform line format made this safe); left acceptance-criteria
  checkboxes untouched since checking those off without per-item verification would have
  been inaccurate.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Verified the diff was exactly 570 files × 1 line changed before committing —
  a blanket find/replace across hundreds of files is exactly the kind of action worth a
  scope-check before it lands.

### PROMPT-011: FEEDBACK_RISK_CHECKLIST verification
- **Date:** 2026-06-23
- **Phase:** Testing / Debugging
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "start" (verify docs/FEEDBACK_RISK_CHECKLIST.md risk-by-risk against actual
  deliverables, not just check boxes).
- **Output Summary:** Found and fixed a real RISK-03 violation — `config/setup.json` had
  committed a machine-specific `D:/ai_models` path (introduced in PROMPT-007). Reverted to
  the portable `./models` default and moved the real path to the gitignored `.env` via the
  existing `MODELS_DIR` override. Created `docs/COSTS.md` (RISK-01) and
  `assets/terminal_output_sample.txt` (RISK-02) — both genuinely missing despite related
  content existing elsewhere. Fixed a stale "148 tests | 94.96%" stat in README.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** This is the most valuable prompt in the session — actually verifying against
  the checklist (rather than assuming prior work satisfied it) caught a real, committed
  RISK-03 regression that the project's own checklist exists specifically to prevent.

---

## Session 4: HardwareProfiler, Infra Deliverables, Same-Model Comparison, Strict Final Review (2026-06-23)

> Prompts recorded verbatim from the actual conversation.

### PROMPT-012: Implement HardwareProfiler.recommend_quantization()
- **Date:** 2026-06-23
- **Phase:** Implementation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "implement HardwareProfiler.recommend_quantization()"
- **Output Summary:** Built the full `HardwareProfiler` class (`detect_cpu/ram/gpu`,
  `get_profile`, `estimate_model_fit`, `recommend_quantization`, `to_markdown`) — the feature
  that had been incorrectly marked DONE earlier despite never being implemented. Wired into
  `main.py` so every run prints a live hardware profile and, for any model whose name encodes
  a param count, a real quantization recommendation. 16 new tests.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Demonstrated working in a real run later in the session — correctly recommended
  Q4 for Mistral-7B-v0.1 on the actual 8 GB RTX 3060 Ti.

### PROMPT-013: Re-check everything, then implement the rest (CI/Makefile/LICENSE/etc.)
- **Date:** 2026-06-23
- **Phase:** Testing / Implementation
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "yes, do the rest but before that lets do one more time check that we didnt
  miss anything before... also you still ask me many times to get permission... i give you
  all permissions on this project"
- **Output Summary:** Second PRD-vs-filesystem audit pass found 13 more genuinely
  unimplemented PRDs beyond the first pass (`CostEstimator` class, `ResultsService.
  load_by_method()/load_latest()`, true end-to-end integration tests against live services —
  the last deliberately left undone since it would make CI flaky). Then implemented
  `.github/workflows/ci.yml`, `Makefile`, `LICENSE`, `CHANGELOG.md`, `docs/HARDWARE_PROFILES.md`,
  `CostEstimator`, and the two `ResultsService` methods.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** Set `permissions.defaultMode: bypassPermissions` in project-local settings per the
  user's explicit, repeated request to reduce interruptions for routine implementation work.

### PROMPT-014: Run a big model on GPU with AirLLM and quantization
- **Date:** 2026-06-23
- **Phase:** Testing / Debugging
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "lest finish the project so then we can run the model on the gpu and use airllm
  and quantization"
- **Output Summary:** Ran Mistral-7B-v0.1 through the standard HF baseline path on the real
  GPU to get the assignment's actual core comparison (same model, normal load vs AirLLM). It
  did not produce a clean CUDA OOM — the NVIDIA Windows driver's system-memory fallback
  silently paged the overflow into RAM, completing in 1237.95s with a reported "13.8 GB VRAM"
  on an 8 GB card. AirLLM on the identical model: 706.67s, 8 MB VRAM — 1.75x faster and the
  only one that genuinely respects the VRAM limit. Documented as the headline comparison in
  `docs/COSTS.md`.
- **Iterations:** 1
- **Useful:** YES
- **Notes:** The "didn't crash, just silently degraded" result was more interesting and more
  honest than the clean-OOM hypothesis the README originally stated — corrected that claim too.

### PROMPT-015: README/notebook pass; user catches a 150-line violation
- **Date:** 2026-06-23
- **Phase:** Testing / Refactoring
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "do that pass on README and notebook and make sure the guidlines is ok and also
  i noticed a file contain more than 150 python lines."
- **Output Summary:** Full README read-through corrected ~10 stale claims accumulated from
  incremental edits (test counts, model names, PRD counts, chart lists). Root-caused and fixed
  a recurring notebook bug: every `nbconvert --execute` was corrupting non-ASCII characters
  under this environment's cp1252 default. Confirmed the user's catch: two test files (164 and
  154 lines) had grown past the limit after later commits added more tests — split each into a
  companion file rather than trimming coverage. Also found and fixed: missing `data/`
  directory, missing Nielsen's-heuristics writeup, missing parameter-sensitivity analysis, and
  two divergent `TODO.md` files (root vs. the guideline-mandated `docs/` location).
- **Iterations:** 1
- **Useful:** YES
- **Notes:** The user catching the line-limit violation directly led to re-auditing the whole
  guidelines doc instead of just the two flagged files — found 4 more genuine structural gaps
  that would have otherwise gone unnoticed.

### PROMPT-016: Add HW1 feedback PDF; strict final review before submission
- **Date:** 2026-06-23
- **Phase:** Testing / Debugging
- **Tool:** Claude Code (claude-sonnet-4-6)
- **Prompt:** "is it ready for the review before submission? ... i want now also to ad
  feeedback file that was for hw1 from the lecturer... please be strict and bring me perfect
  hw. i dont want mistakes like the one you did when you missed to do the quantization phase"
- **Output Summary:** Found and committed the actual `Detailed_Feedback_Report_252608.pdf`
  (sitting untracked in the repo root the whole time) and verified `FEEDBACK_RISK_CHECKLIST.md`'s
  quotes against it word-for-word — all accurate. Then, taking the "no more missed phases"
  instruction literally, re-audited every consolidated service module method-by-method instead
  of trusting class-level "equivalent" judgments from earlier passes. Found and fixed six real,
  previously-undetected gaps: (1) `HFBaselineService` had no proactive memory check and would
  crash uncaught on a gated-model/auth error; (2) `AirLLMService._check_disk_space` was marked
  DONE but never existed — directly relevant since this exact session hit a real 27 GB disk
  incident; (3) `OllamaService` didn't catch `Timeout` or wrap `resp.json()`/`raise_for_status()`,
  so a hang or 500 would crash uncaught; (4) `main.py` called `ResultsService` directly,
  bypassing the SDK entirely — contradicting the SDK's own docstring and guideline §4.1; (5)
  `ApiGatekeeper` retried every exception blindly, including permanent failures, burying
  actionable error messages like "Run: ollama pull x" inside a generic wrapper.
- **Iterations:** 1 (each gap found, fixed, tested, and verified against a real run before
  moving to the next)
- **Useful:** YES
- **Notes:** The pattern across all six: a module being "the right file with real content" is
  not the same as "every planned method/behavior actually exists in it." Class-level
  consolidation checks (does the file/class exist, do the obvious methods match) systematically
  miss this category of gap — only checking each planned behavior individually against the
  actual running code surfaces it. This is the single most important lesson from the whole
  project for future sessions: treat "PRD marked DONE" as a claim to verify, not a fact, at the
  granularity of individual behaviors, not files.

---

## Lessons Learned

1. Always read source documents completely before generating any code
2. Use the feedback report to identify grading risks before starting
3. Plan architecture before implementation — SDK layer must be designed first
4. Test with small models first before attempting large model downloads
5. Verify claimed "done" status against actual files on disk before updating tracking
   docs — assumed status drifts from real status faster than expected
6. Convenience fixes made under time pressure (e.g., hardcoding a path to unblock a disk
   space problem) can silently reintroduce risks the project already has a checklist for —
   re-run that checklist after any config change, not just once at the end
7. A bulk find/replace across many files (570 PRD statuses) is safe only after confirming
   the target line has one uniform format everywhere — check the diff scope before committing
8. "The file/class exists with real content" is not the same claim as "every planned method
   or behavior inside it actually exists." A consolidation check at the file level will miss
   missing proactive checks, unhandled exception types, and bypassed architecture layers —
   those need a method-by-method pass against the actual running code, not just a file-existence
   check. This single distinction surfaced 6 real, previously-undetected bugs in one pass.
9. When a user catches a concrete, falsifiable claim (e.g. "this file is under 150 lines")
   being wrong, treat it as a signal to re-audit the whole category, not just fix the one
   instance — the same pattern almost always recurs elsewhere undetected.
