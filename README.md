# airllm-ollama-benchmark

**HW05 — AI Orchestra Course**

Benchmark comparing three LLM inference methods on local hardware to prove that AirLLM
can run models that are too large for normal RAM/VRAM — at the cost of higher latency.

| Method | Model | Goal |
|--------|-------|------|
| **Ollama** | llama3.2:3b | Fast pipeline verification, latency baseline |
| **HuggingFace Baseline** | Phi-3-mini-4k-instruct (default) | Standard GPU loading, VRAM baseline |
| **AirLLM** | Mistral-7B-v0.1 | CPU layer-paging — runs 14 GB model on 8 GB VRAM GPU |

**Hypothesis:** A 14 GB fp16 model (Mistral-7B) exceeds the RTX 3060 Ti's 8 GB VRAM and
standard loading should fail or degrade badly. **Confirmed, with a twist:** on this
machine's NVIDIA Windows driver, the naive load doesn't crash with a clean CUDA OOM — the
driver's system-memory fallback silently pages the overflow into RAM instead. It "works,"
but takes 20.6 minutes and never actually respects the 8 GB VRAM limit (reports 13.8 GB
"VRAM" used). AirLLM, run on the exact same model, is 1.75× faster *and* keeps VRAM near
zero throughout. Full breakdown in [`docs/COSTS.md`](docs/COSTS.md).

---

## Hardware Tested

| Component | Spec |
|-----------|------|
| CPU | Intel i7-4790K (4 cores, 4.4 GHz boost) |
| GPU | NVIDIA RTX 3060 Ti — 8 GB GDDR6 VRAM |
| RAM | 32 GB DDR3 |
| OS | Windows 11 |

---

## Requirements

- Python 3.11 (pinned in `.python-version`)
- [uv](https://github.com/astral-sh/uv) package manager (MANDATORY per course guidelines)
- [Ollama](https://ollama.ai) installed and running (`ollama serve`)
- HuggingFace account + API token (for model downloads)
- ~20 GB free disk space for model files

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/AliTrabeh/airllm-ollama-benchmark.git
cd airllm-ollama-benchmark
cp .env.example .env          # fill in HF_TOKEN
uv sync

# Start Ollama in a separate terminal
ollama serve
ollama pull llama3.2:3b

# Run the full benchmark (all three methods)
uv run airllm-benchmark --method all --max-tokens 20

# Open results notebook
uv run jupyter notebook notebooks/results_analysis.ipynb
```

---

## Installation

### 1 — Install uv

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2 — Clone and set up the project

```bash
git clone https://github.com/AliTrabeh/airllm-ollama-benchmark.git
cd airllm-ollama-benchmark

# Copy environment template
cp .env.example .env
# Edit .env and set: HF_TOKEN=hf_your_token_here

# Install runtime + dev dependencies
uv sync

# For ML inference (torch, transformers, airllm)
uv sync --group ml
```

### 3 — Verify installation

```bash
uv run airllm-benchmark --version
# airllm-benchmark 1.00
```

---

## Usage

The CLI is `airllm-benchmark`. All commands use `uv run` to ensure the correct venv:

```
usage: airllm-benchmark [-h] [--version]
                        [--method {ollama,hf_baseline,airllm,all}]
                        [--prompt PROMPT] [--max-tokens MAX_TOKENS]
                        [--output-dir OUTPUT_DIR] [--verbose]
```

### Run Ollama baseline (quick verification, ~1–2 s)

```bash
uv run airllm-benchmark --method ollama --max-tokens 20 --verbose
```

**Expected output:**

```
airllm-benchmark v1.00  |  method=ollama  |  tokens=20
  Status  : OK
  Latency : 1.23s
  Tokens  : 20  (16.3 tok/s)
  RAM     : 412 MB peak
  Cost    : ~0.000069 kWh @ 200W TDP

Saved → results/run_20260622T120000Z_ollama.json
```

### Run HuggingFace baseline (standard GPU loading, ~55 s cached)

```bash
uv run airllm-benchmark --method hf_baseline --max-tokens 20
```

First run downloads Phi-3-mini-4k-instruct (~7.6 GB) to `./models/`. Subsequent runs use the cache.

### Run AirLLM (CPU layer-paging, large model, minutes)

```bash
uv run airllm-benchmark --method airllm --max-tokens 20
```

First run downloads Mistral-7B-v0.1 (~14 GB) to `./models/`. Inference is slow by design —
AirLLM pages one transformer layer at a time from disk into RAM.

A real captured terminal output sample (not a mock-up) is saved at
[`assets/terminal_output_sample.txt`](assets/terminal_output_sample.txt).

### Run all three methods and compare

```bash
uv run airllm-benchmark --method all --prompt "Explain quantum entanglement in one sentence."
```

**Expected output (sample — your numbers will vary):**

```
airllm-benchmark v1.00  |  method=all  |  tokens=20

# Benchmark Comparison Report

## Summary

| Method      | Latency (s) | RAM (MB) | VRAM (MB) | Tokens/s | Cost                      |
|-------------|-------------|----------|-----------|----------|---------------------------|
| ollama      |        1.23 |    412.0 |    1800.0 |    16.26 | ~0.000069 kWh @ 200W TDP  |
| hf_baseline |        3.47 |   2048.0 |    2200.0 |     5.76 | ~0.000193 kWh @ 200W TDP  |
| airllm      |      847.32 |   1820.0 |       0.0 |     0.02 | ~0.015263 kWh @ 65W TDP   |

## Recommendations

- Use **ollama** for lowest latency.
- Use **airllm** for lowest RAM footprint.
- AirLLM successfully ran a model too large for normal VRAM via layer paging.

Saved → results/comparison_20260622T121500Z.json
```

### CLI flags reference

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--method` | choice | `all` | Which inference method to run |
| `--prompt` | str | "Explain quantum entanglement…" | Prompt sent to the model |
| `--max-tokens` | int | `20` | Max new tokens to generate (keep small for AirLLM) |
| `--output-dir` | path | `./results` | Override result output directory |
| `--verbose` | flag | off | Print full JSON result instead of summary |

---

## UI/UX & Usability

This project's "UI" is the CLI. Applying [Nielsen's 10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/):

1. **Visibility of system status** — every run prints a hardware profile, then per-method
   progress (download/loading bars from `transformers`/`huggingface_hub`), then a result
   block. Nothing runs silently.
2. **Match real-world language** — output uses plain terms (`Latency`, `RAM`, `Cost`), not
   internal jargon (no raw class names or stack traces on the happy path).
3. **User control and freedom** — every parameter (`--method`, `--prompt`, `--max-tokens`,
   `--output-dir`) is overridable per-invocation; nothing is hardcoded into a single flow.
4. **Consistency and standards** — all three methods share one CLI shape, one JSON result
   schema (`BenchmarkResult`), and one summary format, regardless of which method ran.
5. **Error prevention** — `--max-tokens` defaults small (20) specifically to avoid an
   inexperienced user accidentally starting a 10+ minute AirLLM run by mistake; the README
   calls this out explicitly under "Start small."
6. **Recognition over recall** — `--help` and `--version` are standard argparse flags; the
   user never needs to remember flag names from memory alone.
7. **Flexibility and efficiency of use** — power users can skip straight to `--method all`
   for the full comparison in one command; new users can run one method at a time.
8. **Aesthetic and minimalist design** — the default (non-`--verbose`) output is five lines:
   status, latency, tokens, RAM, cost. The full JSON is opt-in via `--verbose`.
9. **Help users recognize, diagnose, and recover from errors** — connection/model-not-found
   errors print actionable next steps (e.g. `Start it with: ollama serve`,
   `Run: ollama pull <model>`) instead of bare exceptions.
10. **Help and documentation** — this README's Usage section shows real captured output for
    every mode; [`assets/terminal_output_sample.txt`](assets/terminal_output_sample.txt) is an
    actual terminal capture, not a mock-up.

---

## Configuration

### Environment variables (`.env`)

Copy `.env.example` to `.env` and fill in your values. Never commit `.env`.

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | **Yes** | HuggingFace API token — get one at huggingface.co/settings/tokens |
| `MODEL_ID` | No | Override HF baseline model (default: `microsoft/Phi-3-mini-4k-instruct`) |
| `AIRLLM_MODEL_ID` | No | Override AirLLM model (default: `mistralai/Mistral-7B-v0.1`) |
| `OLLAMA_MODEL` | No | Override Ollama model name (default: `llama3.2:3b`) |
| `MAX_NEW_TOKENS` | No | Global token limit (default: `20` — keep small for AirLLM) |
| `DEVICE` | No | `cuda` or `cpu` for HF baseline (default: `cuda`) |
| `MODELS_DIR` | No | Local model cache directory (default: `./models`) |
| `RESULTS_DIR` | No | Output directory for JSON results (default: `./results`) |

### config/setup.json

Non-secret settings committed to the repository. All values overridable via env vars.

```json
{
    "model_id":          "microsoft/Phi-3-mini-4k-instruct",
    "airllm_model_id":   "mistralai/Mistral-7B-v0.1",
    "ollama_model":      "llama3.2:3b",
    "ollama_url":        "http://localhost:11434",
    "max_new_tokens":    20,
    "airllm_max_seq_len": 128,
    "device":            "cuda",
    "models_dir":        "./models",
    "results_dir":       "./results"
}
```

### config/rate_limits.json

Controls the API Gatekeeper's per-service rate limiting and retry behavior.

```json
{
    "services": {
        "ollama":       { "requests_per_minute": 60, "max_retries": 3, "retry_delay_s": 1.0 },
        "huggingface":  { "requests_per_minute": 10, "max_retries": 3, "retry_delay_s": 5.0 },
        "airllm":       { "requests_per_minute": 2,  "max_retries": 1, "retry_delay_s": 10.0 }
    }
}
```

---

## Cost & Resource Analysis

Estimated energy cost per benchmark run at TDP (Thermal Design Power). See
[`docs/COSTS.md`](docs/COSTS.md) for the full breakdown with real measured data
and optimization recommendations.

| Method | Model | Latency | RAM Peak | VRAM Peak | Disk | Energy (kWh) | Cost @ $0.10/kWh |
|--------|-------|---------|----------|-----------|------|--------------|------------------|
| Ollama | llama3.2:3b | 2.77 s | 506 MB | 0 MB | 1.9 GB | ~0.00015 kWh @ 200W | ~$0.000015 |
| HF Baseline | Phi-3-mini-4k-instruct | 54.6 s | 11,048 MB | 7,309 MB | 7.1 GB | ~0.00303 kWh @ 200W | ~$0.0003 |
| AirLLM | Mistral-7B-v0.1 | 706.7 s (~11.8 min) | 14,916 MB | 8 MB (CPU only) | ~14 GB | ~0.01276 kWh @ 65W | ~$0.0013 |

Measured in a single `--method all` run with all models pre-cached (GPU: RTX 3060 Ti, `device=cuda`).

**Key observations:**
- AirLLM's energy cost per run is ~85× higher than Ollama due to the long inference time
- AirLLM uses **near-zero VRAM** (8 MB) — it runs entirely on CPU via `mmap` layer paging
- HF Baseline already peaks at 7.3 GB VRAM on Phi-3-mini (an 8 GB card) — pushed further
  (Mistral-7B, same path) it doesn't cleanly OOM on this driver, it silently falls back to
  system RAM and runs 1.75× slower than AirLLM on the identical model (see same-model
  comparison in [`docs/COSTS.md`](docs/COSTS.md))
- Ollama's quantized model is also the smallest on disk (1.9 GB) — quantization buys
  speed and storage efficiency together

**When AirLLM is worth the cost:**
Use AirLLM when a model exceeds available VRAM/RAM and you have time to wait.
For latency-sensitive workloads, use Ollama with a quantized model.

---

## Visualizations

Running `--method all` saves results to `results/`. Then generate charts:

```bash
uv run python - <<'EOF'
from airllm_benchmark.services.results_service import ResultsService
from airllm_benchmark.visualization.chart_service import ChartService

svc = ResultsService()
results = [svc.load_result(p) for p in svc.list_results()]
paths = ChartService().generate_all_charts(results)
for p in paths:
    print(f"Saved: {p}")
EOF
```

Four charts are saved to `assets/`:

| File | Description |
|------|-------------|
| `latency_bar.png` | Inference latency per method (seconds) |
| `memory_grouped_bar.png` | Peak RAM vs VRAM per method (MB) |
| `throughput_bar.png` | Token throughput per method (tokens/s) |
| `trade_off_scatter.png` | Latency vs RAM trade-off scatter plot |

Or open the notebook for interactive analysis:

```bash
uv run jupyter notebook notebooks/results_analysis.ipynb
```

---

## Project Structure

```
airllm-ollama-benchmark/
├── src/airllm_benchmark/
│   ├── sdk/sdk.py               # Single SDK entry point for all benchmark logic
│   ├── services/
│   │   ├── ollama_service.py    # Ollama REST API client
│   │   ├── hf_baseline_service.py  # HuggingFace transformers loader
│   │   ├── airllm_service.py    # AirLLM CPU layer-paging runner
│   │   ├── metrics_service.py   # RAM/VRAM/timing measurement
│   │   └── results_service.py   # JSON persistence
│   ├── models/
│   │   ├── benchmark_result.py  # BenchmarkResult dataclass
│   │   └── comparison_report.py # ComparisonReport + markdown/JSON output
│   ├── shared/
│   │   ├── gatekeeper.py        # API rate-limiter + retry wrapper
│   │   ├── config.py            # Config loader (JSON + env vars)
│   │   ├── constants.py         # Immutable defaults
│   │   └── version.py           # Version string (1.00)
│   ├── visualization/
│   │   ├── chart_service.py     # Matplotlib chart generator (4 chart types)
│   │   └── notebook_data.py     # Pandas DataFrame builder for notebook
│   └── main.py                  # CLI entry point
├── tests/
│   ├── unit/                    # Per-module unit tests (all external calls mocked)
│   └── integration/             # End-to-end pipeline tests (services mocked)
├── notebooks/
│   └── results_analysis.ipynb  # 8-section results analysis notebook
├── docs/
│   ├── PLAN.md                  # Architecture + ADRs
│   ├── ARCHITECTURE.md          # C4 diagrams
│   ├── MODEL_SELECTION.md       # Model choice rationale
│   └── prds/                    # 561 micro-PRDs across 14 groups
├── config/
│   ├── setup.json               # Non-secret settings
│   └── rate_limits.json         # Gatekeeper rate limits
├── results/                     # Benchmark JSON output (git-ignored)
├── assets/                      # PNG charts (git-ignored)
├── models/                      # Downloaded model cache (git-ignored)
├── pyproject.toml               # Build + lint + test config
├── uv.lock                      # Locked dependency versions
└── .env.example                 # All environment variables (no secrets)
```

---

## Architecture

All business logic flows through the SDK layer — nothing bypasses it:

```
CLI (main.py)
    └── BenchmarkSDK (sdk/sdk.py)        ← single entry point
            └── ApiGatekeeper             ← rate limits + retries + logging
                    ├── OllamaService     → POST localhost:11434/api/generate
                    ├── HFBaselineService → HuggingFace transformers
                    └── AirLLMService     → AirLLM mmap layer-paging
                                ↓
                        MetricsCollector  ← background thread: RAM peak + VRAM
                                ↓
                        BenchmarkResult   ← latency, RAM, VRAM, tokens/s, cost
                                ↓
                        ResultsService    ← saves JSON to results/
                                ↓
                        ChartService      ← saves PNG to assets/
```

See `docs/PLAN.md` for full ADRs and `docs/ARCHITECTURE.md` for C4 diagrams.

---

## How to Add a New Inference Method

The architecture is designed for extension. To add, e.g., `llama.cpp`:

1. Create `src/airllm_benchmark/services/llamacpp_service.py`:
   ```python
   class LlamaCppService:
       def run(self, prompt: str, model_id: str, max_tokens: int) -> BenchmarkResult:
           ...
   ```

2. Add `run_llamacpp()` to `BenchmarkSDK` in `sdk/sdk.py` (one method)

3. Add `"llamacpp"` to `VALID_METHODS` in `shared/constants.py`

4. Add config entry in `config/setup.json`:
   ```json
   "llamacpp_model": "path/to/model.gguf"
   ```

5. Write tests in `tests/unit/test_services/test_llamacpp_service.py`

No other existing files need to change.

---

## Quality Checks

```bash
# Lint (must pass with 0 errors)
uv run ruff check src/

# Tests with coverage (must reach ≥ 85%)
uv run pytest tests/

# Check all source files are ≤ 150 lines
find src -name "*.py" | xargs wc -l | sort -rn | head -10
```

Current status: **159 tests | 95.62% coverage | ruff 0 errors | all files ≤ 150 lines**

---

## Contribution Guidelines

- All code through the SDK layer — no direct service calls from CLI or tests
- Max 150 lines per source file (split if needed)
- Zero Ruff errors (`uv run ruff check src/`)
- Every new function/class must have at least one test
- No hardcoded values — use `cfg.get()` or `os.environ.get()`
- No secrets in code — use `.env` (git-ignored)
- All package operations via `uv` only — never `pip`
- Follow TDD: write the test, watch it fail, then implement

---

## License & Credits

**License:** MIT — see LICENSE file.

**Model licenses:**
- TinyLlama-1.1B-Chat: Apache 2.0
- Mistral-7B-v0.1: Apache 2.0

**Third-party libraries:** requests, psutil, matplotlib, pandas, transformers, torch,
airllm — see `pyproject.toml` for versions.

---

## AI-Assisted Development

Developed with Claude Code (Anthropic). All prompts and AI interactions are documented
in `docs/PROMPTS.md` per course guidelines (software_submission_guidelines-V3 §8.3).
