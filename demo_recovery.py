"""
PatchPilot AI — Autonomous Verified Recovery Showcase Demo.
Runs an end-to-end bug reproduction, failed attempt rollback, strategy pivot,
successful fix, and independent dual-suite verification.

NeatHacks 2026 Submission Demonstration.
"""

import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from patchpilot.models import Issue, FailureCategory, RecoveryAction, AgentState
from patchpilot.orchestrator import PatchPilotOrchestrator
from patchpilot.llm.provider import MockLLMProvider
from patchpilot.recovery.checkpoint import CheckpointStore
from patchpilot.reporting.report import ReportGenerator

console = Console()


def run_showcase():
    console.print(Panel.fit(
        "[bold cyan]PatchPilot AI[/bold cyan] - Autonomous Verified Recovery Showcase\n"
        "[italic]neatHacks 2026 Demonstration[/italic]\n\n"
        "Core Differentiator: [bold green]Verified Recovery[/bold green]\n"
        "Observe how Attempt 1 introduces a regression, gets caught & rolled back,\n"
        "and how Attempt 2 pivots strategy to pass both reproduction & regression suites.",
        border_style="cyan"
    ))

    benchmark_dir = Path("benchmarks/case_3_regression_recovery").resolve()
    issue_file = benchmark_dir / "issue.json"

    with open(issue_file, "r", encoding="utf-8") as f:
        issue_data = json.load(f)

    issue = Issue(
        id=issue_data["id"],
        title=issue_data["title"],
        body=issue_data["body"],
        file_hints=issue_data.get("file_hints", ["pricing.py"]),
        reproduction_command=issue_data.get("reproduction_command", "pytest test_reproduction_quantity.py -v"),
    )

    # Attempt 1: Naive fix that breaks existing tiers
    bad_attempt_patch = (
        "TARGET_FILE: pricing.py\n"
        "ORIGINAL_CODE: multiplier = 1.0\n"
        "PATCHED_CODE: if quantity <= 0: raise ValueError('Quantity must be greater than 0')\n"
        "    return round(base_price * quantity, 2)  # Bug: stripped tier discounts!"
    )

    # Attempt 2: Precision fix that adds validation while preserving all existing tier discounts
    good_attempt_patch = (
        "TARGET_FILE: pricing.py\n"
        "ORIGINAL_CODE: multiplier = 1.0\n"
        "PATCHED_CODE: if quantity <= 0:\n"
        "        raise ValueError('Quantity must be greater than 0')\n"
        "    multiplier = 1.0"
    )

    mock_llm = MockLLMProvider(
        sequential_patches=[bad_attempt_patch, good_attempt_patch]
    )

    checkpoint_store = CheckpointStore(Path(".patchpilot_state.db"))

    orchestrator = PatchPilotOrchestrator(
        repo_dir=benchmark_dir,
        llm_provider=mock_llm,
        checkpoint_store=checkpoint_store,
        max_attempts=3
    )

    console.print(f"[bold]Target Issue:[/bold] #{issue.id}: {issue.title}")
    console.print(f"[dim]Running reproduction baseline...[/dim]\n")

    report = orchestrator.run(
        issue=issue,
        regression_command="pytest test_regression_suite.py -v"
    )

    # Display attempts table
    table = Table(title="PatchPilot AI - Attempt Progression & Recovery Evidence")
    table.add_column("Attempt", style="cyan", no_wrap=True)
    table.add_column("Strategy & Action", style="white")
    table.add_column("Test Result", style="bold")
    table.add_column("Failure Classification", style="magenta")
    table.add_column("Recovery Decision", style="yellow")

    for att in report.attempts:
        passed = att.test_result.passed if att.test_result else False
        status_badge = "[green][OK] Passed[/green]" if passed else "[red][FAIL] Failed[/red]"
        table.add_row(
            f"#{att.attempt_number}",
            att.strategy_description[:45] + "...",
            status_badge,
            att.failure_category.value,
            att.recovery_decision.value if att.recovery_decision else "None (Fix Verified)"
        )

    console.print(table)

    # Display final verdict
    if report.success:
        console.print(Panel(
            f"[bold green][OK] VERIFIED RECOVERY SUCCESSFUL[/bold green]\n\n"
            f"Run ID: [cyan]{report.run_id}[/cyan]\n"
            f"Final State: [bold green]{report.final_state.value}[/bold green]\n"
            f"Total Duration: {report.total_duration_seconds:.2f}s\n"
            f"Neatlogs Trace ID: [magenta]{report.neatlogs_trace_id}[/magenta]\n\n"
            f"[italic]Evidence Summary:[/italic]\n"
            f"- Attempt 1: Failed verification -> Classified -> Instant Rollback\n"
            f"- Attempt 2: Strategy Pivot -> Acceptance Passed -> Regression Passed -> Fixed",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red][FAIL] VERIFICATION FAILED[/bold red]",
            border_style="red"
        ))

    # Export reports
    out_dir = Path("artifacts/demo_recovery")
    json_path, md_path = ReportGenerator.save_reports(report, out_dir)
    console.print(f"\n[green]* Reports generated:[/green]")
    console.print(f"  - Markdown: [blue]{md_path}[/blue]")
    console.print(f"  - JSON:     [blue]{json_path}[/blue]\n")

    return report


if __name__ == "__main__":
    run_showcase()
