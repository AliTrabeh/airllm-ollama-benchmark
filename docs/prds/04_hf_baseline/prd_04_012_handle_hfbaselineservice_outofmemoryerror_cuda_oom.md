# PRD-04-012: Handle HFBaselineService OutOfMemoryError (CUDA OOM)

**Group:** 04_hf_baseline
**Type:** impl
**Target file:** `src/airllm_benchmark/services/hf_service.py`
**Status:** DONE

---

## Goal

Catch torch.cuda.OutOfMemoryError and return descriptive error result.

---

## Acceptance Criteria

- [ ] (none)

---

## Dependencies

None

---

## Notes

—
