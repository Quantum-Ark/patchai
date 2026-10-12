"""
PatchPilot AI — Background Repair Runner.
Executes autonomous repair jobs asynchronously in worker threads,
recording fine-grained real-time execution events, patch attempts,
and verification outcomes to the persistent SQLite database.
"""

import os
import time
import uuid
import json
import shutil
import logging
import tempfile
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

from patchpilot.config import config
from patchpilot.models import Issue, AgentState, FailureCategory
from patchpilot.orchestrator import PatchPilotOrchestrator
from patchpilot.llm.provider import get_llm_provider, MockLLMProvider, BaseLLMProvider
from patchpilot.tools.github import GitHubIssueTool, GitHubPRTool
from patchpilot.db import db

logger = logging.getLogger("patchpilot.runner")


class RepairRunner:
    def __init__(self):
        self._active_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def is_running(self, run_id: str) -> bool:
        with self._lock:
            thread = self._active_threads.get(run_id)
            return bool(thread and thread.is_alive())

    def get_active_count(self) -> int:
        with self._lock:
            # Clean up dead threads
            dead = [rid for rid, t in self._active_threads.items() if not t.is_alive()]
            for rid in dead:
                del self._active_threads[rid]
            return len(self._active_threads)

    def start_repair(
        self,
        issue: Issue,
        repo_owner: str,
        repo_name: str,
        repo_dir: Optional[Path] = None,
        target_branch: str = "main",
        reproduction_command: Optional[str] = None,
        regression_command: Optional[str] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        benchmark_id: Optional[str] = None,
        github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers a new repair run in the database and launches execution in a background thread.
        Returns the initial run descriptor.
        """
        run_id = f"run-{uuid.uuid4().hex[:8]}"

        # Insert run record in database
        run_record = db.create_run(
            run_id=run_id,
            issue_id=str(issue.id),
            issue_title=issue.title,
            repo_owner=repo_owner,
            repo_name=repo_name,
            repo_url=issue.repo_url,
            target_branch=target_branch,
            reproduction_command=reproduction_command or issue.reproduction_command
        )

        db.append_event(
            run_id=run_id,
            event_type="JOB_CREATED",
            state="INTAKE",
            message=f"Created repair run {run_id} for issue #{issue.id}: {issue.title}",
            payload={"repo": f"{repo_owner}/{repo_name}", "target_branch": target_branch}
        )

        thread = threading.Thread(
            target=self._run_worker,
            args=(run_id, issue, repo_owner, repo_name, repo_dir, target_branch, reproduction_command, regression_command, llm_provider, benchmark_id, github_token),
            name=f"patchpilot-{run_id}",
            daemon=True
        )

        with self._lock:
            self._active_threads[run_id] = thread
            thread.start()

        return run_record

    def _run_worker(
        self,
        run_id: str,
        issue: Issue,
        repo_owner: str,
        repo_name: str,
        repo_dir: Optional[Path],
        target_branch: str,
        reproduction_command: Optional[str],
        regression_command: Optional[str],
        llm_provider: Optional[BaseLLMProvider],
        benchmark_id: Optional[str],
        github_token: Optional[str]
    ):
        start_time = time.time()
        temp_dir: Optional[str] = None
        repo_root = Path(__file__).resolve().parent.parent.parent

        try:
            db.append_event(
                run_id=run_id,
                event_type="STATE_CHANGE",
                state="INTAKE",
                message="Initializing isolated execution sandbox and verifying repo state..."
            )

            # 1. Determine execution target directory
            if benchmark_id:
                case_map = {
                    "case_1": "case_1_logic_bug",
                    "case_2": "case_2_boundary_bug",
                    "case_3": "case_3_regression_recovery",
                }
                folder_name = case_map.get(benchmark_id, "case_1_logic_bug")
                src_fixture = repo_root / "benchmarks" / folder_name

                temp_dir = tempfile.mkdtemp(prefix=f"patchpilot-{benchmark_id}-")
                dest_dir = Path(temp_dir) / folder_name
                shutil.copytree(src_fixture, dest_dir)
                target_repo_dir = dest_dir

                # Reset baseline code and load issue.json
                issue_path = dest_dir / "issue.json"
                if issue_path.exists():
                    with open(issue_path, "r", encoding="utf-8") as f:
                        idata = json.load(f)
                    issue = Issue(
                        id=idata["id"],
                        title=idata["title"],
                        body=idata["body"],
                        file_hints=idata.get("file_hints", []),
                        reproduction_command=idata.get("reproduction_command")
                    )
                    if "regression_command" in idata and not regression_command:
                        regression_command = idata["regression_command"]

                if benchmark_id == "case_1":
                    (dest_dir / "calc.py").write_text(
                        "def safe_divide(x: float, y: float) -> float:\n"
                        "    \"\"\"Divide x by y. Needs to handle y == 0 by raising ValueError.\"\"\"\n"
                        "    return x / y\n",
                        encoding="utf-8"
                    )
                elif benchmark_id == "case_2":
                    (dest_dir / "paginator.py").write_text(
                        "def paginate(items: list, page: int = 1, page_size: int = 10) -> list:\n"
                        "    if len(items) == 0 and page == 1:\n"
                        "        return [items[0]]\n"
                        "    start = (page - 1) * page_size\n"
                        "    return items[start:start + page_size]\n",
                        encoding="utf-8"
                    )
                elif benchmark_id == "case_3":
                    (dest_dir / "pricing.py").write_text(
                        "def calculate_price(base_price: float, quantity: int) -> float:\n"
                        "    multiplier = 1.0\n"
                        "    if quantity >= 10:\n"
                        "        multiplier = 0.9\n"
                        "    return round(base_price * quantity * multiplier, 2)\n",
                        encoding="utf-8"
                    )

                # Equip mock provider if no real keys present
                if llm_provider is None:
                    has_live_key = any([
                        os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") not in ("your_openai_api_key_here", "<your-key>"),
                        os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") not in ("your_gemini_api_key_here", "<your-key>"),
                        os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") not in ("your_anthropic_api_key_here", "<your-key>"),
                        os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") not in ("your_groq_api_key_here", "<your-key>"),
                    ])
                    if not has_live_key:
                        if benchmark_id == "case_1":
                            llm_provider = MockLLMProvider(sequential_patches=[
                                "TARGET_FILE: calc.py\nORIGINAL_CODE: return x / y\nPATCHED_CODE: if y == 0:\n        raise ValueError('Division by zero')\n    return x / y"
                            ])
                        elif benchmark_id == "case_2":
                            llm_provider = MockLLMProvider(sequential_patches=[
                                "TARGET_FILE: paginator.py\nORIGINAL_CODE: if len(items) == 0 and page == 1:\n        return [items[0]]\nPATCHED_CODE: if len(items) == 0:\n        return []\n"
                            ])
                        elif benchmark_id == "case_3":
                            llm_provider = MockLLMProvider(sequential_patches=[
                                "TARGET_FILE: pricing.py\nORIGINAL_CODE: multiplier = 1.0\nPATCHED_CODE: if quantity <= 0: raise ValueError('Quantity must be greater than 0')\n    return round(base_price * quantity, 2)",
                                "TARGET_FILE: pricing.py\nORIGINAL_CODE: multiplier = 1.0\nPATCHED_CODE: if quantity <= 0:\n        raise ValueError('Quantity must be greater than 0')\n    multiplier = 1.0"
                            ])
            elif repo_dir:
                target_repo_dir = repo_dir
            else:
                target_repo_dir = repo_root

            # 2. Resolve LLM provider
            if llm_provider is None:
                llm_provider = get_llm_provider()

            db.append_event(
                run_id=run_id,
                event_type="STATE_CHANGE",
                state="INVESTIGATING",
                message=f"Starting LLM investigation with model [{getattr(llm_provider, 'model', 'default')}]"
            )

            # 3. Instantiate orchestrator
            orchestrator = PatchPilotOrchestrator(
                repo_dir=target_repo_dir,
                llm_provider=llm_provider
            )

            # 4. Run Orchestrator
            db.append_event(
                run_id=run_id,
                event_type="STATE_CHANGE",
                state="REPRODUCING",
                message=f"Executing baseline reproduction suite: {reproduction_command or issue.reproduction_command or 'default test runner'}"
            )

            report = orchestrator.run(issue, regression_command=regression_command)

            # 5. Record Attempts in DB
            for att in report.attempts:
                with db._connect() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO attempts (
                            run_id, attempt_number, target_file, applied, passed,
                            failure_category, recovery_decision, unified_diff, attempt_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        att.attempt_number,
                        att.target_file,
                        1 if att.applied_successfully else 0,
                        1 if att.test_result and att.test_result.passed else 0,
                        att.failure_category.value if att.failure_category else None,
                        att.recovery_decision.value if att.recovery_decision else None,
                        att.unified_diff or "",
                        att.model_dump_json()
                    ))
                    conn.commit()

                event_msg = (
                    f"Attempt #{att.attempt_number} on {att.target_file}: "
                    f"{'PASSED' if att.test_result and att.test_result.passed else 'FAILED (' + (att.failure_category.value if att.failure_category else 'test') + ')'}"
                )
                if att.recovery_decision:
                    event_msg += f" -> Decision: {att.recovery_decision.value}"

                db.append_event(
                    run_id=run_id,
                    event_type="ATTEMPT_COMPLETED",
                    state="EVALUATING",
                    message=event_msg,
                    payload={"attempt": att.attempt_number, "target_file": att.target_file}
                )

            # 6. Extract diff text
            diff_text = ""
            if report.verification and report.verification.evidence_diff:
                diff_text = report.verification.evidence_diff
            elif report.attempts and report.attempts[-1].unified_diff:
                diff_text = report.attempts[-1].unified_diff

            # 7. Final status & duration
            duration = round(time.time() - start_time, 3)
            final_status = "VERIFIED" if report.success else "FAILED"

            db.append_event(
                run_id=run_id,
                event_type="RUN_COMPLETED",
                state=final_status,
                message=f"Run {run_id} finished in {duration:.2f}s with status [{final_status}]. {report.summary}",
                payload={"success": report.success, "duration": duration, "neatlogs_trace_id": report.neatlogs_trace_id}
            )

            db.update_run_finished(
                run_id=run_id,
                status=final_status,
                success=report.success,
                duration=duration,
                neatlogs_trace_id=report.neatlogs_trace_id,
                summary=report.summary,
                diff_text=diff_text,
                full_report_json=report.model_dump_json()
            )

        except Exception as e:
            logger.error(f"Execution failed for run {run_id}: {e}", exc_info=True)
            duration = round(time.time() - start_time, 3)
            db.append_event(
                run_id=run_id,
                event_type="ERROR",
                state="FAILED",
                message=f"Fatal error during repair execution: {str(e)}",
                payload={"error": str(e)}
            )
            db.update_run_finished(
                run_id=run_id,
                status="FAILED",
                success=False,
                duration=duration,
                summary=f"Run terminated with error: {str(e)}"
            )
        finally:
            with self._lock:
                if run_id in self._active_threads:
                    del self._active_threads[run_id]

            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass


# Global repair runner
runner = RepairRunner()
