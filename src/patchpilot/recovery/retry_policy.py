"""
Recovery & Retry Policy.
Classifies execution failures, evaluates budget, and formulates strategic recovery pivots.
"""

from typing import Tuple
from patchpilot.models import TestExecutionResult, FailureCategory, RecoveryAction
from patchpilot.config import config


class RetryPolicy:
    def __init__(self, max_attempts: int = config.max_attempts):
        self.max_attempts = max_attempts

    def classify_failure(self, test_result: TestExecutionResult) -> FailureCategory:
        """Analyze test outputs to classify the root cause of failure."""
        combined = f"{test_result.stdout}\n{test_result.stderr}".lower()

        if "syntaxerror" in combined or "indentationerror" in combined:
            return FailureCategory.SYNTAX_ERROR
        if "modulenotfounderror" in combined or "importerror" in combined:
            return FailureCategory.MISSING_DEPENDENCY
        if "timed out" in combined or "timeout" in combined or test_result.exit_code == -1:
            return FailureCategory.TIMEOUT
        if test_result.exit_code == -2:
            return FailureCategory.INCOMPLETE_PATCH
        if "failed" in combined and "assert" in combined:
            return FailureCategory.TEST_ASSERTION_FAILURE
        if "failed" in combined and ("passed" in combined or "regression" in combined):
            return FailureCategory.REGRESSION_INTRODUCED
        if "error" in combined or "traceback" in combined:
            return FailureCategory.INCOMPLETE_PATCH

        return FailureCategory.TEST_ASSERTION_FAILURE

    def evaluate_recovery(
        self,
        current_attempt: int,
        failure_category: FailureCategory,
        test_result: TestExecutionResult
    ) -> Tuple[RecoveryAction, str]:
        """
        Determine the next recovery action and strategy modification.
        """
        if current_attempt >= self.max_attempts:
            return (
                RecoveryAction.TERMINATE_MAX_BUDGET,
                f"Exhausted maximum retry budget ({self.max_attempts} attempts). Terminating."
            )

        if failure_category == FailureCategory.SYNTAX_ERROR:
            return (
                RecoveryAction.ROLLBACK_AND_PIVOT,
                "Syntax or indentation error detected in patch. Roll back immediately and verify Python AST / syntax correctness."
            )

        if failure_category == FailureCategory.REGRESSION_INTRODUCED:
            return (
                RecoveryAction.ROLLBACK_AND_PIVOT,
                "Patch broke existing test cases. Roll back and narrow the change scope to protect existing behavior."
            )

        if failure_category == FailureCategory.TIMEOUT:
            return (
                RecoveryAction.ROLLBACK_AND_PIVOT,
                "Test execution timed out. Check for infinite loops or blocking calls introduced by patch."
            )

        return (
            RecoveryAction.RETRY_WITH_NEW_STRATEGY,
            "Assertion failure. Roll back and pivot hypothesis: inspect edge cases and boundary inputs."
        )
