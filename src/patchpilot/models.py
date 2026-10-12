"""
Core Pydantic domain models for PatchPilot AI.
Defines schemas for issues, investigations, patch attempts, test executions, and verified recovery.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentState(str, Enum):
    IDLE = "IDLE"
    INTAKE = "INTAKE"
    INVESTIGATING = "INVESTIGATING"
    REPRODUCING = "REPRODUCING"
    PATCHING = "PATCHING"
    TESTING = "TESTING"
    EVALUATING = "EVALUATING"
    RECOVERING = "RECOVERING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class FailureCategory(str, Enum):
    NONE = "NONE"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    TEST_ASSERTION_FAILURE = "TEST_ASSERTION_FAILURE"
    REGRESSION_INTRODUCED = "REGRESSION_INTRODUCED"
    TIMEOUT = "TIMEOUT"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    INCOMPLETE_PATCH = "INCOMPLETE_PATCH"


class RecoveryAction(str, Enum):
    RETRY_WITH_NEW_STRATEGY = "RETRY_WITH_NEW_STRATEGY"
    ROLLBACK_AND_PIVOT = "ROLLBACK_AND_PIVOT"
    REFINE_TEST = "REFINE_TEST"
    TERMINATE_MAX_BUDGET = "TERMINATE_MAX_BUDGET"


class Issue(BaseModel):
    id: str
    title: str
    body: str
    repo_url: Optional[str] = None
    file_hints: List[str] = Field(default_factory=list)
    reproduction_command: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)


class TestExecutionResult(BaseModel):
    __test__ = False
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    passed: bool
    summary: str


class ReproductionResult(BaseModel):
    reproduced: bool
    command_executed: str
    baseline_result: TestExecutionResult
    failure_details: str

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)


class InvestigationPlan(BaseModel):
    root_cause_hypothesis: str
    relevant_files: List[str]
    proposed_solution: str
    test_strategy: str

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)


class PatchAttempt(BaseModel):
    attempt_number: int
    strategy_description: str
    target_file: str
    original_snippet: str
    patched_snippet: str
    unified_diff: str
    applied_successfully: bool
    test_result: Optional[TestExecutionResult] = None
    failure_category: FailureCategory = FailureCategory.NONE
    recovery_decision: Optional[RecoveryAction] = None
    recovery_notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)


class VerificationReport(BaseModel):
    acceptance_passed: bool
    regression_passed: bool
    all_tests_passed: bool
    acceptance_summary: str
    regression_summary: str
    evidence_diff: str
    verified_at: datetime = Field(default_factory=datetime.now)

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)


class RunReport(BaseModel):
    run_id: str
    issue: Issue
    final_state: AgentState
    reproduction: Optional[ReproductionResult] = None
    investigation: Optional[InvestigationPlan] = None
    attempts: List[PatchAttempt] = Field(default_factory=list)
    verification: Optional[VerificationReport] = None
    neatlogs_trace_id: Optional[str] = None
    entire_checkpoint_id: Optional[str] = None
    total_duration_seconds: float = 0.0
    success: bool = False
    summary: str = ""

    def model_dump_json(self, **kwargs) -> str:
        return self.json(**kwargs)

    def model_dump(self, **kwargs) -> dict:
        return self.dict(**kwargs)
