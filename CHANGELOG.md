# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [1.00] — 2026-06-17 to 2026-06-23

### Added
- Project skeleton: `uv`-managed package, ruff + pytest + coverage config, CLI entry point
- `BenchmarkSDK` facade + `ApiGatekeeper` rate-limiting/retry layer — no service is called directly
- `OllamaService`, `HFBaselineService`, `AirLLMService` — the three inference methods under benchmark
- `MetricsCollector` (latency/RAM/VRAM capture), `ResultsService` (JSON persistence + comparison reports)
- `ChartService` + `NotebookDataPreparer` — 4 comparison charts, executable analysis notebook
- `HardwareProfiler` — CPU/RAM/GPU detection and `recommend_quantization()`, wired into every CLI run
- `docs/COSTS.md` — real measured cost/resource analysis with optimization recommendations
- GitHub Actions CI workflow, Makefile, MIT `LICENSE`

### Changed
- Model cache relocated from the repo-adjacent `./models` to a configurable `MODELS_DIR`
  (env-overridable), after the default location filled the system drive
- `disk_gb` now measures real on-disk model size per method instead of a stub `0.0`
- Default benchmark model upgraded from `TinyLlama-1.1B` to `microsoft/Phi-3-mini-4k-instruct`
  for the HF baseline once GPU (CUDA) support was enabled

### Fixed
- AirLLM was silently downloading to the OS-default HuggingFace cache instead of the
  configured `models_dir`, because its internal `snapshot_download()` calls never accept a
  `cache_dir` argument — fixed by setting `HUGGINGFACE_HUB_CACHE` early in `load_config()`
- A hardcoded, machine-specific path had been committed to `config/setup.json` — reverted to
  a portable default, real path moved to the gitignored `.env`
- transformers 4.43 compatibility (`torch_dtype=` vs `dtype=`), CUDA/CPU device selection for
  AirLLM's layer-paging decode loop, test isolation issues from PyTorch's C extension

### Verified
- 182 tests passing, 95%+ coverage, 0 ruff errors, all files ≤ 150 lines
- Fresh-clone smoke test: clone → `.env.example` → `.env` → `uv sync` → tests → real run, all green
- Full `--method all` GPU comparison run: Ollama (2.77s), HF Baseline/Phi-3-mini (54.6s, 7.3GB VRAM),
  AirLLM/Mistral-7B (706.7s, 8MB VRAM) — demonstrating AirLLM running a model too large for the GPU
