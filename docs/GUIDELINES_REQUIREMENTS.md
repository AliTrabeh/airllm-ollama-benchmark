# Guidelines Requirements

**Source:** software_submission_guidelines-V3 (Version 3.00, 2026-03-26)

---

## Mandatory Project Structure

Source: software_submission_guidelines-V3 §2.4

```
project-root/
├── src/
│   └── <package>/
│       ├── __init__.py
│       ├── sdk/
│       │   └── sdk.py          # Single entry point for ALL business logic
│       ├── services/           # Business logic
│       ├── shared/
│       │   ├── gatekeeper.py   # API Gatekeeper (rate limits, retries, logging)
│       │   ├── config.py       # Configuration manager
│       │   ├── version.py      # Version tracking (start at 1.00)
│       │   └── constants.py    # Immutable project constants
│       └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
│   ├── PRD.md
│   ├── PLAN.md
│   ├── TODO.md
│   └── PRD_<mechanism>.md      # Per-algorithm PRDs
├── config/
│   ├── setup.json
│   └── rate_limits.json
├── data/
├── results/
├── assets/
├── notebooks/
├── README.md                   # MANDATORY
├── pyproject.toml
├── uv.lock
├── .env-example
└── .gitignore
```

---

## README.md Requirements (§2.1)

Must serve as a user manual. Required sections:

- **Installation Instructions** — system requirements, step-by-step install, environment setup
- **Usage Instructions** — CLI/GUI workflow, examples in different modes
- **Examples and Demos** — code samples, usage screenshots
- **Configuration Guide** — all config files, parameters, effects
- **Contribution Guidelines** — code style and conventions
- **License & Credits** — license, third-party attribution

---

## docs/ Directory (§2.2)

### docs/PRD.md
Central product requirements document containing:
- Project overview, user context, target audience identification
- Success metrics, KPIs, acceptance criteria
- Functional and non-functional requirements, user stories, use cases
- Constraints, dependencies, external limitations
- Timeline and milestones with review points

### docs/PLAN.md
Technical architecture document containing:
- C4 Model diagrams (Context, Container, Component, Code)
- UML diagrams for processes and components
- Deployment and runtime architecture diagrams
- Architecture Decision Records (ADRs) with rationale and trade-offs
- API documentation, data schemas, contracts

### docs/TODO.md
Task tracking document with:
- Detailed task list with statuses (TODO / IN_PROGRESS / DONE)
- Phase breakdown with milestones
- Responsibility assignment
- Definition of done for each task

### Per-Algorithm PRD files (§2.3)
Each major mechanism or algorithm must have a dedicated PRD file, e.g.:
- `docs/prds/PRD_airllm_runner.md`
- `docs/prds/PRD_ollama_baseline.md`

Each PRD must include:
- Background/theory of the algorithm or mechanism
- Specific input/output requirements and success metrics
- Constraints, limitations, trade-offs, rationale
- Specific success criteria and testing requirements

---

## Code Quality Requirements

### File Size Limit (§3.2)
- **Max 150 lines per code file** (excluding comments and blank lines)
- Split files that exceed this limit

### SDK Architecture (§4.1)
- **All business logic must go through the SDK layer**
- No direct API calls in CLI, GUI, or test files
- External consumers call the SDK; SDK calls domain services

### OOP Design (§4.2)
- No code duplication
- Use mixins for shared behavior
- Functions with single responsibility

### API Gatekeeper (§5.1)
- All external API calls must go through the Gatekeeper
- Gatekeeper handles: rate limits, retries, logging, queueing

### Configuration (§5.2, §7.3)
- All rate limits from `config/rate_limits.json`
- All hardcoded values forbidden — use `cfg.get()` or `os.environ.get()`
- Config hierarchy: `config/` → JSON files

---

## Testing Requirements (§6)

### TDD Approach (§6.1)
- Follow Red → Green → Refactor cycle
- Tests written **before** or **with** the code
- Every module must have a test file
- Every function/class must have at least one test

### Coverage Requirement (§6.2)
- **Minimum 85% global test coverage**
- Tests fail if coverage drops below 85%
- Configure in pyproject.toml:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "*/tests/*", "src/**/gui/*"]

[tool.coverage.report]
fail_under = 85
```

### Edge Cases (§6.3)
- Document all boundary conditions
- Include screenshot with test output when relevant
- Graceful degradation for edge conditions

---

## Code Quality Tooling (§7)

### Linter: Ruff (§7.1)
- **Zero Ruff errors** required
- Configure in pyproject.toml:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","C4","SIM"]
ignore = ["E501"]
```

### No Hardcoded Values (§7.2)
- No API URLs, rate limits, timeouts, or secrets hardcoded in source
- All from config files or environment variables

---

## Security & Secrets (§7.4)

- **No secrets in code** — API keys, tokens, passwords
- Use `os.environ.get("VAR_NAME")` only
- `.env` must be in `.gitignore`
- `.env-example` must exist with placeholder values
- Token rotation, monitoring, minimum permissions

---

## Package Manager: uv (§8.4) — MANDATORY

- **FORBIDDEN:** `pip install`, `python -m`, `venv`, `virtualenv`
- **REQUIRED:** All operations via `uv`

| Task | Correct (uv) | Forbidden |
|------|-------------|-----------|
| Install deps | `uv sync` | `pip install` |
| Add package | `uv add <pkg>` | `pip install <pkg>` |
| Run script | `uv run python script.py` | `python script.py` |
| Run tests | `uv run pytest tests/` | `python -m pytest` |
| Lock deps | `uv lock` | `pip freeze` |

Requirements:
- `pyproject.toml` is the single source of truth (NOT requirements.txt)
- `uv.lock` must exist and be committed
- No `pip` calls in code, CI, scripts, or documentation

---

## Version Management (§8.1)

- All code and config must track versions
- Starting version: **1.00**
- In `src/<pkg>/shared/version.py`
- In config JSON as `"version"` key

---

## Research & Results (§9)

- Notebook-based results analysis (Jupyter or equivalent)
- Parameter exploration (sensitivity analysis)
- Visualization: Bar charts, Line charts, Scatter plots, Heatmaps, Box plots
- High-quality graphs: labeled axes, legends, clear titles, high resolution

---

## UI/UX Documentation (§10)

- Document user workflow (CLI in this project)
- Screenshots of every screen/state
- Nielsen's 10 Usability Heuristics considered
- Describe how a user experiences the system

---

## Cost & Resource Analysis (§11)

- **REQUIRED:** Cost breakdown table
- For this project: compute costs (time × electricity), disk space, RAM usage
- Track resource consumption per run
- Budget estimates and optimization strategies

---

## Prompt Engineering Log (§8.3)

- Document every prompt used during AI-assisted development
- For each prompt: purpose, prompt text, output summary, iterations

---

## Final Submission Checklist (§17, §20.9)

1. Documentation: PRD, PLAN, README, per-algorithm PRDs, prompts book
2. Code: modular, ≤150 lines per file, docstrings, naming conventions
3. Configuration: separate files, .env-example, no secrets, .gitignore
4. Tests: ≥85% coverage, edge cases, automated reports, TDD
5. Research: parameter experiments, results notebook, graphs
6. Visualization: architecture diagrams, screenshots, quality charts
7. Costs: resource table, detailed reporting
8. Extensibility: extension points documented, building-block design
9. General: Git history with clear commits, license, deployment notes
