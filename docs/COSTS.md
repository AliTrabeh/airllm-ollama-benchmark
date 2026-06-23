# Cost & Resource Analysis

Real measurements from `results/*.json`, captured on the project's reference hardware
(Intel i7-4790K, RTX 3060 Ti 8 GB VRAM, 32 GB DDR3). All runs use 20 generated tokens
and the prompt `"Explain quantum entanglement in one sentence."`.

## Final comparison run (`--method all`, single process, cached models)

All three methods run back-to-back in the same `--method all` invocation, with every
model already cached locally (no download time included) — the most directly comparable
measurement available.

| Method | Model | Latency | RAM Peak | VRAM Peak | Disk | Tokens/s | Energy (kWh) | Cost @ $0.10/kWh |
|--------|-------|---------|----------|-----------|------|----------|---------------|------------------|
| Ollama | llama3.2:3b | 2.77 s | 506 MB | 0 MB | 1.88 GB | 88.88 | ~0.00015 | ~$0.000015 |
| HF Baseline | microsoft/Phi-3-mini-4k-instruct | 54.60 s | 11,048 MB | 7,309 MB | 7.12 GB | 0.37 | ~0.00303 | ~$0.0003 |
| AirLLM | mistralai/Mistral-7B-v0.1 | 706.67 s | 14,916 MB | 8 MB | 0.002 GB* | 0.03 | ~0.01276 | ~$0.0013 |

\* AirLLM's `disk_gb` in this particular run undercounts — a config bug (since fixed,
see `shared/config.py::load_config`) meant this run's Mistral-7B download landed under
the system default HF cache instead of the configured `models_dir`, so the disk-size
probe looked in the wrong place. The model is genuinely ~14 GB on disk; future runs
measure this correctly.

## Same-model comparison: Mistral-7B-v0.1 (the assignment's actual core ask)

The assignment's 5-step recipe asks for one specific comparison: take the **same** large
model, show normal loading fails or is impractically slow, then show that *same* model
succeeds via AirLLM. The table above doesn't quite do this — it uses Phi-3-mini for the HF
baseline and Mistral-7B for AirLLM. Here's the direct, same-model comparison:

| Method | Model | Latency | RAM Peak | "VRAM" Peak | Disk | Tokens/s |
|--------|-------|---------|----------|--------------|------|----------|
| HF Baseline (naive `.to("cuda")`) | Mistral-7B-v0.1 | **1237.95 s (~20.6 min)** | 20,711 MB | **13,825 MB** | 13.49 GB | 0.016 |
| AirLLM (CPU layer paging) | Mistral-7B-v0.1 | **706.67 s (~11.8 min)** | 14,916 MB | 8 MB | ~14 GB | 0.028 |

**This did not produce a clean CUDA out-of-memory crash — and that result is itself the
most interesting finding.** Mistral-7B's fp16 weights (~14 GB) exceed the RTX 3060 Ti's 8 GB
VRAM by nearly 2×. On older drivers or Linux, `.to("cuda")` on a model this size raises a
hard `CUDA error: out of memory`. On this machine's NVIDIA Windows driver, though, the
driver's *system memory fallback* feature kicked in instead: when a CUDA allocation
exceeds physical VRAM, the driver transparently pages the overflow into system RAM rather
than failing the allocation. The reported VRAM peak (13.8 GB on an 8 GB card) is only
possible because of this — it's not a measurement error, it's CUDA lying to PyTorch about
how much memory it successfully allocated.

The practical consequence: the naive HF baseline *did* run on this model, but at a severe,
silent performance cost — **1.75× slower than AirLLM**, while using **~39% more RAM** and
never actually respecting the 8 GB VRAM boundary it's supposed to operate within. AirLLM,
by contrast, achieves both a faster result *and* genuinely honors the VRAM limit (8 MB
peak) by never attempting to hold more than one layer on the GPU at a time. On hardware
or drivers where the fallback isn't available, the HF baseline path would simply crash
instead of degrading — AirLLM's behavior doesn't depend on this driver quirk to be safe.

## CPU time / disk

- CPU/wall time is captured as `latency_s` in every result (see table above).
- Disk usage is now measured per-run via `disk_gb` (HF-cache snapshot size for
  hf_baseline/airllm, Ollama's `/api/tags` size field for ollama) rather than estimated.
- Model weights live outside the repo at `D:/ai_models` — `Phi-3-mini-4k-instruct`
  (~7.6 GB), `Mistral-7B-v0.1` (~14 GB, plus a transient duplicate on the system default
  cache from the bug above), `phi-2` (~5.4 GB), `TinyLlama-1.1B` (~2.2 GB), `llama3.2:3b`
  (~1.9 GB, Ollama-managed).

## Interpretation

- **Ollama is the only method viable for interactive use** on this hardware: it serves a
  quantized 3B model in ~2.8 s using ~500 MB of RAM and zero VRAM, at 88.9 tokens/s.
- **AirLLM trades latency for capability.** It runs Mistral-7B — a model whose fp16 weights
  (~14 GB) exceed the 8 GB VRAM card — by paging transformer layers from disk via `mmap`,
  one layer at a time, entirely on CPU. Even with the model already cached locally, this
  run took **11.8 minutes** (706.67 s) for 20 tokens — ~255× Ollama's latency — because
  generating each token requires a full pass over all 35 layers, each individually loaded
  from disk. VRAM stays near zero (8 MB) because layers never touch the GPU; RAM peaks
  highest of the three methods (~14.9 GB) since paged layers, KV-cache, and intermediate
  activations all stack up in system memory over the run.
- **The standard HF baseline sits in between, and that's the risk it represents.** With
  Phi-3-mini already cached, loading + generating took 54.6 s — far faster than AirLLM,
  but still ~20× slower than Ollama, while peaking at 7.3 GB VRAM on an 8 GB card. A
  naive `from_pretrained` load has **no fallback** if the next model is even slightly
  larger: it doesn't degrade gracefully like AirLLM does, it just OOMs.
- **Energy cost scales with latency, not model size directly.** AirLLM's per-run energy
  cost (~0.0128 kWh) is ~85× Ollama's, driven by ~12 minutes of CPU-bound wall time at a
  lower 65 W TDP estimate — not by raw FLOPs, since each individual layer computation is
  small.
- **Disk footprint is now measured, not estimated** (`disk_gb`): Ollama's quantized 3B
  model is the smallest on disk (1.9 GB) despite being the fastest at inference — a useful
  reminder that quantization buys both speed and storage efficiency simultaneously.

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
