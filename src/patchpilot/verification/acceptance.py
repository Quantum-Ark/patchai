"""
Independent Acceptance Verification.
Executes the specific acceptance test associated with the reported issue.
"""

from pathlib import Path
from patchpilot.models import TestExecutionResult
from patchpilot.tools.test_runner import TestRunnerTool


class AcceptanceVerifier:
    def __init__(self, repo_dir: Path):
        self.runner = TestRunnerTool(working_dir=repo_dir)

    def verify(self, acceptance_command: str) -> TestExecutionResult:
        """Runs the specific test that was failing initially to verify it now passes."""
        return self.runner.run_command(acceptance_command)
