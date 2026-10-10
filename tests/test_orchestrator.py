"""Integration tests for PatchPilotOrchestrator and autonomous verified recovery loop."""

import pytest
import sys
from pathlib import Path
from patchpilot.models import Issue, FailureCategory, RecoveryAction, AgentState
from patchpilot.orchestrator import PatchPilotOrchestrator
from patchpilot.llm.provider import MockLLMProvider
from patchpilot.recovery.checkpoint import CheckpointStore


def test_orchestrator_recovers_from_regression_in_temp_repo(tmp_path: Path):
    """
    Simulate a scenario where Attempt 1 fails, triggering rollback and recovery policy,
    and Attempt 2 provides the genuine fix that passes verification.
    """
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Target module
    target_code = (
        "def compute_discount(price: float, discount_pct: float) -> float:\n"
        "    return price - (price * (discount_pct / 100.0))\n"
    )
    (src_dir / "discount.py").write_text(target_code, encoding="utf-8")

    # Issue with reproduction test
    test_code = (
        "import pytest\n"
        "from src.discount import compute_discount\n\n"
        "def test_negative_discount_raises():\n"
        "    with pytest.raises(ValueError):\n"
        "        compute_discount(100.0, -10.0)\n"
    )
    (tests_dir / "test_discount.py").write_text(test_code, encoding="utf-8")

    issue = Issue(
        id="ISSUE-42",
        title="ValueError on negative discount percentage",
        body="Negative discount_pct should raise ValueError.",
        file_hints=["src/discount.py"],
        reproduction_command=f'"{sys.executable}" -m pytest tests/test_discount.py -v',
    )

    # Attempt 1: broken patch that raises RuntimeError
    attempt_1_patch = (
        "TARGET_FILE: src/discount.py\n"
        "ORIGINAL_CODE: return price - (price * (discount_pct / 100.0))\n"
        "PATCHED_CODE: raise RuntimeError('Broken first attempt')\n"
    )

    # Attempt 2: correct patch that checks discount_pct < 0 and raises ValueError
    attempt_2_patch = (
        "TARGET_FILE: src/discount.py\n"
        "ORIGINAL_CODE: return price - (price * (discount_pct / 100.0))\n"
        "PATCHED_CODE: if discount_pct < 0:\n        raise ValueError('Negative discount')\n    return price - (price * (discount_pct / 100.0))\n"
    )

    mock_llm = MockLLMProvider(
        sequential_patches=[attempt_1_patch, attempt_2_patch]
    )

    db_path = tmp_path / "checkpoints.db"
    store = CheckpointStore(db_path)

    orchestrator = PatchPilotOrchestrator(
        repo_dir=tmp_path,
        llm_provider=mock_llm,
        checkpoint_store=store,
    )

    report = orchestrator.run(issue)

    # Assertions
    assert report.success is True
    assert report.final_state == AgentState.VERIFIED
    assert len(report.attempts) == 2

    # Attempt 1 failed, rolled back, and triggered recovery pivot
    att1 = report.attempts[0]
    assert att1.attempt_number == 1
    assert att1.test_result.passed is False
    assert att1.recovery_decision in (RecoveryAction.ROLLBACK_AND_PIVOT, RecoveryAction.RETRY_WITH_NEW_STRATEGY)

    # Attempt 2 passed and verified
    att2 = report.attempts[1]
    assert att2.attempt_number == 2
    assert att2.test_result.passed is True

    # Saved in SQLite
    saved_runs = store.list_runs()
    assert len(saved_runs) == 1
    assert saved_runs[0]["success"] == 1
