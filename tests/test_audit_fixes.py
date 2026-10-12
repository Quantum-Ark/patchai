"""Regression tests for audit fixes: injection blocking, traversal guards, config wiring."""

import pytest
from pathlib import Path
from patchpilot.tools.test_runner import TestRunnerTool as _TestRunnerTool
from patchpilot.tools.patch import PatchTool
from patchpilot.tools.github import GitHubIssueTool
from patchpilot.config import PatchPilotConfig, verify_api_token, ensure_api_token


def test_runner_blocks_shell_injection(tmp_path: Path):
    runner = _TestRunnerTool(tmp_path)
    for evil in ("rm -rf /", "pytest tests/ && rm -rf /", "python -c \"import os; os.system('x')\""):
        result = runner.run_command(evil)
        assert result.passed is False
        assert result.exit_code == -2 or "not allowed" in result.summary + result.stderr


def test_runner_blocks_python_code_execution(tmp_path: Path):
    """API8 fix: python -c / python -m / python <script> must never execute."""
    (tmp_path / "test_ok.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    runner = _TestRunnerTool(tmp_path)
    for evil in (
        "python -c printPWNED",
        "python -m pip --version",
        "python -m http.server --help",
        "python evil.py",
        "python3 -c printPWNED",
        "pytest --co -q",
        "pytest -p no:cacheprovider tests/",
        "pytest -s tests/",
        "pytest --pdb tests/",
        "pytest tests/ --junitxml /tmp/out.xml",
        "pytest ../evil.py",
        "pytest /etc/passwd",
        "pytest tests/; rm -rf /",
        "pytest tests/ --capture=no",
        "pytest --import-mode importlib tests/",
    ):
        result = runner.run_command(evil)
        assert result.passed is False, evil
        assert result.exit_code == -2, evil


def test_runner_allows_safe_pytest(tmp_path: Path):
    (tmp_path / "test_ok.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    runner = _TestRunnerTool(tmp_path)
    result = runner.run_command("pytest test_ok.py -v")
    assert result.passed is True


def test_runner_allows_marker_selection(tmp_path: Path):
    (tmp_path / "test_ok.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    runner = _TestRunnerTool(tmp_path)
    result = runner.run_command("pytest test_ok.py -m slow -v")
    # -m slow deselects everything -> exit code 5, but must NOT be blocked (-2)
    assert result.exit_code != -2


def test_github_validators_reject_option_injection():
    from patchpilot.tools.github import _validate_branch_name, _validate_owner_repo
    for evil in ("--upload-pack=touch pwned", "-evil", "../x", "a" * 200):
        with pytest.raises(ValueError):
            _validate_branch_name(evil)
    for evil in ("../x", "a/b", "", "a" * 200):
        with pytest.raises(ValueError):
            _validate_owner_repo(evil, "repo owner")
    # anchored URL parsing rejects non-github hosts
    with pytest.raises(ValueError):
        GitHubIssueTool.parse_issue_url("https://evil.com/github.com/o/r/issues/1")


def test_api_token_helpers():
    assert verify_api_token("abc", "abc") is True
    assert verify_api_token("abc", "abd") is False
    assert verify_api_token("", "abc") is False
    cfg = PatchPilotConfig(api_token="secret-123")
    assert ensure_api_token(cfg) == "secret-123"
    cfg2 = PatchPilotConfig(api_token="")
    gen = ensure_api_token(cfg2)
    assert len(gen) >= 32 and verify_api_token(gen, cfg2.api_token)


def test_db_encrypts_token_when_key_set(tmp_path, monkeypatch):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("PATCHPILOT_TOKEN_KEY", key)
    from patchpilot.db import PatchPilotDB
    db = PatchPilotDB(db_path=tmp_path / "enc.db")
    db.save_github_auth("u", "n", "", "ghp_SUPERSECRET123456", "repo")
    with db._connect() as conn:
        row = conn.execute("SELECT token FROM github_auth WHERE id=1").fetchone()
        assert "SUPERSECRET" not in row["token"]
    auth = db.get_github_auth()
    assert auth["token"] == "ghp_SUPERSECRET123456"
    assert auth["masked_token"] == "****3456"


def test_repair_runner_bounds_concurrency(tmp_path):
    import threading, time
    from patchpilot.runner import RepairRunner
    from patchpilot.models import Issue
    from patchpilot.db import PatchPilotDB
    import patchpilot.runner as runner_mod
    mem = PatchPilotDB(db_path=tmp_path / "q.db")
    runner_mod.db = mem
    rr = RepairRunner(max_concurrent=1)
    blocker = threading.Event()
    orig_worker = rr._run_worker
    def slow_worker(*a, **k):
        blocker.wait(timeout=10)
        return orig_worker(*a, **k)
    rr._run_worker = slow_worker
    issue = Issue(id="i1", title="t", body="b", reproduction_command="pytest tests/ -q")
    rr.start_repair(issue=issue, repo_owner="o", repo_name="r")
    with pytest.raises(RuntimeError, match="queue full"):
        rr.start_repair(issue=issue, repo_owner="o", repo_name="r")
    blocker.set()


def test_runner_blocks_shell_injection(tmp_path: Path):
    runner = _TestRunnerTool(tmp_path)
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
