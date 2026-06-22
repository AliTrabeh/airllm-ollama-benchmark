# PRD-01: Environment & Project Skeleton Setup

**Source files used:**
- software_submission_guidelines-V3 §8.4 (uv), §2.4 (project structure), §7 (config/security)
- L08-summary-Lora-AirLLM-and-HW §9.1 (tips: use uv, avoid newest Python)

**Status:** DONE

---

## Goal

Set up a fully functional, reproducible Python project environment using `uv`, with the
correct directory structure, pyproject.toml, all config files, and quality tooling
(Ruff + pytest + coverage) configured and passing from day one.

---

## Requirements

### Functional Requirements
- Project runs on Python 3.10 (not newest — per L08 §9.1 tips)
- All dependencies managed exclusively via `uv` (no pip, python -m, venv)
- `uv sync` from a fresh clone sets up the entire environment
- `uv run python src/airllm_benchmark/main.py --help` runs without errors
- `uv run ruff check src/` passes with 0 errors
- `uv run pytest tests/ --cov=src --cov-report=term-missing` runs (even with empty tests)

### Non-Functional Requirements
- No secrets in any committed file
- `.env.example` contains all required placeholders
- `pyproject.toml` contains all tool configurations (ruff, pytest, coverage)
- Project version starts at `1.00` in `version.py`

---

## Files Expected to be Created or Modified

```
pyproject.toml                          # Build + lint + test + coverage config
uv.lock                                 # Locked dependencies (auto-generated)
.env.example                            # Placeholder env vars
.gitignore                              # Covers .env, __pycache__, models/, etc.
README.md                               # Initial skeleton (to be filled)

src/
└── airllm_benchmark/
    ├── __init__.py                     # Package init with __version__ and __all__
    ├── main.py                         # CLI entry point skeleton
    └── shared/
        ├── __init__.py
        ├── version.py                  # Version = "1.00"
        ├── constants.py                # Empty for now
        └── config.py                  # Loads .env and config/setup.json

config/
├── setup.json                          # App config (model IDs, max_tokens, etc.)
└── rate_limits.json                    # Gatekeeper rate limit config

tests/
├── conftest.py                         # Shared fixtures
└── unit/
    └── test_shared/
        └── test_config.py              # Tests config loading
```

---

## Acceptance Criteria

- [ ] `uv sync` completes without errors on a fresh clone
- [ ] `uv run python -c "import airllm_benchmark; print(airllm_benchmark.__version__)"` prints `1.00`
- [ ] `uv run ruff check src/` → 0 errors
- [ ] `uv run pytest tests/ -v` → all tests pass
- [ ] `.env` is NOT committed (`.gitignore` covers it)
- [ ] `.env.example` IS committed with all placeholder keys
- [ ] `config/setup.json` exists and is valid JSON
- [ ] No hardcoded values in any `.py` file

---

## Tests / Checks

- `test_config.py`: loads config, verifies required keys present
- `test_config.py`: raises clear error if HF_TOKEN missing (not a cryptic KeyError)
- `test_config.py`: all values come from config files or env, not hardcoded

---

## Grading Risks

- Missing `uv.lock` → fail mandatory check (guidelines §8.4)
- Using `pip` anywhere → fail mandatory check
- Hardcoded HF_TOKEN → security violation
- Python version incompatibility → runtime errors during grading
- Missing `.env.example` → configuration portability deduction (RISK-03)
