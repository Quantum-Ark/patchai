"""Unit tests for PatchPilot AI domain models."""

import pytest
from datetime import datetime
from patchpilot.models import (
    Issue,
    AgentState,
    PatchAttempt,
    FailureCategory,
    RecoveryAction,
    RunReport,
    TestExecutionResult,
    ReproductionResult,
    InvestigationPlan,
    VerificationReport,
)


def test_issue_model():
    issue = Issue(
        id="101",
        title="ZeroDivisionError in invoice calculation",
        body="Dividing by items count when cart is empty causes ZeroDivisionError.",
        file_hints=["calc.py"],
        reproduction_command="pytest tests/test_calc.py",
    )
    assert issue.id == "101"
    assert "ZeroDivisionError" in issue.title
    assert issue.file_hints == ["calc.py"]
    assert issue.reproduction_command == "pytest tests/test_calc.py"


def test_test_execution_result():
    res = TestExecutionResult(
        command="pytest tests/ -v",
        exit_code=0,
        stdout="1 passed in 0.05s",
        stderr="",
        duration_seconds=0.05,
        passed=True,
        summary="1 passed",
    )
    assert res.passed is True
    assert res.exit_code == 0
    assert res.command == "pytest tests/ -v"


def test_patch_attempt_and_recovery():
    attempt = PatchAttempt(
        attempt_number=1,
        strategy_description="Add guard clause if count == 0",
        target_file="calc.py",
        original_snippet="return x / count",
        patched_snippet="if count == 0: return 0\nreturn x / count",
        unified_diff="--- a/calc.py\n+++ b/calc.py\n@@ -1 +1,2 @@\n+if count == 0: return 0",
        applied_successfully=True,
        failure_category=FailureCategory.REGRESSION_INTRODUCED,
        recovery_decision=RecoveryAction.ROLLBACK_AND_PIVOT,
        recovery_notes="Attempt 1 broke existing discount test. Rolling back.",
    )
    assert attempt.attempt_number == 1
    assert attempt.failure_category == FailureCategory.REGRESSION_INTRODUCED
    assert attempt.recovery_decision == RecoveryAction.ROLLBACK_AND_PIVOT


def test_run_report():
    issue = Issue(id="1", title="Test Issue", body="Bug details")
    report = RunReport(
        run_id="run-test-01",
        issue=issue,
        final_state=AgentState.VERIFIED,
        success=True,
        total_duration_seconds=1.25,
        neatlogs_trace_id="test-trace-id",
        summary="Bug successfully reproduced, patched, and verified.",
    )
    assert report.run_id == "run-test-01"
    assert report.success is True
    assert report.final_state == AgentState.VERIFIED
    assert report.neatlogs_trace_id == "test-trace-id"
