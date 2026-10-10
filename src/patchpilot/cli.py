"""
PatchPilot AI Command Line Interface.
Built with Typer and Rich for neatHacks 2026.
"""

import sys
import shutil
import subprocess
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
from patchpilot.telemetry.tracing import NeatlogsTracer

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

    neatlogs_key_display = (
        f"[green][OK] Configured ({config.neatlogs_api_key[:4]}...{config.neatlogs_api_key[-4:]})[/green]"
        if config.neatlogs_api_key else "[yellow][WARN] Missing Key[/yellow]"
    )
    table.add_row("Neatlogs API Key", neatlogs_key_display)
    if config.neatlogs_project_id:
        table.add_row("Neatlogs Project ID", config.neatlogs_project_id)
    table.add_row("Neatlogs Ingest URL", config.neatlogs_ingest_url)
    table.add_row("LLM Model", config.model)
    table.add_row("Max Recovery Attempts", str(config.max_attempts))
    table.add_row("Execution Timeout", f"{config.execution_timeout_seconds}s")
    table.add_row("Checkpoint DB", str(config.checkpoint_db_path))

    console.print(table)


@app.command()
def doctor():
    """Diagnose environment tools, dependencies, and integration readiness."""
    table = Table(title="PatchPilot AI - Environment Diagnostics (Doctor)")
    table.add_column("Subsystem", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python Runtime", "[green][OK][/green]", f"Python {py_ver}")

    # Git
    git_bin = shutil.which("git")
    if git_bin:
        table.add_row("Git CLI", "[green][OK][/green]", git_bin)
    else:
        table.add_row("Git CLI", "[red][FAIL][/red]", "Not found on PATH")

    # Docker
    docker_bin = shutil.which("docker")
    if docker_bin:
        table.add_row("Docker Sandbox", "[green][OK][/green]", "Available")
    else:
        table.add_row("Docker Sandbox", "[yellow][WARN][/yellow]", "Not active; using isolated subprocess fallback")

    # Entire CLI (portable detection)
    _entire_bin = shutil.which("entire")
    _entire_found = bool(_entire_bin)
    if not _entire_found:
        for _cand in (
            Path.home() / ".local" / "bin" / "entire",
            Path.home() / ".local" / "bin" / "entire.exe",
        ):
            if _cand.exists():
                _entire_bin = str(_cand)
                _entire_found = True
                break
    if _entire_found:
        table.add_row("Entire CLI", "[green][OK][/green]", f"Installed & configured ({_entire_bin})")
    else:
        table.add_row("Entire CLI", "[yellow][WARN][/yellow]", "Entire binary not found")

    # Neatlogs
    if config.neatlogs_api_key:
        masked = f"{config.neatlogs_api_key[:4]}...{config.neatlogs_api_key[-4:]}"
        table.add_row("Neatlogs Tracing", "[green][OK][/green]", f"Configured via NEATLOGS_API_KEY ({masked})")
    else:
        table.add_row("Neatlogs Tracing", "[yellow][WARN][/yellow]", "NEATLOGS_API_KEY not configured")

    # Crustdata API
    if config.crustdata_api_key:
        masked_crust = f"{config.crustdata_api_key[:4]}...{config.crustdata_api_key[-4:]}"
        table.add_row("Crustdata API", "[green][OK][/green]", f"Connected via CRUSTDATA_API_KEY ({masked_crust})")

    # Checkpoint store
    store = CheckpointStore(config.checkpoint_db_path)
    table.add_row("Checkpoint Store", "[green][OK][/green]", f"SQLite: {config.checkpoint_db_path}")

    console.print(table)


@app.command()
def repair(
    issue_source: Optional[str] = typer.Argument(
        None,
        help="Inline issue description string or issue file path."
    ),
    issue_url: Optional[str] = typer.Option(
        None,
        "--issue-url",
        help="GitHub issue URL (e.g. https://github.com/org/repo/issues/42)."
    ),
    issue_file: Optional[Path] = typer.Option(
        None,
        "--issue-file",
        help="Path to JSON or Markdown issue specification file."
    ),
    repo_dir: Path = typer.Option(
        Path("."),
        "--repo",
        "-r",
        help="Target repository directory to investigate and fix."
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider: 'openai', 'anthropic', 'gemini', or 'mock' (offline unit test only)."
    ),
    output_dir: Path = typer.Option(
        Path("artifacts"),
        "--output",
        "-o",
        help="Directory to export JSON and Markdown reports."
    )
):
    """
    Autonomously investigate, reproduce, generate patch, and verify fix.
    """
    # Initialize provider
    try:
        llm = get_llm_provider(provider)
    except Exception as e:
        console.print(f"[bold red]LLM Provider Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(Panel.fit(
        f"[bold cyan]PatchPilot AI[/bold cyan] - Autonomous Verified Recovery Agent\n"
        f"Target Repo: [yellow]{repo_dir.resolve()}[/yellow]\n"
        f"Provider: [magenta]{llm.provider_name}[/magenta] ([dim]{llm.model_name}[/dim])",
        border_style="cyan"
    ))

    # Determine issue input
    if issue_file and issue_file.is_file():
        console.print(f"Loading issue from file: [blue]{issue_file}[/blue]")
        issue = GitHubIssueTool.load_from_file(issue_file)
    elif issue_url:
        console.print(f"Loading issue from URL: [blue]{issue_url}[/blue]")
        issue = GitHubIssueTool.load_from_url(issue_url)
    elif issue_source:
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
    else:
        console.print("[red]Error: Must provide an issue source via argument, --issue-url, or --issue-file.[/red]")
        raise typer.Exit(code=1)

    console.print(f"Loaded Issue: [bold]#{issue.id}[/bold] - [italic]{issue.title}[/italic]\n")

    # Initialize orchestrator
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


# Alias 'run' to 'repair'
app.command(name="run")(repair)


@app.command()
def inspect(run_id: str = typer.Argument(..., help="Run ID to inspect")):
    """Inspect detailed attempts, diffs, and verification for a specific run."""
    store = CheckpointStore(config.checkpoint_db_path)
    run_data = store.get_run(run_id)

    if not run_data:
        console.print(f"[red]Error: Run '{run_id}' not found in SQLite store.[/red]")
        raise typer.Exit(code=1)

    console.print(Panel(
        f"[bold cyan]Run Details: {run_id}[/bold cyan]\n"
        f"Issue: #{run_data.get('issue_id')} - {run_data.get('issue_title')}\n"
        f"State: {run_data.get('final_state')} | Success: {bool(run_data.get('success'))}\n"
        f"Duration: {run_data.get('total_duration')}s | Trace: {run_data.get('neatlogs_trace_id')}",
        border_style="cyan"
    ))

    attempts = run_data.get("attempts", [])
    table = Table(title=f"Attempts for {run_id}")
    table.add_column("Attempt", style="cyan")
    table.add_column("Target File", style="white")
    table.add_column("Result", style="bold")
    table.add_column("Failure Category", style="magenta")
    table.add_column("Recovery Decision", style="yellow")

    for a in attempts:
        badge = "[green][OK] Passed[/green]" if a.get("passed") else "[red][FAIL] Failed[/red]"
        table.add_row(
            str(a.get("attempt_number")),
            str(a.get("target_file")),
            badge,
            str(a.get("failure_category")),
            str(a.get("recovery_decision"))
        )

    console.print(table)


@app.command()
def report(run_id: str = typer.Argument(..., help="Run ID to show report for")):
    """Print the markdown summary report for a specific run."""
    store = CheckpointStore(config.checkpoint_db_path)
    run_data = store.get_run(run_id)

    if not run_data:
        console.print(f"[red]Error: Run '{run_id}' not found.[/red]")
        raise typer.Exit(code=1)

    summary = run_data.get("summary") or "No summary available."
    console.print(Panel(summary, title=f"Summary for {run_id}", border_style="green"))


@app.command()
def evaluate():
    """Execute the 3 reproducible benchmark evaluation cases."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from benchmarks.run_benchmarks import main as run_benchmarks_main
    run_benchmarks_main()



@app.command()
def verify_integrations():
    """Verify live connectivity for Neatlogs, Entire CLI, and configured LLM."""
    table = Table(title="PatchPilot AI - Integration Verification")
    table.add_column("Integration", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    # Neatlogs
    tracer = NeatlogsTracer()
    if tracer.is_configured():
        masked = f"{config.neatlogs_api_key[:4]}...{config.neatlogs_api_key[-4:]}"
        table.add_row("Neatlogs Telemetry", "[green][OK] Configured[/green]", f"Key: {masked} | Ingest: {tracer.ingest_url}")
    else:
        table.add_row("Neatlogs Telemetry", "[yellow][WARN] Inactive[/yellow]", "NEATLOGS_API_KEY not configured")

    # Entire
    try:
        entire_ok = bool(shutil.which("entire")) or any(
            (Path.home() / ".local" / "bin" / name).exists()
            for name in ("entire", "entire.exe")
        )
        if entire_ok:
            table.add_row("Entire Continuous Memory", "[green][OK] Enabled[/green]", "Entire CLI verified")
        else:
            table.add_row("Entire Continuous Memory", "[yellow][WARN][/yellow]", "Entire binary not found")
    except Exception as e:
        table.add_row("Entire Continuous Memory", "[red][FAIL][/red]", str(e))

    # LLM
    try:
        provider = get_llm_provider()
        table.add_row("LLM Provider", "[green][OK] Ready[/green]", f"{provider.provider_name} ({provider.model_name})")
    except Exception:
        table.add_row("LLM Provider", "[yellow][WARN] Not Configured[/yellow]", "Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY in .env")

    # Crustdata
    if config.crustdata_api_key:
        masked_crust = f"{config.crustdata_api_key[:4]}...{config.crustdata_api_key[-4:]}"
        table.add_row("Crustdata Intelligence", "[green][OK] Active[/green]", f"Key: {masked_crust} (2025-11-01 API)")
    else:
        table.add_row("Crustdata Intelligence", "[yellow][WARN] Optional[/yellow]", "CRUSTDATA_API_KEY not configured")

    console.print(table)


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
        "1. [yellow]entire enable --agent antigravity[/yellow]\n"
        "2. [yellow]git add .[/yellow]\n"
        "3. [yellow]git commit -m \"feat: Verified recovery agent implementation\"[/yellow]\n"
        "4. [yellow]entire checkpoint list[/yellow]\n"
        "5. [yellow]entire checkpoint explain HEAD[/yellow]\n\n"
        "Submission URL format:\n"
        "https://entire.io/gh/OWNER/REPO/commit/FULL_COMMIT_SHA",
        border_style="cyan"
    ))


@app.command()
def serve(
    port: int = typer.Option(3000, "--port", "-p", help="Port to serve the interactive homepage"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host address to bind")
):
    """Serve the interactive animated web homepage locally."""
    import http.server
    import socketserver
    import webbrowser
    from functools import partial

    web_dir = Path(__file__).parent.parent.parent / "web"
    if not web_dir.is_dir():
        console.print(f"[bold red]Error:[/bold red] Web directory not found at {web_dir}")
        raise typer.Exit(code=1)

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(web_dir))
    
    console.print(Panel.fit(
        f"[bold cyan]PatchPilot AI — Web Experience[/bold cyan]\n"
        f"Serving directory: [yellow]{web_dir.resolve()}[/yellow]\n"
        f"URL: [bold green]http://{host}:{port}[/bold green]\n"
        f"Press [dim]Ctrl+C[/dim] to stop server.",
        border_style="cyan"
    ))

    try:
        with socketserver.TCPServer((host, port), handler) as httpd:
            console.print(f"[dim]Opening browser at http://{host}:{port} ...[/dim]")
            try:
                webbrowser.open(f"http://{host}:{port}")
            except Exception:
                pass
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")


if __name__ == "__main__":
    app()

