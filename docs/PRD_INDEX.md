# PRD Index

**Source:** software_submission_guidelines-V3 §2.3

All per-mechanism PRD files for the airllm-ollama-benchmark project.

---

## PRD Files

| PRD | Title | Status | Priority |
|-----|-------|--------|----------|
| [PRD-01](prds/PRD_01_env_setup.md) | Environment & Project Skeleton Setup | TODO | P0 |
| [PRD-02](prds/PRD_02_ollama_baseline.md) | Ollama Baseline Runner | TODO | P0 |
| [PRD-03](prds/PRD_03_hf_model_selection.md) | HuggingFace Model Selection & HF Baseline | TODO | P0 |
| [PRD-04](prds/PRD_04_airllm_runner.md) | AirLLM CPU Runner | TODO | P0 |
| [PRD-05](prds/PRD_05_metrics_collection.md) | Metrics Collection Service | TODO | P0 |
| [PRD-06](prds/PRD_06_sdk_architecture.md) | SDK Architecture & Gatekeeper | TODO | P1 |
| [PRD-07](prds/PRD_07_results_storage.md) | Results Storage & Comparison Report | TODO | P1 |
| [PRD-08](prds/PRD_08_visualization.md) | Visualization & Results Analysis | TODO | P1 |
| [PRD-09](prds/PRD_09_testing_quality.md) | Testing & Code Quality | TODO | P1 |

---

## Implementation Order

PRDs must be implemented in this order (dependencies flow downward):

```
PRD-01 (Environment)
    └── PRD-06 (SDK Architecture)
            ├── PRD-05 (Metrics Collection)
            ├── PRD-02 (Ollama Baseline)
            ├── PRD-03 (HF Model Selection + Baseline)
            └── PRD-04 (AirLLM Runner)
                        └── PRD-07 (Results Storage)
                                    └── PRD-08 (Visualization)
                                                └── PRD-09 (Testing)
```

---

## Status Legend

- `TODO` — Not started
- `IN_PROGRESS` — Currently being worked on
- `DONE` — Completed and verified
- `BLOCKED` — Waiting on dependency
