"""
PatchPilot AI Command Line Interface.
Built with Typer and Rich for neatHacks 2026.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from patchpilot import __version__
from patchpilot.config import config
from patchpilot.models import Issue
from patchpilot.tools.github import GitHubIssueTool
from patchpilot.recovery.checkpoint import CheckpointStore
from patchpilot.reporting.report import ReportGenerator
from patchpilot.orchestrator import PatchPilotOrchestrator
from patchpilot.llm.provider import get_llm_provider

app = typer.Typer(
    name="patchpilot",
    help="Autonomous GitHub Issue-to-Verified-Fix Agent with Verified Recovery."
)
console = Console()


@app.command()
def version():
    """Print PatchPilot AI version."""
    console.print(f"[bold cyan]PatchPilot AI[/bold cyan] version [green]{__version__}[/green]")


@app.command()
def status():
    """Display environment, Neatlogs observability, and checkpoint store status."""
    table = Table(title="PatchPilot AI - System Status")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Value / State", style="green")

    table.add_row("Version", __version__)
    table.add_row("Neatlogs Project ID", config.neatlogs_project_id)
    table.add_row("Neatlogs Ingest URL", config.neatlogs_ingest_url)
    table.add_row("Neatlogs Configured", "[OK] Ready" if config.neatlogs_api_key else "[WARN] Missing Key")
    table.add_row("LLM Model", config.model)
    table.add_row("Max Recovery Attempts", str(config.max_attempts))
    table.add_row("Execution Timeout", f"{config.execution_timeout_seconds}s")
    table.add_row("Checkpoint DB", str(config.checkpoint_db_path))

    console.print(table)


@app.command()
def run(
    issue_source: str = typer.Argument(
        ...,
        help="Path to issue JSON/Markdown file or issue description string."
    ),
    repo_dir: Path = typer.Option(
        Path("."),
        "--repo",
        "-r",
        help="Target repository directory to investigate and fix."
    ),
    provider: str = typer.Option(
        "openai",
        "--provider",
        "-p",
        help="LLM provider: 'openai' or 'mock' (for deterministic offline testing)."
    ),
    output_dir: Path = typer.Option(
        Path("artifacts"),
        "--output",
        "-o",
        help="Directory to export JSON and Markdown reports."
    )
):
    """
    Run autonomous issue investigation, reproduction, verified recovery, and verification.
    """
    console.print(Panel.fit(
        f"[bold cyan]PatchPilot AI[/bold cyan] - Autonomous Verified Recovery Agent\n"
        f"Target Repo: [yellow]{repo_dir.resolve()}[/yellow]\n"
        f"Provider: [magenta]{provider}[/magenta]",
        border_style="cyan"
    ))

    # Parse issue
    path_candidate = Path(issue_source)
    if path_candidate.is_file():
        console.print(f"Loading issue from file: [blue]{path_candidate}[/blue]")
        issue = GitHubIssueTool.load_from_file(path_candidate)
    else:
        console.print("Parsing inline issue description...")
        issue = GitHubIssueTool.load_from_dict({
            "id": "cli-issue",
            "title": issue_source[:60],
            "body": issue_source
        })

    console.print(f"Loaded Issue: [bold]#{issue.id}[/bold] - [italic]{issue.title}[/italic]\n")

    # Initialize orchestrator
    llm = get_llm_provider(provider)
    orchestrator = PatchPilotOrchestrator(
        repo_dir=repo_dir,
        llm_provider=llm
    )

    with console.status("[bold green]Investigating, reproducing, and verifying patch...[/bold green]"):
        report = orchestrator.run(issue)

    # Display results
    if report.success:
        console.print(Panel(
            f"[bold green][OK] FIX VERIFIED AND RECOVERED SUCCESSFULLY![/bold green]\n"
            f"Run ID: [cyan]{report.run_id}[/cyan]\n"
            f"Duration: {report.total_duration_seconds:.2f}s | Attempts: {len(report.attempts)}\n"
            f"Neatlogs Trace ID: [magenta]{report.neatlogs_trace_id or 'Local'}[/magenta]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red][FAIL] FIX ATTEMPT FAILED[/bold red]\n"
            f"Final State: {report.final_state.value}\n"
            f"Attempts: {len(report.attempts)}",
            border_style="red"
        ))

    # Save reports
    json_path, md_path = ReportGenerator.save_reports(report, output_dir)
    console.print(f"\n[green]* Reports exported:[/green]")
    console.print(f"  - Markdown Report: [blue]{md_path}[/blue]")
    console.print(f"  - Machine JSON:    [blue]{json_path}[/blue]")


@app.command()
def history():
    """List historical run checkpoints stored in SQLite."""
    store = CheckpointStore(config.checkpoint_db_path)
    runs = store.list_runs()

    if not runs:
        console.print("[yellow]No historical checkpoints found in local store.[/yellow]")
        return

    table = Table(title="PatchPilot AI - Checkpoint History")
    table.add_column("Run ID", style="cyan")
    table.add_column("Issue ID", style="white")
    table.add_column("Title", style="white")
    table.add_column("State", style="magenta")
    table.add_column("Success", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Created", style="dim")

    for r in runs:
        success_badge = "[green][OK] Passed[/green]" if r["success"] else "[red][FAIL] Failed[/red]"
        table.add_row(
            r["run_id"],
            str(r["issue_id"]),
            r["issue_title"][:40],
            r["final_state"],
            success_badge,
            f"{r['total_duration']:.2f}s",
            str(r["created_at"])
        )

    console.print(table)


@app.command()
def entire_sync():
    """Display Entire CLI checkpoint commands for neatHacks submission evidence."""
    console.print(Panel(
        "[bold cyan]Entire Integration Guidelines - neatHacks 2026[/bold cyan]\n\n"
        "To link your Git commit to the agent sessions and decisions:\n"
        "1. [yellow]entire enable --agent codex[/yellow]\n"
        "2. [yellow]git add .[/yellow]\n"
        "3. [yellow]git commit -m \"feat: Verified recovery agent implementation\"[/yellow]\n"
        "4. [yellow]entire checkpoint list[/yellow]\n"
        "5. [yellow]entire checkpoint explain HEAD[/yellow]\n\n"
        "Submission URL format:\n"
        "https://entire.io/gh/OWNER/REPO/commit/FULL_COMMIT_SHA",
        border_style="cyan"
    ))


if __name__ == "__main__":
    app()
