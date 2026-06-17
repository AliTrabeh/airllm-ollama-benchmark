# PRD-04: AirLLM CPU Runner

**Source files used:**
- L08-summary-Lora-AirLLM-and-HW §8 (AirLLM: Running Large Models on CPU), §9.1 (step 4)
- software_submission_guidelines-V3 §4 (SDK), §5 (Gatekeeper)

**Status:** TODO

---

## Goal

Implement a service that runs a large HuggingFace model on CPU using AirLLM's virtual
memory paging approach, demonstrating that a model too large for normal RAM can still
run, and capturing the latency/memory trade-off data.

---

## Background (from L08-summary §8)

**AirLLM** is an open-source research tool for running large models on standard CPU:

- Works layer by layer: only ONE LAYER is loaded into RAM at any time
- Uses `mmap` on SafeTensors format to map model weights as virtual memory
- Page faults trigger kernel to load layer data from disk on demand
- Memory footprint: tiny (one layer) vs full model
- Latency: HIGH (I/O-bound — each layer requires disk read)
- The bottleneck is disk bandwidth, not compute

From lecture §8.3: "AirLLM's real bottleneck is I/O. Small memory footprint but high latency.
Good for research on consumer hardware, not for real-time production use."

**Why SafeTensors?** (from L08-summary §4.3, §8.4):
SafeTensors is a flat buffer format (no executable code, no deserialization). It enables
`mmap` directly: `mmap(file)` maps the file to virtual memory, and the OS loads pages
only when accessed. Pickle-based `.bin` files cannot be mmap'd safely.

---

## Requirements

### Functional
- `AirLLMService.run(prompt, model_id, max_tokens)` runs inference via AirLLM
- Captures: latency per token (seconds/token), total latency, peak RAM during inference
- Model must be in SafeTensors format on disk
- HF_TOKEN used for initial download if needed
- Handles gracefully: model not found on disk, insufficient disk space, import errors

### Non-Functional
- AirLLM library version pinned in pyproject.toml
- Layer-by-layer processing is transparent to the SDK caller
- Model storage path configurable via `MODELS_DIR` env var
- Start with a small `max_new_tokens` (e.g., 20) to verify pipeline before heavy runs

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/services/
└── airllm_service.py               # AirLLMService class

tests/unit/test_services/
└── test_airllm_service.py          # Unit tests with mocked airllm

config/setup.json                   # Add: airllm_max_tokens (start small!), airllm_model_id
```

---

## Acceptance Criteria

- [ ] `AirLLMService.run()` returns `BenchmarkResult` with populated latency_s and ram_peak_mb
- [ ] `latency_s` is significantly higher than Ollama baseline (expected for I/O-bound inference)
- [ ] RAM peak is significantly lower than HF baseline (expected for layer-by-layer loading)
- [ ] Starting with `max_new_tokens=20` is the default (safety first)
- [ ] Unit tests pass with mocked AirLLM library calls
- [ ] Test coverage ≥ 85% for `airllm_service.py`
- [ ] AirLLM successfully runs a model that failed in HF baseline

---

## Tests / Checks

- `test_airllm_service.py`:
  - `test_successful_run()` — mocked, verifies BenchmarkResult populated
  - `test_latency_captured()` — latency_s > 0
  - `test_ram_captured()` — ram_peak_mb > 0
  - `test_model_path_from_config()` — no hardcoded path
  - `test_small_tokens_default()` — max_new_tokens defaults to small value

---

## Grading Risks

- AirLLM not actually running the large model → missing step 4 of assignment (L08 §9.1)
- Missing latency measurement → key metric missing from comparison
- Using GGUF format instead of SafeTensors → AirLLM won't work (L08 §4.3)
- No comparison showing AirLLM succeeds where HF baseline failed → assignment not demonstrated
- max_new_tokens too high → timeout during grading evaluation
