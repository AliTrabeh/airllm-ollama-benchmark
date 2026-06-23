# Hardware Profiles

Detailed specs for the hardware this project was actually benchmarked on, plus expected
behavior per method given those specs. Source of truth for the structured data is
[`config/hardware_profiles.json`](../config/hardware_profiles.json); this doc is the
human-readable narrative version.

## Benchmark target

| Component | Spec |
|-----------|------|
| CPU | Intel Core i7-4790K — 4 cores / 8 threads, 95 W TDP |
| RAM | 32 GB DDR3, ~25.6 GB/s bandwidth |
| GPU | NVIDIA GeForce RTX 3060 Ti — 8 GB GDDR6 VRAM, 4864 CUDA cores, 200 W TDP |

This is an asymmetric setup deliberately: an older CPU paired with a genuinely capable GPU.
That asymmetry is what makes the AirLLM-vs-HF-baseline comparison meaningful — the GPU is
good enough to run small-to-mid models quickly, but not large enough to hold a 7B model at
full precision, so the interesting question is what happens when a model doesn't fit.

## Expected benchmark results on this hardware

Estimates before measuring, later confirmed by `results/*.json` (see
[`docs/COSTS.md`](COSTS.md) for the actual numbers):

| Method | Model class | Expected latency | Expected RAM | Expected VRAM | Expected tok/s |
|--------|-------------|-------------------|---------------|----------------|-----------------|
| Ollama | Quantized 3B (GGUF) | Seconds | < 1 GB | 0 (CPU-served by default here) | High (50-150) |
| HF Baseline | Mid-size FP16 (~3-4B) | Tens of seconds | Several GB | Several GB, near VRAM ceiling | Low (< 1) |
| AirLLM | 7B+, FP32, CPU-paged | Minutes | High (peaks above the other two) | Near-zero | Very low (< 0.1) |

## Why AirLLM succeeds where standard HF loading fails here

A 7B-parameter model in FP16 is roughly 14 GB — almost double this card's 8 GB of VRAM.
The standard HuggingFace loading path (`AutoModelForCausalLM.from_pretrained(...).to("cuda")`)
has exactly one strategy: load the whole model, then move it to the GPU. There's no partial
mode — it either fits or it raises a CUDA out-of-memory error. On this hardware, that means
the standard path simply cannot run a 7B model at full precision; the only options are
quantizing it (reducing precision) or not running it on the GPU at all.

AirLLM takes the second option to its logical extreme: it never puts the full model on the
GPU (or even fully in RAM). It memory-maps the safetensors checkpoint and streams one
transformer layer at a time through the compute path, discarding each layer's weights after
that layer's forward pass completes. The trade-off is exactly what you'd expect from turning
a parallel-friendly workload into a serial, I/O-bound one: latency goes from seconds to
minutes, because every single token now requires re-reading every layer of the model from
disk. But it never OOMs, regardless of how large the model is relative to available VRAM —
the constraint becomes disk space and patience, not VRAM.

`HardwareProfiler.recommend_quantization()` (see [`shared/hardware_profiler.py`](../src/airllm_benchmark/shared/hardware_profiler.py))
formalizes the *other* answer to this same problem: instead of paging through CPU/disk,
quantize the model down until it fits in VRAM directly. For a 7B model on this card, that
function recommends Q4 (≈3.5 GB) over the default FP16 (14 GB) — a path this project doesn't
take for AirLLM (which always runs FP32 on CPU, by the architecture's own design), but one
that's available for the HF baseline path if a future iteration adds quantized loading.
