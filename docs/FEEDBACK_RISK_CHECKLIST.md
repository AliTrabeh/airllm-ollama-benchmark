# Feedback Risk Checklist

**Source:** Detailed_Feedback_Report_252608 (HW01 feedback, Student 252608)

> These are the exact areas where points were lost in HW01. Each risk maps to a
> concrete action to prevent losing points in HW05.

---

## Critical Risks (Lost Points in HW01)

### RISK-01: No Cost / Resource Analysis
**Feedback Quote:** "There is no evidence of cost or resource awareness in your project.
Any real-world AI application must consider the economic implications of its design choices.
A professional would document and reason about what their solution costs to operate and
how those costs behave as usage scales."

**Source:** Detailed_Feedback_Report_252608 §Costs&Pricing

**Risk Level:** HIGH — explicitly penalized

**Prevention Actions:**
- [x] Create `docs/COSTS.md` with resource breakdown per run
- [x] Measure and record: CPU time (seconds), RAM peak (GB) — `disk_gb` field exists in
      `BenchmarkResult` but is currently always `0.0` (not actually measured); follow-up item
- [x] Include a comparison table: Ollama vs normal HF vs AirLLM resource usage
- [x] Write interpretation: "AirLLM uses ~X GB RAM vs ~Y GB normally, at Z× latency cost"
- [x] Document optimization recommendations

**Acceptance Criteria:**
- [x] Results include numeric resource measurements
- [x] At least one table comparing methods across resource dimensions
- [x] Written paragraph interpreting trade-offs

**Verified 2026-06-22:** `docs/COSTS.md` created with real measured data from `results/*.json`,
comparison table, interpretation, and 4 optimization recommendations. Linked from README.
Outstanding: `disk_gb` is a stub (always 0) — not a blocker for this risk, but worth fixing
in a future pass.

---

### RISK-02: UI/UX Not Communicated
**Feedback Quote:** "The user-facing dimension of your project is not fully communicated.
How someone experiences and interacts with your system — and how you present that
experience — should be a considered part of your submission. Think about how you would
help a reader understand what it looks and feels like to actually use your work, without
having to run it themselves."

**Source:** Detailed_Feedback_Report_252608 §UI/UX

**Risk Level:** HIGH — explicitly penalized

**Prevention Actions:**
- [x] Add "Usage" section in README with exact CLI commands
- [x] Include expected terminal output (copy-paste from actual run)
- [x] Save screenshots or terminal recordings in `assets/`
- [x] Document every CLI mode and flag in README (`### CLI flags reference` table)
- [x] Add a "What to expect" section: "After running X, you will see Y" — done via
      **Expected output** blocks under each method in Usage

**Acceptance Criteria:**
- [x] README has working step-by-step usage examples
- [x] At least one screenshot or terminal output sample in assets/
- [x] A reader can understand what the CLI looks like without running it

**Verified 2026-06-22:** Added `assets/terminal_output_sample.txt` — a real captured run
(`--method ollama --verbose`), not a mock-up. Linked from README Usage section. Confirmed
README's CLI flags table matches the actual argparse definitions in `main.py`.

---

### RISK-03: Configuration Not Professional/Portable
**Feedback Quote:** "Your configuration management is mostly solid, but there are aspects
of how your project handles its environment that could be more professional and portable.
Consider how your project would be set up by someone in a completely different environment
who has never seen your configuration before."

**Source:** Detailed_Feedback_Report_252608 §Configuration&Security

**Risk Level:** MEDIUM-HIGH

**Prevention Actions:**
- [x] `.env.example` with every variable and a comment explaining each
- [x] `config/setup.json` with all non-secret settings
- [x] README explains every environment variable
- [x] README explains every config file
- [ ] Test that a fresh clone with only `.env.example` renamed to `.env` works — **not yet
      tested**; requires a clean clone + `uv sync` + smoke run, deliberately left for a
      separate verification pass rather than assumed
- [x] No hardcoded paths or machine-specific values — **fixed during this review**: a
      prior session change had committed `models_dir: "D:/ai_models"` directly into
      `config/setup.json` (machine-specific). Reverted to the portable default
      `"./models"`; the actual D-drive path now lives only in the local, gitignored `.env`
      via the existing `MODELS_DIR` override.

**Acceptance Criteria:**
- [x] `.env.example` exists and contains all variables
- [x] All config values documented in README
- [x] Zero hardcoded secrets in any source file (confirmed via grep — no API keys/tokens in src/)

**Verified 2026-06-22:** Caught and fixed a real RISK-03 violation (hardcoded `D:/ai_models`
path in committed config). Remaining open item: fresh-clone smoke test not yet performed.

---

### RISK-04: Extensibility Not Demonstrated
**Feedback Quote:** "Your project's design could better support future growth and modification.
Professional software is built with the expectation that requirements will change. Think about
how clearly your architecture separates concerns, and how easily a new developer could extend
your system without disrupting what already works."

**Source:** Detailed_Feedback_Report_252608 §Extensibility

**Risk Level:** MEDIUM

**Prevention Actions:**
- [x] SDK layer clearly separates concerns (sdk.py as single entry point) — docstring on
      `BenchmarkSDK` states "CLI and tests must use this class; no service may be called
      directly"
- [x] Adding a new model/method = adding one service file, not touching SDK substantially
- [x] Document "extension points" in PLAN.md or ARCHITECTURE.md — `docs/PLAN.md` has an
      explicit "Extension Points" section with a numbered how-to
- [x] Use building-block design per guidelines §16

**Acceptance Criteria:**
- [x] SDK architecture enforced (every `run_*` method routes through `ApiGatekeeper.call()`)
- [x] PLAN.md documents how to add a new benchmark runner

**Verified 2026-06-22:** Confirmed `sdk.py` wraps all three service calls through the
gatekeeper, and `PLAN.md` § Extension Points gives a concrete 6-step recipe for adding a
new inference method.

---

### RISK-05: Quality Standards Not Established
**Feedback Quote:** "Your project's approach to maintaining code quality is not clearly
established. Modern professional development relies on automated tooling and processes to
ensure consistency and catch issues early. Think about what mechanisms in your project
enforce quality standards beyond manual review."

**Source:** Detailed_Feedback_Report_252608 §Quality Standards

**Risk Level:** MEDIUM

**Prevention Actions:**
- [x] Ruff configured in pyproject.toml and passes with 0 errors
- [x] pytest configured with coverage ≥ 85%
- [x] pyproject.toml has all tool configs (ruff, pytest, coverage)
- [x] README has "Quality Checks" section with exact commands

**Acceptance Criteria:**
- [x] `uv run ruff check src/` → 0 errors (re-verified live)
- [x] `uv run pytest --cov=src` → ≥ 85% coverage (159 passed, **95.62%** coverage, re-verified live)
- [x] Both commands documented in README

**Verified 2026-06-22:** Re-ran both commands after the CUDA/device changes — fixed a stale
stat in README ("148 tests | 94.96%" → "159 tests | 95.62%").

---

## Areas of Excellence to Maintain (from HW01)

These were praised in HW01 — keep doing them in HW05:

### KEEP-01: Project Planning
"Your project planning demonstrates structured thinking and clear articulation of both the
problem space and the technical approach."
→ **Action:** Keep the PRD + PLAN + TODO structure, maintain it throughout

### KEEP-02: Code Documentation
"Your documentation clearly communicates the purpose, setup, and usage of your project."
→ **Action:** Keep docstrings on every function/class, keep README detailed

### KEEP-03: Testing Quality
"Your testing demonstrates a rigorous approach to validating your implementation across a
meaningful range of scenarios, including edge cases."
→ **Action:** Write tests for each benchmark module, include edge cases

### KEEP-04: Research & Analysis
"Your analytical work clearly documents your experimental process and the insights you
derived from it."
→ **Action:** Document every measurement, include interpretation, not just numbers

### KEEP-05: Version Management
"Your version control and development process documentation reflects disciplined,
professional engineering habits."
→ **Action:** Keep clear commits, use version.py starting at 1.00

---

## Pre-Submission Risk Verification

Run through this list before submitting:

- [x] RISK-01: Cost/resource table exists with real measurements (`docs/COSTS.md`)
- [x] RISK-01: Interpretation paragraph written
- [x] RISK-02: CLI usage examples in README with actual output
- [x] RISK-02: At least one screenshot or terminal sample in assets/ (`terminal_output_sample.txt`)
- [x] RISK-03: `.env.example` has every variable with placeholder
- [x] RISK-03: No secrets or hardcoded values in code (fixed `D:/ai_models` hardcode found
      during this review — see RISK-03 above)
- [x] RISK-04: SDK layer used throughout
- [x] RISK-04: Extension points documented
- [x] RISK-05: `uv run ruff check src/` → 0 errors
- [x] RISK-05: `uv run pytest --cov=src` → ≥ 85% (95.62%)
- [x] KEEP-01: PRD + PLAN + TODO complete and up to date (all 570 PRD files + TODO.md
      now reflect actual DONE state)
- [x] KEEP-02: All modules have docstrings (every file with functions/classes has one;
      the two trivial files without — `constants.py`, `version.py` — contain only
      module-level constants, no functions/classes to document)
- [x] KEEP-03: Tests cover all benchmark scenarios + edge cases (159 tests, 27 explicitly
      named error/empty/invalid/edge-case tests)
- [x] KEEP-04: Results notebook or analysis document with interpretation
      (`notebooks/results_analysis.ipynb`, executed in place, plus `docs/COSTS.md`)
- [x] KEEP-05: Git history shows clean, meaningful commits

**Not yet verified (deliberately left open, not assumed):**
- RISK-03 fresh-clone smoke test (clone → `.env.example` → `.env` → `uv sync` → run)
- `disk_gb` field is a stub (always 0.0) — cosmetic gap in RISK-01's resource measurements
