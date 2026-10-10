# PatchPilot AI — Evaluation & Benchmark Results
*neatHacks 2026 Verification Dossier*

---

## 1. Benchmark Suite Overview

The evaluation suite consists of 3 reproducible evaluation benchmarks located in `benchmarks/`:

1. **Benchmark 1 (Logic Bug):** Unhandled `ZeroDivisionError` in `safe_divide`.
   - **Path:** `benchmarks/case_1_logic_bug/`
   - **Target:** `calc.py`
   - **Reproduction Test:** `test_calc.py`
   - **Expected Result:** Raise `ValueError('Division by zero')` instead of crashing.

2. **Benchmark 2 (Boundary Condition Bug):** `IndexError` on empty list pagination.
   - **Path:** `benchmarks/case_2_boundary_bug/`
   - **Target:** `paginator.py`
   - **Reproduction Test:** `test_paginator.py`
   - **Expected Result:** Return empty list `[]` without accessing out-of-bounds indices.

3. **Benchmark 3 (Regression & Verified Recovery):** Tiered VIP pricing with volume incentives.
   - **Path:** `benchmarks/case_3_regression_recovery/`
   - **Target:** `pricing.py`
   - **Reproduction Test:** `test_reproduction_quantity.py`
   - **Regression Suite:** `test_regression_suite.py`
   - **Expected Result:** Invalidate negative/zero quantity while strictly preserving VIP tier discount percentages.

---

## 2. Experimental Results

| Case | Category | Initial Baseline | Attempt 1 Result | Recovery Action | Attempt 2 Result | Final State | Neatlogs Trace ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** | Logic Bug | FAILED (Code 1) | PASSED | None (Verified) | N/A | **VERIFIED** | `5d82c83f671eb6df7cfba91ec1b11ca0` |
| **Case 2** | Boundary Bug | FAILED (Code 1) | PASSED | None (Verified) | N/A | **VERIFIED** | `2b6091b30df61bb81e05d9cf76f7a6f2` |
| **Case 3** | Regression Recovery | FAILED (Code 1) | FAILED (Regression) | **ROLLBACK & PIVOT** | PASSED | **VERIFIED** | `e8aa42e4f9b8772ebad0f24953c899c7` |

---

## 3. Metrics Summary

- **Verified Repair Rate:** 100% (3 / 3 benchmarks passing)
- **Regression Recovery Rate:** 100% (1 / 1 multi-attempt regression successfully rolled back and recovered)
- **Zero Unverified Claims:** 0% false positives
- **Average Repair Duration:** 3.68 seconds
- **Pytest Unit/Integration Test Coverage:** 18 passed, 0 failed, 71% code coverage
