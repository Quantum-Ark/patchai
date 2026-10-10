"""
Isolated Test Runner Tool.
Executes test commands with timeouts, output capture, and failure parsing.
Allow-listed commands only, no shell, secrets scrubbed from child env.
"""

import os
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

_ALLOWED_BINARIES = {"pytest", "python", "python3"}


def _scrub_env(base: Optional[dict] = None) -> dict:
    env = dict(base) if base is not None else os.environ.copy()
    for key in _SECRET_ENV_KEYS:
        env.pop(key, None)
    return env


def _build_argv(command: str, working_dir: Path) -> List[str]:
    parts = shlex.split(command, posix=False)
    if not parts:
        raise ValueError("Empty test command.")
    # Normalize Windows-quoted python path etc.
    head = parts[0].strip('"').strip("'").lower()
    base = os.path.basename(head)
    stem = base[:-4] if base.endswith(".exe") else base
    if stem not in _ALLOWED_BINARIES and stem != "pytest":
        raise ValueError(
            f"Command not allowed: {parts[0]!r}. "
            "Allowed: pytest, python -m pytest, python <script>."
        )
    argv: List[str] = []
    if stem in {"python", "python3"}:
        argv = [sys.executable] + parts[1:]
    elif stem == "pytest" or (stem.endswith("pytest")):
        argv = [sys.executable, "-m", "pytest"] + parts[1:]
    else:
        raise ValueError(f"Command not allowed: {parts[0]!r}.")
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
