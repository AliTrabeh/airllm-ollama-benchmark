# PRD-03: HuggingFace Model Selection & HF Baseline

**Source files used:**
- L08-summary-Lora-AirLLM-and-HW §4 (Model selection), §9.1 (steps 1 and 3)
- software_submission_guidelines-V3 §4 (SDK), §7.4 (secrets/tokens)

**Status:** TODO

---

## Goal

Select appropriate HuggingFace models for the experiment (small for pipeline verification,
large for the "too big" baseline) and implement a standard HF inference service that
demonstrates normal model loading failing or being impractically slow for large models.

---

## Background (from L08-summary §4.1)

Model selection criteria (lecture §4.1):
1. **Task** — choose a task (text generation / causal LM is simplest)
2. **License** — verify license allows use
3. **Format** — SafeTensors preferred for AirLLM compatibility
4. **Size** — must be too large for available VRAM/RAM for the "baseline failure" demo
5. **Latency** — expected response time

> From lecture: "A large model isn't necessarily better for the task. Model size is critical."

> From assignment tips (§9.1): "Start with a small model and small max_new_tokens to verify
> the pipeline works before trying heavy models."

---

## Recommended Model Strategy

### Small model (pipeline verification):
- Use for Ollama baseline and initial testing
- ~1-3B parameters, fits easily in RAM
- Example: `tinyllama` (1.1B), `phi-2` (2.7B), `gemma-2b`

### Large model (AirLLM experiment):
- Must be too large for available GPU VRAM or normal CPU RAM
- Use SafeTensors format (required by AirLLM)
- ~7B+ parameters
- Example: `meta-llama/Llama-2-7b-hf`, `mistralai/Mistral-7B-v0.1`, `tiiuae/falcon-7b`
- Actual model choice depends on available disk space and HF token access

---

## Requirements

### Functional
- `HFBaselineService.run(prompt, model_id, max_tokens)` attempts normal model loading
- Captures: RAM/VRAM before and after loading, latency, tokens generated
- If model doesn't fit → catches OOM error, returns `BenchmarkResult` with error field set
- HF token loaded from environment variable `HF_TOKEN` only
- Model cached to configurable directory (not hardcoded path)

### Non-Functional
- Token NEVER logged or printed
- Model cache directory configurable via `MODELS_DIR` env var
- Download only triggered once (use cached weights)
- Small model verified first (fast, no GPU needed)

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/services/
└── hf_baseline_service.py          # HFBaselineService class

tests/unit/test_services/
└── test_hf_baseline_service.py     # Unit tests with mocked transformers

config/setup.json                   # Add: small_model_id, large_model_id, models_dir
docs/
└── MODEL_SELECTION.md              # Document chosen models, license, rationale
```

---

## Acceptance Criteria

- [ ] `HFBaselineService.run()` returns `BenchmarkResult` in both success and OOM cases
- [ ] OOM case: `BenchmarkResult.error` is populated with clear message
- [ ] OOM case: RAM/VRAM at time of failure is still recorded
- [ ] HF_TOKEN loaded via `os.environ.get("HF_TOKEN")` — never hardcoded
- [ ] `MODEL_SELECTION.md` documents: chosen models, licenses, sizes, rationale
- [ ] Unit tests pass with mocked `AutoModelForCausalLM`
- [ ] Test coverage ≥ 85% for `hf_baseline_service.py`

---

## Tests / Checks

- `test_hf_baseline_service.py`:
  - `test_small_model_inference()` — mocked, verifies BenchmarkResult fields
  - `test_oom_handled_gracefully()` — mock raises RuntimeError("CUDA out of memory")
  - `test_token_not_in_logs()` — verify HF_TOKEN not in any log output
  - `test_memory_captured_on_oom()` — RAM/VRAM recorded even on failure

---

## Grading Risks

- HF token exposed in logs → security violation, automatic deduction
- Large model not demonstrating failure → missing step 3 of assignment (L08 §9.1)
- No license documentation → professional standard not met (L08 §4.2)
- Missing OOM handling → crashes instead of graceful baseline measurement
- Using newest Python causing transformers incompatibility → pipeline broken
