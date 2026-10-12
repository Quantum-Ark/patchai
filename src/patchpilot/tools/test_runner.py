"""
Isolated Test Runner Tool.
Executes test commands with timeouts, output capture, and failure parsing.
Allow-listed commands only (bare `pytest` with safe flags), no shell,
secrets scrubbed from child env.
"""

import os
import re
import shlex
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Optional
from patchpilot.models import TestExecutionResult
from patchpilot.config import config

_SECRET_ENV_KEYS = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GITHUB_TOKEN",
    "NEATLOGS_API_KEY",
    "CRUSTDATA_API_KEY",
}

# Pytest flags that allow code execution, plugin loading, shell-outs, or
# network/file exfiltration. Rejected outright.
_BLOCKED_PYTEST_FLAGS = {
    "-p", "--plugins", "--override-ini", "-o", "--rootdir",
    "--basetemp", "--cache-clear", "--import-mode",
    "-s", "--capture", "--pdb", "--pdbcls", "--trace",
    "--lf", "--ff", "--stepwise", "--sw",
    "--junitxml", "--resultlog", "--co",
    "--doctest-modules", "--doctest-glob",
    "--cov", "--cov-append", "--cov-config", "--cov-report",
    "-n", "--numprocesses", "--dist", "--tx", "-d",
    "--boxed",
    "--deselect",
}

# Any flag value containing these substrings is rejected (shell/code/URL).
_BLOCKED_VALUE_SUBSTRINGS = (
    ":", ";", "|", "&", "$", "`", "(", ")", "<", ">", "\\", "\n", "\r",
    "http://", "https://", "ftp://", "\\\\",
)


def _scrub_env(base: Optional[dict] = None) -> dict:
    env = dict(base) if base is not None else os.environ.copy()
    for key in _SECRET_ENV_KEYS:
        env.pop(key, None)
    return env


def _looks_like_path(arg: str) -> bool:
    return (
        arg.endswith(".py")
        or "/" in arg
        or "\\" in arg
        or arg in (".", "tests")
        or arg.startswith("tests/")
        or arg.startswith("tests\\")
        or "::" in arg
    )


def _validate_test_path(arg: str, working_dir: Path) -> None:
    """Ensure a path/selector arg stays inside working_dir and names a test."""
    selector, _, _ = arg.partition("::")
    if os.path.isabs(selector):
        raise ValueError(f"Absolute paths are not allowed: {arg!r}.")
    if ".." in selector.replace("\\", "/").split("/"):
        raise ValueError(f"Path traversal is not allowed: {arg!r}.")
    base = working_dir.resolve()
    candidate = (working_dir / selector).resolve() if selector not in (".", "") else base
    try:
        inside = candidate.is_relative_to(base)
    except (OSError, ValueError):
        raise ValueError(f"Invalid test path: {arg!r}.")
    if not inside:
        raise ValueError(f"Test path escapes working directory: {arg!r}.")
    if selector not in (".", "") and not candidate.exists():
        raise ValueError(f"Test path does not exist: {arg!r}.")
    if selector not in (".", "") and candidate.is_file() and not selector.endswith(".py"):
        raise ValueError(f"Only .py test files may be named: {arg!r}.")
    if selector not in (".", "") and candidate.is_file():
        name = candidate.name
        if not (name.startswith("test_") or name.endswith("_test.py")):
            raise ValueError(f"Only test files may be named: {arg!r}.")


def _build_argv(command: str, working_dir: Path) -> List[str]:
    parts = shlex.split(command, posix=False)
    if not parts:
        raise ValueError("Empty test command.")
    # Normalize Windows-quoted python path etc.
    head = parts[0].strip('"').strip("'").lower()
    base = os.path.basename(head)
    stem = base[:-4] if base.endswith(".exe") else base
    # SECURITY: only the bare `pytest` binary is accepted. `python`,
    # `python -m ...`, and `python <script>` allow arbitrary code execution.
    if stem != "pytest":
        raise ValueError(
            f"Command not allowed: {parts[0]!r}. "
            "Allowed: pytest <test-path> [safe flags]."
        )
    rest = parts[1:]
    skip_next = False
    for i, tok in enumerate(rest):
        if skip_next:
            skip_next = False
            continue
        if tok.startswith("-"):
            flag = tok.split("=")[0]
            if flag.lower() in _BLOCKED_PYTEST_FLAGS:
                raise ValueError(f"Pytest flag not allowed: {tok!r}.")
            if "=" not in tok and i + 1 < len(rest) and not rest[i + 1].startswith("-"):
                val = rest[i + 1]
                if any(s in val for s in _BLOCKED_VALUE_SUBSTRINGS):
                    raise ValueError(f"Unsafe flag value: {val!r}.")
                skip_next = True
                continue
            if any(s in tok for s in _BLOCKED_VALUE_SUBSTRINGS):
                raise ValueError(f"Unsafe pytest argument: {tok!r}.")
        else:
            if _looks_like_path(tok):
                _validate_test_path(tok, working_dir)
            elif re.fullmatch(r"[A-Za-z0-9_]+", tok):
                continue  # bare marker word after -m/-k: safe
            else:
                raise ValueError(f"Unexpected pytest argument: {tok!r}.")
    argv: List[str] = [sys.executable, "-m", "pytest"] + rest
    # Block shell metacharacters smuggled as args
    dangerous = {"&&", "||", ";", "|", "`", "$(", ">", "<", ">>"}
    joined = " ".join(argv)
    if any(tok in joined for tok in dangerous):
        raise ValueError("Shell metacharacters are not allowed in test commands.")
    return argv


class TestRunnerTool:
    def __init__(self, working_dir: Path, timeout_seconds: int = config.execution_timeout_seconds):
        self.working_dir = working_dir.resolve()
        self.timeout_seconds = timeout_seconds

    def run_command(self, command: str) -> TestExecutionResult:
        """Execute a test command and return structured result."""
        start_time = time.time()
        try:
            argv = _build_argv(command, self.working_dir)

            run_env = _scrub_env()
            run_env["PYTHONPATH"] = f"{self.working_dir}{os.pathsep}{run_env.get('PYTHONPATH', '')}"

            process = subprocess.run(
                argv,
                cwd=self.working_dir,
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=run_env,
            )
            duration = time.time() - start_time
            exit_code = process.returncode
            passed = exit_code == 0

            summary = f"Command exited with code {exit_code} in {duration:.2f}s."
            if passed:
                summary += " All tests passed."
            else:
                summary += " Test failures or errors detected."

            return TestExecutionResult(
                command=command,
                exit_code=exit_code,
                stdout=process.stdout,
                stderr=process.stderr,
                duration_seconds=round(duration, 3),
                passed=passed,
                summary=summary,
            )

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            return TestExecutionResult(
                command=command,
                exit_code=-1,
                stdout=e.stdout or "" if isinstance(e.stdout, str) else "",
                stderr=f"Command timed out after {self.timeout_seconds} seconds.",
                duration_seconds=round(duration, 3),
                passed=False,
                summary=f"TIMEOUT: Exceeded {self.timeout_seconds}s limit.",
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestExecutionResult(
                command=command,
                exit_code=-2,
                stdout="",
                stderr=str(e),
                duration_seconds=round(duration, 3),
                passed=False,
                summary=f"Execution error: {str(e)}",
            )
