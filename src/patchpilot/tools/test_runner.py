"""
Isolated Test Runner Tool.
Executes test commands with timeouts, output capture, and failure parsing.
"""

import sys
import time
import subprocess
from pathlib import Path
from patchpilot.models import TestExecutionResult
from patchpilot.config import config


class TestRunnerTool:
    def __init__(self, working_dir: Path, timeout_seconds: int = config.execution_timeout_seconds):
        self.working_dir = working_dir.resolve()
        self.timeout_seconds = timeout_seconds

    def run_command(self, command: str) -> TestExecutionResult:
        """Execute a test command and return structured result."""
        start_time = time.time()
        try:
            # Use Python executable from current venv if running python or pytest
            cmd = command
            if command.startswith("pytest"):
                cmd = f'"{sys.executable}" -m {command}'
            elif command.startswith("python "):
                cmd = f'"{sys.executable}" ' + command[7:]

            import os
            run_env = os.environ.copy()
            run_env["PYTHONPATH"] = f"{self.working_dir}{os.pathsep}{run_env.get('PYTHONPATH', '')}"

            process = subprocess.run(
                cmd,
                cwd=self.working_dir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=run_env,
            )
            duration = time.time() - start_time
            passed = (process.exit_code == 0) if hasattr(process, "exit_code") else (process.returncode == 0)
            exit_code = process.returncode

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
