"""Regression tests for audit fixes: injection blocking, traversal guards, config wiring."""

import pytest
from pathlib import Path
from patchpilot.tools.test_runner import TestRunnerTool
from patchpilot.tools.patch import PatchTool
from patchpilot.tools.github import GitHubIssueTool
from patchpilot.config import PatchPilotConfig


def test_runner_blocks_shell_injection(tmp_path: Path):
    runner = TestRunnerTool(tmp_path)
    for evil in ("rm -rf /", "pytest tests/ && rm -rf /", "python -c \"import os; os.system('x')\""):
        result = runner.run_command(evil)
        assert result.passed is False
        assert result.exit_code == -2 or "not allowed" in result.summary + result.stderr


def test_runner_blocks_env_secret_leak(tmp_path: Path):
    import patchpilot.tools.test_runner as tr
    env = {"OPENAI_API_KEY": "sk-secret", "PATH": "x", "OTHER": "keep"}
    scrubbed = tr._scrub_env(env)
    assert "OPENAI_API_KEY" not in scrubbed
    assert scrubbed["OTHER"] == "keep"


def test_patch_rejects_traversal_and_noop(tmp_path: Path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    tool = PatchTool(tmp_path)
    ok, _, err = tool.apply_replacement("../evil.py", "x", "y")
    assert ok is False and "traversal" in err.lower()
    ok, _, err = tool.apply_replacement("a.py", "x = 1", "x = 1")
    assert ok is False and "no-op" in err.lower()
    ok, _, err = tool.apply_replacement("a.py", "   ", "y")
    assert ok is False


def test_github_url_parsing_and_validation():
    owner, repo, num = GitHubIssueTool.parse_issue_url(
        "https://github.com/octocat/hello-world/issues/42"
    )
    assert (owner, repo, num) == ("octocat", "hello-world", 42)
    with pytest.raises(ValueError):
        GitHubIssueTool.parse_issue_url("https://example.com/not-an-issue")
    with pytest.raises((OSError, ValueError)):
        GitHubIssueTool.load_from_file(Path("nonexistent-xyz.json"))


def test_config_env_wiring(monkeypatch):
    monkeypatch.setenv("PATCHPILOT_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("PATCHPILOT_TIMEOUT_SECONDS", "120")
    cfg = PatchPilotConfig()
    assert cfg.max_attempts == 5
    assert cfg.execution_timeout_seconds == 120
    with pytest.raises(Exception):
        PatchPilotConfig(max_attempts=0)
