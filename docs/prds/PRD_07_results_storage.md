# PRD-07: Results Storage & Comparison Report

**Source files used:**
- L08-summary-Lora-AirLLM-and-HW §9.1 (step 5: compare methods)
- software_submission_guidelines-V3 §9 (research & results), §11 (costs)
- Detailed_Feedback_Report_252608 §Research&Analysis (KEEP-04), §Costs&Pricing (RISK-01)

**Status:** DONE

---

## Goal

Save all benchmark results to structured JSON files in `results/`, generate a comparison
report, and produce the cost/resource breakdown table required to avoid the HW01 grading
deduction for missing cost analysis.

---

## Requirements

### Functional
- Save each `BenchmarkResult` to `results/run_<timestamp>_<method>.json`
- Generate `ComparisonReport` with all three methods side by side
- Save `ComparisonReport` to `results/comparison_<timestamp>.json`
- `ComparisonReport` includes a summary table (markdown formatted)

### ComparisonReport must include (required by L08 §9.1 step 5 + guidelines §11):
- Latency comparison (seconds) across methods
- RAM peak comparison (MB/GB) across methods
- VRAM comparison (if GPU available)
- Tokens/second comparison
- **Cost/resource breakdown** (RISK-01 prevention):
  - Estimated electricity: time × CPU TDP
  - Disk space required per method
  - RAM headroom needed
  - "Is it worth it?" recommendation

---

## Files Expected to be Created or Modified

```
src/airllm_benchmark/models/
└── comparison_report.py            # ComparisonReport dataclass

src/airllm_benchmark/services/
└── results_service.py              # Save/load results, generate report

results/                            # Directory (git-ignored for large results)
└── .gitkeep                        # Keep directory in repo

tests/unit/test_services/
└── test_results_service.py
```

---

## ComparisonReport Structure

```python
@dataclass
class ComparisonReport:
    results: list[BenchmarkResult]  # All benchmark runs
    best_latency: str               # Method with lowest latency
    best_memory: str                # Method with lowest RAM
    summary_table: str              # Markdown table
    cost_breakdown: dict            # Per-method cost estimates
    recommendations: list[str]      # AirLLM trade-off analysis
    timestamp: str
```

### Summary Table Format (Markdown)

| Method | Model | Latency (s) | RAM Peak (MB) | VRAM (MB) | tok/s | Disk (GB) |
|--------|-------|-------------|---------------|-----------|-------|-----------|
| ollama | ... | ... | ... | ... | ... | ... |
| hf_baseline | ... | ... | ... | ... | ... | ... |
| airllm | ... | ... | ... | ... | ... | ... |

---

## Acceptance Criteria

- [ ] Results saved as JSON with all BenchmarkResult fields
- [ ] ComparisonReport generated and saved after all runs
- [ ] Summary table in Markdown format included in report
- [ ] `cost_breakdown` field populated with resource estimates
- [ ] `recommendations` list includes AirLLM trade-off interpretation
- [ ] Unit tests verify save/load roundtrip
- [ ] `results/` directory in repo with `.gitkeep`

---

## Tests / Checks

- `test_results_service.py`:
  - `test_save_and_load_result()` — save BenchmarkResult, load it back, verify equality
  - `test_comparison_report_generated()` — 3 results → ComparisonReport with table
  - `test_cost_breakdown_present()` — report has cost_breakdown with all methods
  - `test_recommendations_present()` — report has at least one recommendation

---

## Grading Risks

- Missing cost breakdown → RISK-01 (Costs & Pricing deduction from feedback)
- Missing interpretation/recommendations → numbers without analysis (feedback KEEP-04)
- Results not saved → grader cannot verify experiment ran
- No comparison table → assignment step 5 not satisfied (L08 §9.1)
