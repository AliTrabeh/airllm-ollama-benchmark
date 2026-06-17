# Assignment Analysis — HW05

**Source:** L08-summary-Lora-AirLLM-and-HW (Section 9: המשימה המעשית)

---

## What HW05 Asks Us to Build

The goal is to **prove that AirLLM works** — to demonstrate that a model too large for normal
RAM/GPU can still run locally on CPU using AirLLM's virtual-memory paging approach.

### The 5 Required Steps (Section 9.1)

| Step | Description | Source |
|------|-------------|--------|
| 1 | Choose a task and select a Hugging Face model suitable for the computer | L08-summary §9.1 |
| 2 | Install Ollama, run the model, verify everything works (functional baseline) | L08-summary §9.1 |
| 3 | Take a model too large for RAM/GPU — show it's too slow or fails normally | L08-summary §9.1 |
| 4 | Run that same model via AirLLM on CPU — show it DOES run, measure latency | L08-summary §9.1 |
| 5 | Measure & compare: response time, memory, run time — CPU vs GPU vs AirLLM | L08-summary §9.1 |

### Official Tips from Assignment (Section 9.1 — red box)

- Use virtual environment; preferably **uv** (MANDATORY per guidelines)
- Do **NOT** use the newest Python version — many packages not yet compatible
- Protect HuggingFace token — never expose it
- Start with a **small model and small max_new_tokens** to verify the pipeline before trying heavy models
- Ensure enough **disk space** before downloading large models

---

## Measurements Required

From Section 9.1 (step 5):

- Response time (latency in seconds)
- Memory consumption (RAM in GB, VRAM in GB)
- Run time (total wall-clock time per inference)
- Comparison table: CPU baseline vs GPU baseline vs AirLLM CPU

---

## What AirLLM Is (from L08-summary, Section 8)

AirLLM is an open-source research tool that allows running large models (even huge ones) on
a standard CPU by using **virtual memory paging** (`mmap` + SafeTensors format).

Key principle: Only one layer at a time is loaded into RAM. The OS page table maps layers
from disk into virtual memory. When a layer is needed, a Page Fault triggers the kernel to
load it from disk into the Page Cache. This is exactly how OS virtual memory works.

**Trade-off:** Very small memory footprint, but **high latency** due to I/O-bound disk reads.

This is why we measure latency explicitly — AirLLM's whole point is enabling large model
inference at the cost of speed.

---

## What Ollama Is (from L08-summary, Section 6)

Ollama is the "Netflix of models" — it knows how to read GGUF files, loads the model,
and runs it. It exposes an OpenAI-compatible API on `localhost:11434`. It's used here as
the **normal inference baseline** (fast, small model, shows the system works end-to-end).

---

## Model Selection Criteria (from L08-summary, Section 4.1)

1. **Task** — what task do we want? Text generation (causal LM) is simplest.
2. **License** — must check license before use
3. **Format** — SafeTensors preferred for AirLLM (not GGUF, not pickle)
4. **Model size** — too large for GPU/RAM is the *point* of the demo
5. **Latency** — how long is acceptable to wait?

> "A large model isn't necessarily better for the task. A much larger model is better in
> practice, but more expensive to run. Model size is critical." — L08-summary §4.1

---

## Quantization Context (from L08-summary, Section 5)

Start with Q2 to verify the pipeline before caring about output quality.
FP32=full precision, FP16=half memory, FP8=aggressive, Q4=standard quantization, Q2=extreme.

---

## Recommended Approach

Based on the assignment tips:

1. **Small model first** (e.g., 1-3B param) via Ollama — verify end-to-end pipeline
2. **Medium model** (e.g., 7B) — show it fits with Ollama, measure normal inference
3. **Large model** (e.g., 13B or 70B) — show it fails or is impractically slow normally
4. **Same or comparable large model via AirLLM** — show it runs on CPU, measure latency
5. **Compare all three in a table and chart**
