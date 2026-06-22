# Model Selection

**Source:** L08-summary §4 (selection criteria), §9.1 (assignment steps)

---

## Selection Criteria (from lecture §4.1)

| Criterion | Decision |
|-----------|----------|
| Task | Text generation (causal LM) — simplest pipeline, easiest to measure |
| License | Apache 2.0 or similar permissive |
| Format | SafeTensors (required for AirLLM layer paging) |
| Size | Small model must fit in 8 GB VRAM; large model must NOT fit (demonstrates the problem) |
| Latency | Small model should respond in seconds; large model OOM is the expected outcome |

---

## Chosen Models

### Small Model — Pipeline Verification

| Field | Value |
|-------|-------|
| HuggingFace ID | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` |
| Parameters | 1.1 B |
| Size on disk | ~2.2 GB (fp16 SafeTensors) |
| VRAM required | ~2.2 GB fp16 — fits easily in 8 GB |
| License | Apache 2.0 |
| Format | SafeTensors ✓ |
| Purpose | Verify the inference pipeline works before testing large models |

### Large Model — OOM Demo + AirLLM Target

| Field | Value |
|-------|-------|
| HuggingFace ID | `mistralai/Mistral-7B-v0.1` |
| Parameters | 7 B |
| Size on disk | ~14 GB (fp16 SafeTensors) |
| VRAM required | ~14 GB fp16 — **exceeds 8 GB RTX 3060 Ti** |
| License | Apache 2.0 |
| Format | SafeTensors ✓ |
| Purpose | (1) HF baseline: demonstrates OOM on normal loading; (2) AirLLM: runs successfully via layer paging |

### Ollama Baseline

| Field | Value |
|-------|-------|
| Ollama tag | `tinyllama` |
| Underlying model | TinyLlama 1.1B, GGUF quantized (Q4_K_M) |
| VRAM | ~600 MB quantized — trivially fits |
| Purpose | Fast quantized inference baseline; shows the Ollama workflow |

---

## Hardware Context

- GPU: RTX 3060 Ti — **8 GB GDDR6 VRAM**
- RAM: 32 GB DDR3
- The 7B model in fp16 requires ~14 GB VRAM → OOM on this card → AirLLM layer paging solves it

---

## Why These Models

1. **TinyLlama** is widely used for testing (fast, no gating, Apache 2.0), proving the pipeline before committing to a heavy run.
2. **Mistral-7B-v0.1** is the canonical "too large for consumer GPU in fp16" model: 14 GB fp16 vs 8 GB VRAM. It ships in SafeTensors format which AirLLM requires.
3. The same model ID is used for both the HF baseline (fails) and AirLLM (succeeds) — making the comparison direct and fair.
