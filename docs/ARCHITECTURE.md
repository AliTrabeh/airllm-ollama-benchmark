# Architecture — airllm-ollama-benchmark

**Source:** software_submission_guidelines-V3 §4, §16 + L08-summary §6, §8

---

## Three-Method Benchmark Architecture

This project benchmarks three distinct LLM inference approaches.
Each is isolated in its own service module. The SDK provides a unified interface.

---

## Method 1: Ollama (Local Inference via GGUF)

**Source:** L08-summary §6

```
┌─────────────────────────────────────────────────┐
│  Ollama Process (background daemon)               │
│  - Reads GGUF model file                         │
│  - Exposes OpenAI-compatible API on :11434        │
│  - Handles model loading, quantization, inference │
└─────────────────────┬───────────────────────────┘
                      │ HTTP REST (localhost:11434)
                      ▼
┌─────────────────────────────────────────────────┐
│  ollama_service.py                               │
│  - POST /api/generate                            │
│  - Wraps call in Gatekeeper                      │
│  - Measures: wall-clock time, token count        │
│  - Note: memory measured via OS (psutil)         │
└─────────────────────────────────────────────────┘
```

**Key facts:**
- Ollama loads GGUF format (quantized, compressed)
- Runs on CPU or GPU depending on available hardware
- Very fast for small-medium models
- Used as the "this works normally" baseline

---

## Method 2: HuggingFace Standard Loading (Baseline)

**Source:** L08-summary §3 (Inference: Prefill & Decode), §4 (Model selection)

```
┌─────────────────────────────────────────────────┐
│  hf_baseline_service.py                          │
│  - AutoModelForCausalLM.from_pretrained()        │
│  - Loads ALL weights into RAM/VRAM at once       │
│  - Runs inference (Prefill + Decode phases)      │
│  - Fails or runs out of memory for large models  │
└─────────────────────────────────────────────────┘
```

**Key facts:**
- Standard HuggingFace Transformers loading
- Entire model weight matrix loaded into VRAM (GPU) or RAM (CPU)
- Memory requirement ≈ model_params × bytes_per_param
  (e.g., 7B params × 2 bytes FP16 = 14 GB)
- This is the "too big to fit" failure mode we demonstrate

---

## Method 3: AirLLM (Virtual Memory Paging)

**Source:** L08-summary §8 (AirLLM: Running Large Models on CPU)

```
┌─────────────────────────────────────────────────┐
│  airllm_service.py                               │
│  - AirLLMChatGenerationMixin or LlamaChat()      │
│  - Uses mmap: maps SafeTensors file to VM space  │
│  - Only ONE LAYER loaded into RAM at a time      │
│  - OS page faults trigger disk reads per layer   │
└─────────────────────────────────────────────────┘
      │
      │ Virtual Memory (mmap)
      ▼
┌─────────────────────────────────────────────────┐
│  OS Page Table                                   │
│  Virtual Address → Physical RAM page             │
│  Page Fault → Kernel reads page from disk        │
└─────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Disk: SafeTensors model file                    │
│  (can be TB on disk, only MB accessed at once)  │
└─────────────────────────────────────────────────┘
```

**Key facts (from lecture §8.1-8.4):**
- AirLLM processes ONE LAYER at a time
- Memory footprint = one layer + KV cache (very small vs full model)
- Latency is high because each layer requires disk I/O
- Uses SafeTensors + mmap (not pickle/bin)
- The bottleneck is I/O (disk bandwidth), not compute
- This is the virtual-memory paging principle (§8.2): OS brings pages in on demand

---

## Metrics Collection Architecture

```
┌───────────────────────────────────────────────────────┐
│  MetricsService                                        │
│                                                        │
│  capture_context():                                    │
│    - time.perf_counter() for wall clock                │
│    - psutil.Process().memory_info().rss for RAM        │
│    - torch.cuda.memory_allocated() for VRAM (if GPU)  │
│    - Token count from tokenizer                        │
│                                                        │
│  Returns: BenchmarkResult dataclass                    │
└───────────────────────────────────────────────────────┘
```

### BenchmarkResult fields:
```python
@dataclass
class BenchmarkResult:
    method: str          # "ollama" | "hf_baseline" | "airllm"
    model_id: str        # HuggingFace model ID or Ollama model name
    prompt: str          # Input prompt
    output: str          # Model output text
    latency_s: float     # Total wall-clock seconds
    ram_peak_mb: float   # Peak RAM usage in MB
    vram_peak_mb: float  # Peak VRAM usage in MB (0 if CPU)
    tokens_generated: int
    tokens_per_second: float
    error: str | None    # Error message if run failed
    timestamp: str       # ISO format
```

---

## Data Flow (Complete)

```
1. User: uv run python src/airllm_benchmark/main.py --method all --prompt "..."
2. main.py: parse args, create Config, call SDK
3. SDK: validate inputs, delegate to appropriate service(s)
4. Gatekeeper: check rate limits, log call
5. Service: execute inference + capture metrics
6. MetricsService: record timing and memory
7. BenchmarkResult: returned to SDK
8. SDK: aggregate into ComparisonReport
9. main.py: save to results/results_<timestamp>.json
10. Notebook: read results/, generate charts, interpret
```

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.10 | Compatibility per assignment tips (not newest) |
| Package manager | uv | MANDATORY per guidelines §8.4 |
| Model inference (Ollama) | requests / httpx | REST calls to local Ollama daemon |
| Model inference (HF) | transformers + torch | Standard HuggingFace stack |
| Model inference (AirLLM) | airllm library | Assignment requirement |
| Memory measurement | psutil + torch.cuda | Cross-platform memory monitoring |
| Testing | pytest + pytest-cov | Required by guidelines |
| Linting | ruff | Required by guidelines §7.1 |
| Data serialization | json / dataclasses | Simple, no external dependency |
| Visualization | matplotlib / plotly | Charts for results |
| Notebooks | Jupyter | Results analysis per guidelines §9.2 |

---

## Security Architecture

Source: software_submission_guidelines-V3 §7.4

```
.env (git-ignored)           # Real secrets: HF_TOKEN=hf_xxxxx
.env.example (committed)     # Template: HF_TOKEN=

src/.../shared/config.py     # Loads via os.environ.get("HF_TOKEN")
                             # Never hardcodes token
                             # Raises clear error if token missing
```

HuggingFace token is used ONLY for model downloads. Never printed, logged, or
included in any output files.
