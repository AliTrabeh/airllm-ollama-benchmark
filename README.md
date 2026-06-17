# airllm-ollama-benchmark

**HW05 — AI Orchestra Course**

Benchmark comparing three LLM inference methods on local hardware:
1. **Ollama** — fast local inference via GGUF (small model, pipeline verification)
2. **HuggingFace Baseline** — standard model loading (demonstrates large model limits)
3. **AirLLM** — virtual memory paging (runs large models on CPU with low RAM)

**Goal:** Prove that AirLLM can run models too large for normal RAM/VRAM, by measuring
and comparing latency, memory usage, and throughput across all three methods.

---

## Requirements

- Python 3.10 (not the latest — compatibility with AirLLM and transformers)
- [uv](https://github.com/astral-sh/uv) package manager (MANDATORY)
- [Ollama](https://ollama.ai) installed and running
- HuggingFace account with API token (for model downloads)
- ~20 GB free disk space for model files

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd airllm-ollama-benchmark

# 2. Copy environment template and fill in your values
cp .env.example .env
# Edit .env: set HF_TOKEN=your_token_here

# 3. Install all dependencies via uv
uv sync

# 4. Verify setup
uv run python -c "import airllm_benchmark; print(airllm_benchmark.__version__)"
```

---

## Usage

### Run Ollama baseline (small model, quick verification)
```bash
uv run python src/airllm_benchmark/main.py \
    --method ollama \
    --prompt "What is the capital of France?" \
    --max-tokens 50
```

### Run HuggingFace baseline (demonstrates large model limits)
```bash
uv run python src/airllm_benchmark/main.py \
    --method hf_baseline \
    --prompt "Explain quantum entanglement briefly." \
    --max-tokens 100
```

### Run AirLLM on CPU (large model, layer-by-layer paging)
```bash
uv run python src/airllm_benchmark/main.py \
    --method airllm \
    --prompt "Explain quantum entanglement briefly." \
    --max-tokens 20
```

### Run all methods and generate comparison report
```bash
uv run python src/airllm_benchmark/main.py \
    --method all \
    --prompt "Explain quantum entanglement briefly." \
    --max-tokens 20
```

Results saved to `results/` directory.

---

## Configuration

All settings in `config/setup.json` and environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace API token | — (required) |
| `MODEL_ID` | HuggingFace model for HF baseline | See setup.json |
| `OLLAMA_MODEL` | Ollama model name | See setup.json |
| `AIRLLM_MODEL_ID` | HuggingFace model for AirLLM | See setup.json |
| `MAX_NEW_TOKENS` | Token generation limit | 20 (keep small!) |
| `MODELS_DIR` | Local model cache directory | ./models/ |
| `RESULTS_DIR` | Output directory | ./results/ |
| `DEVICE` | cuda or cpu | cpu |

See `.env.example` for a complete template with comments.

---

## Quality Checks

```bash
# Lint check (must pass with 0 errors)
uv run ruff check src/

# Run tests with coverage (must be ≥ 85%)
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_services/test_ollama_service.py -v
```

---

## Results & Analysis

After running benchmarks, open the analysis notebook:

```bash
uv run jupyter notebook notebooks/results_analysis.ipynb
```

Results are saved as JSON in `results/`. Charts are saved in `assets/`.

---

## Project Structure

```
airllm-ollama-benchmark/
├── src/airllm_benchmark/        # Main package
│   ├── sdk/sdk.py               # SDK layer (single entry point)
│   ├── services/                # Business logic (one file per method)
│   ├── models/                  # Data models (BenchmarkResult, etc.)
│   └── shared/                  # Config, gatekeeper, constants
├── tests/                       # Unit and integration tests
├── docs/                        # All planning and architecture documents
│   └── prds/                    # Per-mechanism PRD files
├── config/                      # Configuration files (no secrets)
├── notebooks/                   # Results analysis notebook
├── results/                     # Benchmark output (JSON)
├── assets/                      # Charts and screenshots
├── pyproject.toml               # Build, lint, test config
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## Architecture

All business logic flows through the SDK layer:

```
CLI (main.py) → SDK (sdk.py) → Gatekeeper → Services → External APIs/Models
```

See `docs/PLAN.md` and `docs/ARCHITECTURE.md` for full architecture documentation.

---

## License

MIT License. See LICENSE file.

Model licenses: see `docs/MODEL_SELECTION.md` for individual model license information.

---

## AI-Assisted Development

This project was developed with AI assistance (Claude Code). All prompts and AI interactions
are documented in `docs/PROMPTS.md` per course guidelines (software_submission_guidelines-V3 §8.3).
