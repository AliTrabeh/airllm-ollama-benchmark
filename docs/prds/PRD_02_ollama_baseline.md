# PRD-02: Ollama Baseline Runner

**Source files used:**
- L08-summary-Lora-AirLLM-and-HW §6 (Ollama: local inference), §9.1 (step 2)
- software_submission_guidelines-V3 §4 (SDK), §5 (Gatekeeper)

**Status:** TODO

---

## Goal

Implement a service that calls Ollama's local API, verifies the pipeline works end-to-end,
and captures timing + memory metrics. This is the "normal inference, small model" baseline.

---

## Background (from L08-summary §6)

Ollama is the "Netflix of models" — it reads GGUF files, loads and serves them locally,
and exposes an OpenAI-compatible REST API on `localhost:11434`.

Key Ollama commands:
```bash
ollama pull llama3          # Download model
ollama run llama3 "prompt"  # One-shot inference
ollama serve                # Exposes API on localhost:11434
```

The API endpoint for inference: `POST http://localhost:11434/api/generate`

---

## Requirements

### Functional
- Call Ollama API with a user-provided prompt and model name
- Capture: wall-clock latency (seconds), token count, tokens/second
- Capture: RAM usage before and after inference (via psutil)
- Handle: Ollama not running → clear error message
- Handle: Model not installed → clear error message with `ollama pull` hint
- Return a `BenchmarkResult` dataclass

### Non-Functional
- All API calls routed through Gatekeeper
- No hardcoded URL — reads from `config/setup.json`
- Model name configurable via `.env` or CLI arg
- HTTP timeout configurable

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/services/
└── ollama_service.py               # OllamaService class

src/airllm_benchmark/models/
└── benchmark_result.py             # BenchmarkResult dataclass

tests/unit/test_services/
└── test_ollama_service.py          # Unit tests with mocked HTTP

config/setup.json                   # Add: ollama_url, default_ollama_model
```

---

## Acceptance Criteria

- [ ] `OllamaService.run(prompt, model, max_tokens)` returns `BenchmarkResult`
- [ ] `BenchmarkResult.latency_s` > 0 after a successful run
- [ ] When Ollama is not running, raises `OllamaConnectionError` with helpful message
- [ ] All HTTP calls go through `Gatekeeper.execute()`
- [ ] No hardcoded `localhost:11434` in service — reads from config
- [ ] Unit tests pass with mocked HTTP responses
- [ ] Test coverage ≥ 85% for `ollama_service.py`

---

## Tests / Checks

- `test_ollama_service.py`:
  - `test_successful_inference()` — mocked response, verifies BenchmarkResult fields
  - `test_ollama_not_running()` — connection refused → OllamaConnectionError
  - `test_model_not_found()` — 404 response → ModelNotFoundError with pull hint
  - `test_metrics_captured()` — latency_s > 0, tokens_generated > 0

---

## Grading Risks

- Ollama not verified as working → missing step 2 of assignment (L08 §9.1)
- No memory measurement → missing required metric (L08 §9.1 step 5)
- Direct API call without Gatekeeper → architecture violation
- Missing error handling → fragile pipeline
