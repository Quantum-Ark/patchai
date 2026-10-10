"""
Bug Reproduction Tool.
Executes baseline tests or repro scripts to verify failure prior to patching.
"""

from pathlib import Path
from patchpilot.models import Issue, ReproductionResult
from patchpilot.tools.test_runner import TestRunnerTool


class ReproductionTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.runner = TestRunnerTool(working_dir=repo_dir)

    def reproduce(self, issue: Issue) -> ReproductionResult:
        """
        Runs baseline reproduction command.
        In bug fixing, a failure at baseline confirms that the bug is actively reproduced.
        """
        command = issue.reproduction_command or "pytest tests/ -v"
        result = self.runner.run_command(command)

        # The bug is reproduced if the command fails (exit_code != 0)
        reproduced = not result.passed
        details = (
            f"Bug successfully reproduced via '{command}' (exit code {result.exit_code})."
            if reproduced
            else f"Warning: Command '{command}' passed unexpectedly on unmodified code."
        )

        return ReproductionResult(
            reproduced=reproduced,
            command_executed=command,
            baseline_result=result,
            failure_details=details
        )
