"""Unit tests for recovery policy and SQLite checkpoint persistence."""

import pytest
from pathlib import Path
from patchpilot.models import (
    Issue,
    AgentState,
    PatchAttempt,
    FailureCategory,
    RecoveryAction,
    RunReport,
    TestExecutionResult,
)
from patchpilot.recovery.retry_policy import RetryPolicy
from patchpilot.recovery.checkpoint import CheckpointStore


def test_retry_policy_classification_syntax_error():
    policy = RetryPolicy(max_attempts=3)
    acceptance = TestExecutionResult(
        command="pytest",
        exit_code=1,
        stdout="SyntaxError: invalid syntax in math.py",
        stderr="",
        duration_seconds=0.1,
        passed=False,
        summary="Failed with syntax error",
    )
    category = policy.classify_failure(acceptance)
    assert category == FailureCategory.SYNTAX_ERROR

    action, guidance = policy.evaluate_recovery(
        current_attempt=1,
        failure_category=category,
        test_result=acceptance,
    )
    assert action == RecoveryAction.ROLLBACK_AND_PIVOT
    assert "Syntax or indentation error" in guidance


def test_retry_policy_budget_exhaustion():
    policy = RetryPolicy(max_attempts=3)
    acceptance = TestExecutionResult(
        command="pytest",
        exit_code=1,
        stdout="FAILED test_calc",
        stderr="",
        duration_seconds=0.1,
        passed=False,
        summary="Assertion error",
    )
    category = policy.classify_failure(acceptance)
    action, guidance = policy.evaluate_recovery(
        current_attempt=3,
        failure_category=category,
        test_result=acceptance,
    )
    assert action == RecoveryAction.TERMINATE_MAX_BUDGET
    assert "Exhausted maximum retry budget" in guidance


def test_checkpoint_store_sqlite(tmp_path: Path):
    db_file = tmp_path / "checkpoints.db"
    store = CheckpointStore(db_file)

    issue = Issue(id="TEST-1", title="Sample Issue", body="Description")
    attempt = PatchAttempt(
        attempt_number=1,
        strategy_description="Fix off-by-one index",
        target_file="test.py",
        original_snippet="x[i+1]",
        patched_snippet="x[i]",
        unified_diff="--- a/test.py\n+++ b/test.py",
        applied_successfully=True,
    )
    report = RunReport(
        run_id="run-123",
        issue=issue,
        final_state=AgentState.VERIFIED,
        attempts=[attempt],
        total_duration_seconds=1.5,
        neatlogs_trace_id="trace-abc",
        success=True,
        summary="Verified successfully",
    )

    store.save_run(report)

    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0]["run_id"] == "run-123"
    assert runs[0]["success"] == 1
    assert runs[0]["neatlogs_trace_id"] == "trace-abc"

    run_detail = store.get_run("run-123")
    assert run_detail is not None
    assert run_detail["run_id"] == "run-123"
    assert len(run_detail["attempts"]) == 1
    assert run_detail["attempts"][0]["target_file"] == "test.py"
