# PRD-05: Metrics Collection Service

**Source files used:**
- L08-summary-Lora-AirLLM-and-HW §9.1 (step 5: what to measure)
- software_submission_guidelines-V3 §9 (research and results), §11 (costs)
- Detailed_Feedback_Report_252608 §Costs&Pricing (RISK-01)

**Status:** DONE

---

## Goal

Implement a unified metrics collection service that captures timing, memory, and token
statistics consistently across all three inference methods (Ollama, HF baseline, AirLLM).

---

## Required Metrics (from L08-summary §9.1 step 5)

The assignment explicitly requires measuring and comparing:
- **Response time** (total wall-clock seconds)
- **Memory consumption** (RAM in GB, VRAM in GB)
- **Run time** (same as response time for single inference)
- Comparison across: CPU baseline, GPU baseline, AirLLM

Additional resource metrics (required by guidelines §11 to avoid RISK-01 from feedback):
- **Disk usage** (GB consumed by model files)
- **Tokens per second** (throughput)
- **Cost estimate** (compute time × electricity estimate)

---

## Requirements

### Functional
- `MetricsCollector` context manager: captures timing and memory around a block
- Captures: start_ram_mb, peak_ram_mb, end_ram_mb (via psutil)
- Captures: start_vram_mb, peak_vram_mb (via torch.cuda if available, else 0)
- Captures: wall_clock_seconds (perf_counter)
- Returns all metrics as a `MetricsSnapshot` dataclass

### Non-Functional
- Works on CPU-only machines (no CUDA requirement)
- Gracefully handles torch not installed (VRAM metrics = 0)
- Sampling interval configurable

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/services/
└── metrics_service.py              # MetricsCollector context manager

src/airllm_benchmark/models/
├── benchmark_result.py             # BenchmarkResult dataclass (all metric fields)
└── comparison_report.py            # ComparisonReport dataclass

tests/unit/test_services/
└── test_metrics_service.py         # Tests for metrics capture
```

---

## BenchmarkResult Dataclass

```python
@dataclass
class BenchmarkResult:
    method: str          # "ollama" | "hf_baseline" | "airllm"
    model_id: str
    prompt: str
    output: str
    latency_s: float     # Total wall-clock seconds
    ram_peak_mb: float   # Peak RAM in MB
    vram_peak_mb: float  # Peak VRAM in MB (0 if CPU-only)
    tokens_generated: int
    tokens_per_second: float
    disk_gb: float       # Model size on disk
    cost_estimate: str   # e.g. "~0.02 kWh @ 65W TDP"
    error: str | None
    timestamp: str       # ISO8601
```

---

## Acceptance Criteria

- [ ] `MetricsCollector` captures timing with < 1ms overhead
- [ ] `ram_peak_mb` reflects actual peak, not just before/after delta
- [ ] Works on machine without CUDA (`vram_peak_mb = 0.0`)
- [ ] `BenchmarkResult` serializes cleanly to/from JSON
- [ ] Unit tests pass without requiring GPU or large models
- [ ] `cost_estimate` field populated (even rough estimate)

---

## Tests / Checks

- `test_metrics_service.py`:
  - `test_timing_captured()` — sleep 0.1s, verify latency_s ≈ 0.1
  - `test_ram_captured()` — allocate array, verify ram_peak increases
  - `test_no_cuda_graceful()` — torch.cuda not available → vram=0, no crash
  - `test_serialization()` — BenchmarkResult → JSON → BenchmarkResult roundtrip

---

## Grading Risks

- Missing memory measurements → RISK-01 cost/resource deduction (feedback)
- No cost_estimate field → RISK-01 deduction
- Metrics only captured at start/end (not peak) → inaccurate RAM reporting
- Not comparing methods → missing the core comparison assignment requires (L08 §9.1 step 5)
