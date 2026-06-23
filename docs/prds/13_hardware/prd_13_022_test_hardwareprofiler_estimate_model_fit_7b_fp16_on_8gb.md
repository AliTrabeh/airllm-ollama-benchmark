# PRD-13-022: Test HardwareProfiler.estimate_model_fit 7B FP16 on 8GB VRAM = False

**Group:** 13_hardware
**Type:** test
**Target file:** `tests/unit/test_shared/test_hardware_profiler.py`
**Status:** DONE

---

## Goal

7B * 2 bytes = 14GB > 8GB VRAM; verify False returned.

---

## Acceptance Criteria

- [ ] (none)

---

## Dependencies

None

---

## Notes

—
