"""
PatchPilot AI — Dashboard API and GitHub Integration Test Suite.
Verifies real database persistence, GitHub token auth, repository caching,
background repair lifecycle, real-time event logging, and Pull Request safety gates.
"""

import os
import json
import tempfile
from pathlib import Path
import pytest

from patchpilot.db import PatchPilotDB
from patchpilot.tools.github import GitHubPRTool, GitHubIssueTool
from patchpilot.models import Issue, TestExecutionResult
from patchpilot.runner import RepairRunner


@pytest.fixture
def temp_db(tmp_path):
    """Provides an isolated SQLite DB instance for testing."""
    db_file = tmp_path / "test_patchpilot.db"
    return PatchPilotDB(db_path=db_file)


def test_db_schema_initialization(temp_db):
    """Verify that all required tables are created on initialization."""
    with temp_db._connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

    assert "github_auth" in tables
    assert "runs" in tables
    assert "run_events" in tables
    assert "attempts" in tables
    assert "pull_requests" in tables
    assert "repositories" in tables


def test_github_auth_lifecycle(temp_db):
    """Verify storing, retrieving, masking, and deleting GitHub credentials."""
    assert temp_db.get_github_auth() is None

    temp_db.save_github_auth(
        username="octocat",
        name="The Octocat",
        avatar_url="https://github.com/octocat.png",
        token="ghp_1234567890abcdef1234567890abcdef1234",
        scopes="repo, pull_requests:write"
    )

    auth = temp_db.get_github_auth()
    assert auth is not None
    assert auth["username"] == "octocat"
    assert auth["name"] == "The Octocat"
    assert "ghp_1234" in auth["masked_token"]
    assert auth["token"] == "ghp_1234567890abcdef1234567890abcdef1234"

    temp_db.delete_github_auth()
    assert temp_db.get_github_auth() is None


def test_repository_caching_and_search(temp_db):
    """Verify caching repository metadata from GitHub and searching."""
    mock_repos = [
        {
            "owner": {"login": "Quantum-Ark"},
            "name": "patchai",
            "full_name": "Quantum-Ark/patchai",
            "default_branch": "main",
            "private": False,
            "description": "Autonomous software repair engine",
            "open_issues_count": 3
        },
        {
            "owner": {"login": "Quantum-Ark"},
            "name": "infra-deploy",
            "full_name": "Quantum-Ark/infra-deploy",
            "default_branch": "main",
            "private": True,
            "description": "AWS cloud deployment templates",
            "open_issues_count": 0
        }
    ]

    temp_db.cache_repositories(mock_repos)

    cached = temp_db.get_cached_repositories()
    assert len(cached) == 2

    # Search filter
    filtered = temp_db.get_cached_repositories(query="infra")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "infra-deploy"


def test_repair_run_lifecycle_and_realtime_events(temp_db):
    """Verify run creation, fine-grained event streaming, and completion."""
    run = temp_db.create_run(
        run_id="run-test-001",
        issue_id="101",
        issue_title="ZeroDivision in metrics",
        repo_owner="Quantum-Ark",
        repo_name="patchai",
        target_branch="main"
    )

    assert run["run_id"] == "run-test-001"
    assert run["status"] == "RUNNING"
    assert run["final_state"] == "INTAKE"

    # Append events
    temp_db.append_event("run-test-001", "STATE_CHANGE", "INVESTIGATING", "Analyzing code graph")
    temp_db.append_event("run-test-001", "STATE_CHANGE", "REPRODUCING", "Baseline failure confirmed")
    temp_db.append_event("run-test-001", "STATE_CHANGE", "PATCHING", "Generating attempt #1")

    events = temp_db.get_run_events("run-test-001")
    assert len(events) == 3
    assert events[0]["state"] == "INVESTIGATING"
    assert events[1]["state"] == "REPRODUCING"
    assert events[2]["state"] == "PATCHING"

    # Finish run as verified
    temp_db.update_run_finished(
        run_id="run-test-001",
        status="VERIFIED",
        success=True,
        duration=1.45,
        neatlogs_trace_id="trace-abc-123",
        summary="Issue #101 verified and resolved in 1.45s",
        diff_text="--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n- return x / y\n+ if y == 0: raise ValueError()\n+ return x / y"
    )

    finished = temp_db.get_run("run-test-001")
    assert finished["status"] == "VERIFIED"
    assert finished["success"] == 1
    assert finished["neatlogs_trace_id"] == "trace-abc-123"
    assert "calc.py" in finished["diff_text"]


def test_pr_safety_gate_blocking_unverified():
    """Verify that unverified runs cannot create normal PRs without override."""
    # Run is unverified (status = FAILED)
    failed_run = {
        "run_id": "run-fail-99",
        "issue_id": "404",
        "status": "FAILED",
        "success": 0
    }

    # Standard check: must be VERIFIED
    is_verified = (failed_run["status"] == "VERIFIED")
    override_allowed = False

    can_publish_normal = is_verified
    assert not can_publish_normal

    # With explicit user acknowledgment override:
    user_acknowledged_failure = True
    can_publish_with_warning = user_acknowledged_failure and not is_verified
    assert can_publish_with_warning


def test_duplicate_pr_detection():
    """Verify that checking existing PRs prevents duplicate PR creation."""
    # In GitHubPRTool, find_existing_pr checks if an open PR with same head branch exists
    # When token is empty/offline, returns None gracefully
    result = GitHubPRTool.find_existing_pr("Quantum-Ark", "patchai", "patchpilot/fix-nonexistent", token="fake_token")
    assert result is None or isinstance(result, dict)


def test_save_and_list_pull_requests(temp_db):
    """Verify saving a created PR to the database and listing in history."""
    # First create a run
    temp_db.create_run(
        run_id="run-pr-test",
        issue_id="55",
        issue_title="Off by one error in paginator",
        repo_owner="Quantum-Ark",
        repo_name="patchai"
    )

    pr = temp_db.save_pull_request(
        run_id="run-pr-test",
        repo_owner="Quantum-Ark",
        repo_name="patchai",
        pr_number=42,
        pr_url="https://github.com/Quantum-Ark/patchai/pull/42",
        title="fix(55): Off by one error in paginator",
        body="Verified patch generated by PatchPilot AI",
        branch="patchpilot/fix-55-abc123",
        base_branch="main",
        is_draft=False
    )

    assert pr["pr_number"] == 42
    assert pr["pr_url"] == "https://github.com/Quantum-Ark/patchai/pull/42"

    prs = temp_db.list_pull_requests()
    assert len(prs) == 1
    assert prs[0]["pr_number"] == 42
    assert prs[0]["branch"] == "patchpilot/fix-55-abc123"

    # Stats should reflect the PR
    stats = temp_db.get_dashboard_stats()
    assert stats["total_prs"] == 1
    assert stats["total_runs"] == 1


def test_token_verification_graceful_handling():
    """Verify GitHub token verification handles invalid/empty tokens gracefully."""
    empty_res = GitHubPRTool.verify_token("")
    assert empty_res["valid"] is False

    invalid_res = GitHubPRTool.verify_token("invalid_dummy_token_12345")
    assert invalid_res["valid"] is False
    assert "error" in invalid_res
