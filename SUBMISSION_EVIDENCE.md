# PatchPilot AI — neatHacks 2026 Submission Evidence & Verification Dossier

---

## 1. Project Information
- **Project Name:** PatchPilot AI
- **Repository Path:** `c:\Users\Abhishek\Downloads\patchpilotai`
- **Git Branch:** `main`
- **Initial Commit SHA:** `3765fbe568c838beaff0f30e67248f878d70f030`
- **Agent Integration:** Antigravity CLI / Codex (via Entire CLI 0.11.4)
- **Core Differentiator:** **Verified Recovery** — autonomous bug reproduction, failure classification, automated rollback on regressions, strategic pivots, and dual-suite independent verification.

---

## 2. Neatlogs Integration Evidence
- **Neatlogs Project ID:** `b0860223-3c80-445d-a3f1-3002c0643197`
- **Ingestion Endpoint:** `https://ingest.neatlogs.com/v1/trace`
- **Authentication:** `Authorization: Bearer $NEATLOGS_API_KEY` (configured via `.env`)
- **Verified Trace IDs Sent to Neatlogs Ingestion:**
  - **Flagship Verified Recovery Showcase:** `1fd1807e23cac2b5d2c81c9fbb12faf3` (HTTP 200 OK)
  - **Benchmark Case 1 (Logic Bug):** `5d82c83f671eb6df7cfba91ec1b11ca0` (HTTP 200 OK)
  - **Benchmark Case 2 (Boundary Bug):** `2b6091b30df61bb81e05d9cf76f7a6f2` (HTTP 200 OK)
  - **Benchmark Case 3 (Regression Recovery):** `e8aa42e4f9b8772ebad0f24953c899c7` (HTTP 200 OK)
- **Instrumentation Highlights:**
  - One-shot initialization via `NeatlogsTracer` and `TraceBuilder`.
  - Granular workflow spans: `baseline_reproduction`, `generate_patch_attempt_<n>`, `test_run_attempt_<n>`, `rollback_attempt_<n>`, `regression_run_attempt_<n>`, and `independent_verification`.
  - Token tracking and duration captured per span without leaking sensitive repo secrets or credentials.
  - Safe offline fallback when credentials are absent.

---

## 3. Entire CLI Integration Evidence
- **Entire CLI Version:** `0.11.4` (windows/amd64)
- **Agent Integration:** `entire enable --agent antigravity`
  - Output:
    ```
    Agent: Antigravity
    Installed 3 hooks for Antigravity CLI
    Configured project: .entire/settings.json
    ```
- **Entire Status:**
  - Output:
    ```
    ● Enabled · branch main
    Agents · Antigravity
    ```
- **Entire Graph Plugin:**
  - Installed: `entire-graph v0.4.0`
  - Command run: `entire graph init-agents --repo .`
  - Output:
    ```
    wrote .entire\graph-agent.md
    updated AGENTS.md
    updated CLAUDE.md
    ```
- **Checkpoint & Commit Linkage:**
  - Commit SHA: `3765fbe568c838beaff0f30e67248f878d70f030`
  - Status: The codebase is fully committed and synchronized with Entire configuration files (`.entire/settings.json`, `.entire/graph-agent.md`, `.entire/.gitignore`).
  - **Authenticated User:** `github:ABHISHEK-DBZ` (Abhishek Jha)
  - **Active Session ID:** `962e40f4-2378-4cff-8c3c-c3802c4a26da` (Agent: Antigravity)
  - **Authentication Status:** Verified & Logged in (Token stored in Windows Credential Manager). Continuous session tracking active.

---

## 4. Benchmark & Verified Recovery Evaluation Results

All 3 reproducible benchmark cases executed with 100% pass rate:

| Benchmark Case | Defect Type | Attempts | Recovery Demonstrated | Outcome | Neatlogs Trace ID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1: Logic Bug** | Unhandled `ZeroDivisionError` in `safe_divide` | 1 | Direct Fix | **[OK] VERIFIED** | `5d82c83f671eb6df7cfba91ec1b11ca0` |
| **Case 2: Boundary Bug** | `IndexError` on empty list pagination (`page=1`) | 1 | Direct Fix | **[OK] VERIFIED** | `2b6091b30df61bb81e05d9cf76f7a6f2` |
| **Case 3: Regression Recovery** | Pricing engine validation that broke VIP tiers | 2 | **YES (Multi-Attempt)** | **[OK] VERIFIED** | `e8aa42e4f9b8772ebad0f24953c899c7` |

### Detailed Recovery Trace of Case 3:
1. **Initial State:** Baseline test fails with `DID NOT RAISE ValueError` when quantity <= 0.
2. **Attempt #1:** Naive patch validates quantity, but breaks tier discount calculation.
3. **Regression Detection:** Regression test suite fails (`calculate_tiered_price(100.0, "gold", 1) == 100.0 != 80.0`).
4. **Classification & Rollback:** Classified as `REGRESSION_INTRODUCED`. File `pricing.py` is instantly restored to clean baseline via `PatchTool.rollback()`.
5. **Strategy Pivot:** Recovery policy prompts the agent: *"Patch broke existing test cases. Roll back and narrow the change scope to protect existing behavior."*
6. **Attempt #2:** Precision fix validates quantity while preserving tier multipliers.
7. **Verification:** Both acceptance test and regression suite pass (100% clean). State transitions to `VERIFIED`.

---

## 5. Automated Test Suite Results
- **Framework:** `pytest 9.1.1` with `pytest-cov 7.1.0`
- **Total Tests:** 18
- **Passed:** 18 (100%)
- **Failed:** 0
- **Warnings:** 0
- **Overall Code Coverage:** 71%

```
tests/test_models.py::test_issue_model PASSED                            [  5%]
tests/test_models.py::test_test_execution_result PASSED                  [ 11%]
tests/test_models.py::test_patch_attempt_and_recovery PASSED             [ 16%]
tests/test_models.py::test_run_report PASSED                             [ 22%]
tests/test_orchestrator.py::test_orchestrator_recovers_from_regression_in_temp_repo PASSED [ 27%]
tests/test_patch.py::test_apply_replacement_and_rollback PASSED          [ 33%]
tests/test_patch.py::test_rollback_all PASSED                            [ 38%]
tests/test_patch.py::test_missing_snippet_fails_safely PASSED            [ 44%]
tests/test_recovery.py::test_retry_policy_classification_syntax_error PASSED [ 50%]
tests/test_recovery.py::test_retry_policy_budget_exhaustion PASSED       [ 55%]
tests/test_recovery.py::test_checkpoint_store_sqlite PASSED              [ 61%]
tests/test_state_machine.py::test_valid_happy_path_transitions PASSED    [ 66%]
tests/test_state_machine.py::test_recovery_cycle_transitions PASSED      [ 72%]
tests/test_state_machine.py::test_invalid_transition_raises PASSED       [ 77%]
tests/test_state_machine.py::test_can_transition_to PASSED               [ 83%]
tests/test_tracing.py::test_tracer_initialization_without_key PASSED     [ 88%]
tests/test_tracing.py::test_tracer_lifecycle_with_mocked_network PASSED  [ 94%]
tests/test_tracing.py::test_tracer_network_failure_is_graceful PASSED    [100%]

============================= 18 passed in 7.69s ==============================
```

---

## 6. Submission Checklist

- [x] **Working local prototype implemented and tested** (`patchpilot` CLI, orchestrator, state machine).
- [x] **Core differentiator demonstrated** (genuine recovery with automated rollback on regressions).
- [x] **Neatlogs observability integrated and verified** (live 200 OK trace ingestion).
- [x] **Entire CLI configured & enabled** (`entire enable --agent antigravity`, `graph` plugin installed).
- [x] **Git commit created** (Commit SHA: `3765fbe568c838beaff0f30e67248f878d70f030`).
- [x] **3 reproducible evaluation benchmarks created and passing**.
- [x] **3-minute demo script completed** (`DEMO_SCRIPT.md`).
- [x] **Full business plan and financial model created** (`BUSINESS_PLAN.md`).
- [x] **Clean README with architecture diagram** (`README.md`).
- [x] **Secrets protected** (`.env` excluded from version control; zero hardcoded keys).
