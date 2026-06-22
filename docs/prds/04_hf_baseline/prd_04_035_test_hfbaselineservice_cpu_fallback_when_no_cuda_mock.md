# PRD-04-035: Test HFBaselineService CPU fallback when no CUDA (mock)

**Group:** 04_hf_baseline
**Type:** test
**Target file:** `tests/unit/test_services/test_hf_service.py`
**Status:** DONE

---

## Goal

Mock torch.cuda.is_available to False; verify device is 'cpu'.

---

## Acceptance Criteria

- [ ] (none)

---

## Dependencies

None

---

## Notes

—
