# PRD-08: Visualization & Results Analysis

**Source files used:**
- software_submission_guidelines-V3 §9.3 (visualization), §9.2 (results notebook)
- Detailed_Feedback_Report_252608 §UI/UX (RISK-02), §Research&Analysis (KEEP-04)
- L08-summary-Lora-AirLLM-and-HW §9.1 (step 5: measure and compare)

**Status:** TODO

---

## Goal

Create professional visualizations of benchmark results and a Jupyter/results analysis
notebook. This directly addresses RISK-02 (UI/UX not communicated) by providing visual
evidence that makes results understandable without running the code.

---

## Background (from guidelines §9.3)

> "Visualization quality is a key tool for conveying research findings."

Required chart types include: Bar charts, Line charts, Scatter plots, Heatmaps, Box plots,
Waterfall charts. Requirements: labeled axes, legends, clear titles, high resolution.

---

## Required Visualizations

### Chart 1: Latency Comparison (Bar Chart)
- X axis: Method (Ollama, HF Baseline, AirLLM)
- Y axis: Latency in seconds
- Title: "Inference Latency Comparison: Ollama vs HF Baseline vs AirLLM"
- Shows: AirLLM is slower but functional for large models

### Chart 2: Memory Usage Comparison (Grouped Bar Chart)
- X axis: Method
- Y axis: Peak RAM (MB) + VRAM (MB) as grouped bars
- Title: "Peak Memory Usage per Method"
- Shows: AirLLM uses dramatically less RAM than HF baseline

### Chart 3: Tokens/Second Comparison (Bar Chart)
- X axis: Method
- Y axis: Tokens per second
- Shows: throughput trade-off

### Chart 4: Trade-off Summary (Scatter Plot)
- X axis: Latency (s)
- Y axis: RAM Peak (MB)
- Annotated with method names
- Shows: AirLLM trades latency for memory efficiency

### Chart 5: Resource Summary Table (saved as PNG or in notebook)
- Markdown table rendered visually
- Method, Model, Latency, RAM, VRAM, Cost estimate

---

## Notebook Requirements (from guidelines §9.2)

File: `notebooks/results_analysis.ipynb`

Sections:
1. **Setup** — load results from `results/` directory
2. **Experiment Overview** — what was tested, why
3. **Latency Analysis** — Chart 1 + interpretation
4. **Memory Analysis** — Chart 2 + interpretation
5. **Throughput Analysis** — Chart 3
6. **Trade-off Analysis** — Chart 4 + discussion
7. **Cost & Resource Analysis** — cost breakdown table
8. **Conclusions** — when to use AirLLM, limitations, recommendations

---

## Files Expected to be Created or Modified

```
notebooks/
└── results_analysis.ipynb          # Main analysis notebook

src/airllm_benchmark/services/
└── visualization_service.py        # Generates and saves charts

assets/
├── chart_latency.png
├── chart_memory.png
├── chart_throughput.png
└── chart_tradeoff.png

tests/unit/test_services/
└── test_visualization_service.py
```

---

## Acceptance Criteria

- [ ] All 4 charts generated and saved to `assets/`
- [ ] Charts have: title, labeled axes, legend, high resolution (≥150 DPI)
- [ ] Notebook runs end-to-end with `uv run jupyter nbconvert --to notebook --execute`
- [ ] Charts embedded in notebook
- [ ] "Conclusions" section provides interpretation (not just numbers)
- [ ] Charts referenced in README for RISK-02 prevention

---

## Tests / Checks

- `test_visualization_service.py`:
  - `test_chart_files_created()` — mock results, verify PNG files saved
  - `test_chart_has_labels()` — verify axes and title populated
  - `test_empty_results_handled()` — empty list → clear error, not crash

---

## Grading Risks

- No visualizations → guidelines §9.3 requirement not met
- No notebook → guidelines §9.2 requirement not met
- Charts without labels/titles → unprofessional, quality deduction
- No interpretation in notebook → KEEP-04 violation (analysis must interpret, not just report)
- Screenshots not in README → RISK-02 (UI/UX not communicated to grader)
