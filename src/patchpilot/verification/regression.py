"""
Independent Regression Verification.
Executes the broader test suite to guarantee that the applied patch did not introduce regressions elsewhere.
"""

from pathlib import Path
from patchpilot.models import TestExecutionResult
from patchpilot.tools.test_runner import TestRunnerTool


class RegressionVerifier:
    def __init__(self, repo_dir: Path):
        self.runner = TestRunnerTool(working_dir=repo_dir)

    def verify(self, regression_command: str = "pytest tests/ -v") -> TestExecutionResult:
        """Runs the regression suite to ensure no side effects were introduced."""
        return self.runner.run_command(regression_command)
