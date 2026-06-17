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
- [ ] Create `docs/COSTS.md` with resource breakdown per run
- [ ] Measure and record: CPU time (seconds), RAM peak (GB), disk used (GB)
- [ ] Include a comparison table: Ollama vs normal HF vs AirLLM resource usage
- [ ] Write interpretation: "AirLLM uses ~X GB RAM vs ~Y GB normally, at Z× latency cost"
- [ ] Document optimization recommendations

**Acceptance Criteria:**
- Results include numeric resource measurements
- At least one table comparing methods across resource dimensions
- Written paragraph interpreting trade-offs

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
- [ ] Add "Usage" section in README with exact CLI commands
- [ ] Include expected terminal output (copy-paste from actual run)
- [ ] Save screenshots or terminal recordings in `assets/`
- [ ] Document every CLI mode and flag in README
- [ ] Add a "What to expect" section: "After running X, you will see Y"

**Acceptance Criteria:**
- README has working step-by-step usage examples
- At least one screenshot or terminal output sample in assets/
- A reader can understand what the CLI looks like without running it

---

### RISK-03: Configuration Not Professional/Portable
**Feedback Quote:** "Your configuration management is mostly solid, but there are aspects
of how your project handles its environment that could be more professional and portable.
Consider how your project would be set up by someone in a completely different environment
who has never seen your configuration before."

**Source:** Detailed_Feedback_Report_252608 §Configuration&Security

**Risk Level:** MEDIUM-HIGH

**Prevention Actions:**
- [ ] `.env.example` with every variable and a comment explaining each
- [ ] `config/setup.json` with all non-secret settings
- [ ] README explains every environment variable
- [ ] README explains every config file
- [ ] Test that a fresh clone with only `.env.example` renamed to `.env` works
- [ ] No hardcoded paths or machine-specific values

**Acceptance Criteria:**
- `.env.example` exists and contains all variables
- All config values documented in README
- Zero hardcoded secrets in any source file

---

### RISK-04: Extensibility Not Demonstrated
**Feedback Quote:** "Your project's design could better support future growth and modification.
Professional software is built with the expectation that requirements will change. Think about
how clearly your architecture separates concerns, and how easily a new developer could extend
your system without disrupting what already works."

**Source:** Detailed_Feedback_Report_252608 §Extensibility

**Risk Level:** MEDIUM

**Prevention Actions:**
- [ ] SDK layer clearly separates concerns (sdk.py as single entry point)
- [ ] Adding a new model/method = adding one service file, not touching SDK
- [ ] Document "extension points" in PLAN.md or ARCHITECTURE.md
- [ ] Use building-block design per guidelines §16

**Acceptance Criteria:**
- SDK architecture enforced
- PLAN.md documents how to add a new benchmark runner

---

### RISK-05: Quality Standards Not Established
**Feedback Quote:** "Your project's approach to maintaining code quality is not clearly
established. Modern professional development relies on automated tooling and processes to
ensure consistency and catch issues early. Think about what mechanisms in your project
enforce quality standards beyond manual review."

**Source:** Detailed_Feedback_Report_252608 §Quality Standards

**Risk Level:** MEDIUM

**Prevention Actions:**
- [ ] Ruff configured in pyproject.toml and passes with 0 errors
- [ ] pytest configured with coverage ≥ 85%
- [ ] pyproject.toml has all tool configs (ruff, pytest, coverage)
- [ ] README has "Quality Checks" section with exact commands

**Acceptance Criteria:**
- `uv run ruff check src/` → 0 errors
- `uv run pytest --cov=src` → ≥ 85% coverage
- Both commands documented in README

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

- [ ] RISK-01: Cost/resource table exists with real measurements
- [ ] RISK-01: Interpretation paragraph written
- [ ] RISK-02: CLI usage examples in README with actual output
- [ ] RISK-02: At least one screenshot or terminal sample in assets/
- [ ] RISK-03: `.env.example` has every variable with placeholder
- [ ] RISK-03: No secrets or hardcoded values in code
- [ ] RISK-04: SDK layer used throughout
- [ ] RISK-04: Extension points documented
- [ ] RISK-05: `uv run ruff check src/` → 0 errors
- [ ] RISK-05: `uv run pytest --cov=src` → ≥ 85%
- [ ] KEEP-01: PRD + PLAN + TODO complete and up to date
- [ ] KEEP-02: All modules have docstrings
- [ ] KEEP-03: Tests cover all benchmark scenarios + edge cases
- [ ] KEEP-04: Results notebook or analysis document with interpretation
- [ ] KEEP-05: Git history shows clean, meaningful commits
