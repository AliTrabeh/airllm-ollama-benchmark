# Cost & Resource Analysis

Real measurements from `results/*.json`, captured on the project's reference hardware
(Intel i7-4790K, RTX 3060 Ti 8 GB VRAM, 32 GB DDR3). All runs use 20 generated tokens
and the prompt `"Explain quantum entanglement in one sentence."`.

## Latest successful run per method

| Method | Model | Latency | RAM Peak | VRAM Peak | Tokens/s | Energy (kWh) | Cost @ $0.10/kWh |
|--------|-------|---------|----------|-----------|----------|---------------|------------------|
| Ollama | llama3.2:3b | 2.62 s | 507 MB | 0 MB | 128.96 | ~0.00015 | ~$0.000015 |
| HF Baseline | microsoft/Phi-3-mini-4k-instruct | 615.96 s* | 10,359 MB | 7,309 MB | 0.03 | ~0.03422 | ~$0.0034 |
| AirLLM | mistralai/Mistral-7B-v0.1 | 444.39 s | 4,560 MB | 8 MB | 0.05 | ~0.00802 | ~$0.0008 |

\* This HF Baseline run includes a one-time model download (~10 min, triggered by the
models-directory migration to a new drive). A cached run of an equivalent-size model
(microsoft/phi-2, 2.7B) without download overhead measured **509.2 s** latency and
**5,328 MB** VRAM peak — inference time dominates regardless of download status, because
loading a multi-GB checkpoint onto an 8 GB GPU is itself slow on this hardware.

## CPU time / disk

- CPU/wall time is captured as `latency_s` in every result (see table above).
- Disk usage: model weights now live outside the repo at `D:/ai_models` — `Phi-3-mini-4k-instruct`
  (~7.6 GB), `Mistral-7B-v0.1` (~14 GB), `phi-2` (~5.4 GB), `TinyLlama-1.1B` (~2.2 GB).
  Total disk footprint observed: ~36 GB.

## Interpretation

- **Ollama is the only method viable for interactive use** on this hardware: it serves a
  quantized 3B model in ~2.6 s using a few hundred MB of RAM and zero VRAM.
- **AirLLM trades latency for capability.** It runs Mistral-7B — a model whose fp16 weights
  (~14 GB) exceed the 8 GB VRAM card — by paging transformer layers from disk via `mmap`,
  at the cost of ~170× the latency of Ollama and ~4,560 MB RAM. VRAM stays near zero (8 MB)
  because layers are processed on CPU/disk, not held on the GPU.
- **The standard HF baseline is the worst of both worlds for large models.** A naive
  `from_pretrained` load of a model sized to nearly fill the GPU (Phi-3-mini, 7.3 GB VRAM
  peak on an 8 GB card) is both slow (minutes, not seconds) and memory-hungry, with no
  graceful degradation path if the model is any larger — it would simply OOM.
- **Energy cost scales with latency, not model size directly.** AirLLM's per-run energy
  cost (~0.008 kWh) is ~53× Ollama's, driven entirely by the extra ~7 minutes of wall time
  at a lower 65 W CPU-bound TDP estimate, not by FLOPs.

## Optimization recommendations

1. **Use Ollama with a quantized model whenever latency matters.** It is the cheapest and
   fastest option by a wide margin on this hardware.
2. **Reserve AirLLM for models that genuinely exceed available VRAM/RAM**, where the
   alternative is an outright OOM failure rather than a slower success.
3. **Avoid running the plain HF baseline on models sized close to the VRAM ceiling** —
   either quantize (4-bit/8-bit via `bitsandbytes`) or switch to AirLLM once the model
   approaches the GPU's capacity, since plain `from_pretrained` has no fallback when it
   doesn't fit.
4. **Warm the model cache before timing runs.** First-run downloads (minutes, network-bound)
   should not be counted against inference latency; the benchmark harness here separates
   the two only by convention (re-run once to get a cached-latency number) — a future
   improvement would be to time download and inference separately in `BenchmarkResult`.
