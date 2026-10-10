"""
Core Orchestrator for PatchPilot AI.
Coordinates issue intake, reproduction, investigation, bounded patch loops, verified recovery,
and telemetry reporting.
"""

import ast
import uuid
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from patchpilot.config import config
from patchpilot.models import (
    Issue, AgentState, RunReport, PatchAttempt,
    InvestigationPlan, VerificationReport, FailureCategory, RecoveryAction
)
from patchpilot.state_machine import AgentStateMachine
from patchpilot.llm.provider import BaseLLMProvider, get_llm_provider
from patchpilot.tools.github import GitHubIssueTool
from patchpilot.tools.repository import RepositoryTool
from patchpilot.tools.reproduce import ReproductionTool
from patchpilot.tools.patch import PatchTool
from patchpilot.tools.test_runner import TestRunnerTool
from patchpilot.recovery.checkpoint import CheckpointStore
from patchpilot.recovery.retry_policy import RetryPolicy
from patchpilot.verification.acceptance import AcceptanceVerifier
from patchpilot.verification.regression import RegressionVerifier
from patchpilot.telemetry.tracing import NeatlogsTracer, TraceBuilder
from patchpilot.reporting.report import ReportGenerator


def _parse_investigation(text: str) -> Tuple[str, List[str], str, str]:
    hypo, sol, strat = "", "", ""
    files: List[str] = []
    for line in (text or "").splitlines():
        up = line.strip().upper()
        if up.startswith("HYPOTHESIS:"):
            hypo = line.split(":", 1)[1].strip()
        elif up.startswith("RELEVANT_FILES:"):
            raw = line.split(":", 1)[1]
            files = [p.strip().strip("./") for p in raw.replace(";", ",").split(",") if p.strip()]
        elif up.startswith("PROPOSED_SOLUTION:"):
            sol = line.split(":", 1)[1].strip()
        elif up.startswith("TEST_STRATEGY:"):
            strat = line.split(":", 1)[1].strip()
    return hypo, files, sol, strat


def _parse_patch_response(text: str) -> Tuple[str, str, str]:
    target, orig, new = "", "", ""
    if not text or "ORIGINAL_CODE:" not in text or "PATCHED_CODE:" not in text:
        return target, orig, new
    head, _, tail = text.partition("PATCHED_CODE:")
    new = tail.strip().strip("`").strip()
    _, _, after_orig = head.partition("ORIGINAL_CODE:")
    after_orig = after_orig.strip()
    if "TARGET_FILE:" in head.split("ORIGINAL_CODE:")[0]:
        pre = head.split("ORIGINAL_CODE:")[0]
        _, _, tf = pre.partition("TARGET_FILE:")
        target = tf.strip().splitlines()[0].strip().strip("./") if tf.strip() else ""
    orig = after_orig.strip().strip("`").strip()
    return target, orig, new


def _validate_patch_syntax(repo_tool, rel_path: str, original: str, replacement: str) -> Optional[str]:
    try:
        content = repo_tool.read_file_safe(rel_path)
    except (ValueError, FileNotFoundError, OSError) as e:
        return f"Cannot read {rel_path}: {e}"
    if original not in content:
        return f"Original snippet not found in {rel_path}."
    candidate = content.replace(original, replacement, 1)
    if rel_path.endswith(".py"):
        try:
            ast.parse(candidate)
        except SyntaxError as e:
            return f"Patched Python is invalid: {e}"
    return None


class PatchPilotOrchestrator:
    def __init__(
        self,
        repo_dir: Path,
        llm_provider: Optional[BaseLLMProvider] = None,
        max_attempts: int = config.max_attempts,
        tracer: Optional[NeatlogsTracer] = None,
        checkpoint_store: Optional[CheckpointStore] = None
    ):
        self.repo_dir = repo_dir.resolve()
        self.llm = llm_provider or get_llm_provider()
        self.max_attempts = max_attempts
        self.tracer = tracer or NeatlogsTracer()
        self.checkpoint_store = checkpoint_store or CheckpointStore(db_path=config.checkpoint_db_path)

        self.repo_tool = RepositoryTool(self.repo_dir)
        self.patch_tool = PatchTool(self.repo_dir)
        self.repro_tool = ReproductionTool(self.repo_dir)
        self.test_runner = TestRunnerTool(self.repo_dir)
        self.retry_policy = RetryPolicy(max_attempts=max_attempts)
        self.acceptance_verifier = AcceptanceVerifier(self.repo_dir)
        self.regression_verifier = RegressionVerifier(self.repo_dir)

    def run(self, issue: Issue, regression_command: Optional[str] = None) -> RunReport:
        """
        Executes the autonomous issue-to-verified-fix workflow.
        """
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        sm = AgentStateMachine()

        trace_builder = TraceBuilder(
            tracer=self.tracer,
            workflow_name="patchpilot-issue-fix",
            run_id=run_id,
            issue_id=issue.id
        )

        attempts_list: List[PatchAttempt] = []
        reproduction_res = None
        investigation_plan = None
        verification_report = None
        overall_success = False

        try:
            # 1. State: INTAKE
            sm.transition_to(AgentState.INTAKE, f"Starting intake for issue #{issue.id}")
            trace_builder.record_tool_span("issue_intake", {"issue_id": issue.id, "title": issue.title}, "Intake validated.")

            # 2. State: INVESTIGATING
            sm.transition_to(AgentState.INVESTIGATING, "Analyzing repository context and error patterns")
            files_found = self.repo_tool.discover_files()
            rel_files = [str(f.relative_to(self.repo_dir)) for f in files_found]

            investigation_prompt = (
                f"Analyze issue: {issue.title}\nDescription: {issue.body}\n"
                f"Candidate files: {rel_files[:10]}\n"
                f"Reply in exactly this format:\n"
                f"HYPOTHESIS: <one-sentence root cause>\n"
                f"RELEVANT_FILES: <comma-separated repo-relative paths>\n"
                f"PROPOSED_SOLUTION: <concrete fix>\n"
                f"TEST_STRATEGY: <how to verify>"
            )
            investigation_response = self.llm.generate(investigation_prompt)
            trace_builder.record_llm_span("investigate_root_cause", config.model, investigation_prompt, investigation_response)

            hypothesis, relevant, solution, strategy = _parse_investigation(
                investigation_response
            )
            llm_files = [f for f in relevant if f]
            # Prefer explicit issue hints, then validated LLM files, then discovery.
            validated_llm_files = []
            for cand in llm_files:
                try:
                    self.repo_tool.read_file_safe(cand)
                    validated_llm_files.append(cand)
                except (ValueError, FileNotFoundError):
                    continue
            if issue.file_hints:
                target_files = [h for h in issue.file_hints]
            elif validated_llm_files:
                target_files = validated_llm_files
            else:
                target_files = rel_files[:2]
            investigation_plan = InvestigationPlan(
                root_cause_hypothesis=hypothesis or f"Hypothesis derived from issue #{issue.id}",
                relevant_files=target_files,
                proposed_solution=solution or "Implement defensive check / boundary correction",
                test_strategy=strategy or issue.reproduction_command or "pytest tests/ -v",
            )

            # 3. State: REPRODUCING
            sm.transition_to(AgentState.REPRODUCING, "Executing baseline tests to reproduce failure")
            reproduction_res = self.repro_tool.reproduce(issue)
            trace_builder.record_tool_span(
                "baseline_reproduction",
                {"cmd": reproduction_res.command_executed},
                {"reproduced": reproduction_res.reproduced, "exit_code": reproduction_res.baseline_result.exit_code}
            )

            # 4. Patch & Recovery Loop
            sm.transition_to(AgentState.PATCHING, "Entering bounded patch generation loop")
            current_attempt = 1
            last_failure_category = FailureCategory.NONE
            recovery_guidance = ""

            while current_attempt <= self.max_attempts:
                # If we were in RECOVERING, transition back to PATCHING
                if sm.current_state == AgentState.RECOVERING:
                    sm.transition_to(AgentState.PATCHING, f"Starting attempt #{current_attempt}")

                attempt_strategy = f"Attempt #{current_attempt}: " + (recovery_guidance or "Initial direct fix hypothesis")

                # Generate patch via LLM with real file context
                ctx_parts = []
                for tf in target_files[:3]:
                    try:
                        ctx_parts.append(f"--- {tf} ---\n{self.repo_tool.read_file_safe(tf)[:4000]}")
                    except (ValueError, FileNotFoundError, OSError):
                        continue
                ctx_block = "\n\n".join(ctx_parts) if ctx_parts else "(no file context)"
                patch_prompt = (
                    f"Generate code replacement for issue '{issue.title}'.\n"
                    f"Description: {issue.body[:1000]}\n"
                    f"Previous notes: {recovery_guidance}\n"
                    f"Target files: {target_files}\n"
                    f"Contents:\n{ctx_block}\n\n"
                    f"Reply EXACTLY:\nTARGET_FILE: <path>\nORIGINAL_CODE:\n<verbatim>\nPATCHED_CODE:\n<fix>"
                )
                patch_code_resp = self.llm.generate(patch_prompt)
                trace_builder.record_llm_span(f"generate_patch_attempt_{current_attempt}", config.model, patch_prompt, patch_code_resp)

                # Extract replacement snippets from provider or file content
                target_file_rel = target_files[0] if target_files else "app.py"
                original_text = ""
                replacement_text = ""

                parsed_target, original_text, replacement_text = _parse_patch_response(patch_code_resp)
                if parsed_target:
                    target_file_rel = parsed_target

                if not original_text or not replacement_text:
                    # LLM gave no usable patch: fail this attempt cleanly and pivot.
                    from patchpilot.models import TestExecutionResult as _TER
                    _parse_fail = _TER(
                        command="patch-parse", exit_code=1, stdout="",
                        stderr="LLM response missing usable ORIGINAL_CODE/PATCHED_CODE.",
                        duration_seconds=0.0, passed=False,
                        summary="Patch parse failure.",
                    )
                    _fc = FailureCategory.INCOMPLETE_PATCH
                    _act, _guide = self.retry_policy.evaluate_recovery(current_attempt, _fc, _parse_fail)
                    attempts_list.append(PatchAttempt(
                        attempt_number=current_attempt, strategy_description=attempt_strategy,
                        target_file=target_file_rel, original_snippet=original_text,
                        patched_snippet=replacement_text, unified_diff="",
                        applied_successfully=False, test_result=None,
                        failure_category=_fc, recovery_decision=_act, recovery_notes=_guide,
                    ))
                    if _act == RecoveryAction.TERMINATE_MAX_BUDGET:
                        sm.transition_to(AgentState.FAILED, "Retry budget exhausted.")
                        break
                    sm.transition_to(AgentState.RECOVERING, f"Pivoting: {_guide}")
                    recovery_guidance = _guide
                    current_attempt += 1
                    continue

                _syn_err = _validate_patch_syntax(self.repo_tool, target_file_rel, original_text, replacement_text)
                if _syn_err:
                    from patchpilot.models import TestExecutionResult as _TER2
                    _syn_fail = _TER2(
                        command="patch-syntax-check", exit_code=1, stdout="",
                        stderr=_syn_err, duration_seconds=0.0, passed=False,
                        summary="Patch pre-check failed.",
                    )
                    _fc2 = (
                        FailureCategory.SYNTAX_ERROR
                        if "invalid" in _syn_err.lower()
                        else FailureCategory.INCOMPLETE_PATCH
                    )
                    _act2, _guide2 = self.retry_policy.evaluate_recovery(current_attempt, _fc2, _syn_fail)
                    attempts_list.append(PatchAttempt(
                        attempt_number=current_attempt, strategy_description=attempt_strategy,
                        target_file=target_file_rel, original_snippet=original_text,
                        patched_snippet=replacement_text, unified_diff="",
                        applied_successfully=False, test_result=None,
                        failure_category=_fc2, recovery_decision=_act2, recovery_notes=_guide2,
                    ))
                    if _act2 == RecoveryAction.TERMINATE_MAX_BUDGET:
                        sm.transition_to(AgentState.FAILED, "Retry budget exhausted.")
                        break
                    sm.transition_to(AgentState.RECOVERING, f"Pivoting: {_guide2}")
                    recovery_guidance = _guide2
                    current_attempt += 1
                    continue

                applied, diff, err = self.patch_tool.apply_replacement(
                    target_file_rel,
                    original_text,
                    replacement_text
                )

                if not applied:
                    # Patch could not be applied (missing snippet, traversal, etc.)
                    from patchpilot.models import TestExecutionResult as _TER3
                    _apply_fail = _TER3(
                        command="patch-apply", exit_code=1, stdout="",
                        stderr=err or "Patch apply failed.",
                        duration_seconds=0.0, passed=False,
                        summary="Patch apply failed.",
                    )
                    _fc3 = FailureCategory.INCOMPLETE_PATCH
                    _act3, _guide3 = self.retry_policy.evaluate_recovery(current_attempt, _fc3, _apply_fail)
                    attempts_list.append(PatchAttempt(
                        attempt_number=current_attempt, strategy_description=attempt_strategy,
                        target_file=target_file_rel, original_snippet=original_text,
                        patched_snippet=replacement_text, unified_diff=diff,
                        applied_successfully=False, test_result=None,
                        failure_category=_fc3, recovery_decision=_act3, recovery_notes=_guide3,
                    ))
                    trace_builder.record_tool_span(
                        f"patch_apply_failure_{current_attempt}",
                        {"target_file": target_file_rel}, err or "apply failed",
                    )
                    if _act3 == RecoveryAction.TERMINATE_MAX_BUDGET:
                        sm.transition_to(AgentState.FAILED, "Retry budget exhausted.")
                        break
                    sm.transition_to(AgentState.RECOVERING, f"Pivoting: {_guide3}")
                    recovery_guidance = _guide3
                    current_attempt += 1
                    continue

                # State: TESTING
                sm.transition_to(AgentState.TESTING, f"Running tests on patch attempt #{current_attempt}")
                test_cmd = issue.reproduction_command or "pytest tests/ -v"
                test_result = self.test_runner.run_command(test_cmd)
                trace_builder.record_tool_span(
                    f"test_run_attempt_{current_attempt}",
                    {"cmd": test_cmd},
                    {"passed": test_result.passed, "exit_code": test_result.exit_code}
                )

                # State: EVALUATING
                sm.transition_to(AgentState.EVALUATING, f"Evaluating outcome of attempt #{current_attempt}")

                # Run regression test suite if provided to ensure no regressions introduced
                reg_result = None
                if regression_command:
                    reg_result = self.test_runner.run_command(regression_command)
                    trace_builder.record_tool_span(
                        f"regression_run_attempt_{current_attempt}",
                        {"cmd": regression_command},
                        {"passed": reg_result.passed, "exit_code": reg_result.exit_code}
                    )

                if test_result.passed and (reg_result is None or reg_result.passed):
                    # Genuine Verified Success on this attempt!
                    attempt_record = PatchAttempt(
                        attempt_number=current_attempt,
                        strategy_description=attempt_strategy,
                        target_file=target_file_rel,
                        original_snippet=original_text,
                        patched_snippet=replacement_text,
                        unified_diff=diff,
                        applied_successfully=applied,
                        test_result=test_result,
                        failure_category=FailureCategory.NONE,
                        recovery_decision=None,
                        recovery_notes="Attempt passed both reproduction verification and regression test suite."
                    )
                    attempts_list.append(attempt_record)
                    break
                else:
                    # Failed attempt: Execute Verified Recovery Policy
                    if test_result.passed and reg_result and not reg_result.passed:
                        failure_cat = FailureCategory.REGRESSION_INTRODUCED
                        eval_result = reg_result
                    else:
                        failure_cat = self.retry_policy.classify_failure(test_result)
                        eval_result = test_result

                    recovery_action, guidance = self.retry_policy.evaluate_recovery(
                        current_attempt, failure_cat, eval_result
                    )

                    attempt_record = PatchAttempt(
                        attempt_number=current_attempt,
                        strategy_description=attempt_strategy,
                        target_file=target_file_rel,
                        original_snippet=original_text,
                        patched_snippet=replacement_text,
                        unified_diff=diff,
                        applied_successfully=applied,
                        test_result=eval_result,
                        failure_category=failure_cat,
                        recovery_decision=recovery_action,
                        recovery_notes=guidance
                    )
                    attempts_list.append(attempt_record)

                    # Rollback the failed modification before next attempt
                    self.patch_tool.rollback(target_file_rel)
                    trace_builder.record_tool_span(
                        f"rollback_attempt_{current_attempt}",
                        {"target_file": target_file_rel},
                        "Rolled back cleanly to baseline."
                    )

                    if recovery_action == RecoveryAction.TERMINATE_MAX_BUDGET:
                        sm.transition_to(AgentState.FAILED, "Retry budget exhausted without passing tests.")
                        break

                    # Pivot to recovery state for next attempt
                    sm.transition_to(AgentState.RECOVERING, f"Pivoting strategy: {guidance}")
                    last_failure_category = failure_cat
                    recovery_guidance = guidance
                    current_attempt += 1

            # 5. Final Independent Verification
            last_attempt = attempts_list[-1] if attempts_list else None
            if last_attempt and last_attempt.test_result and last_attempt.test_result.passed:
                acceptance_res = self.acceptance_verifier.verify(issue.reproduction_command or "pytest tests/ -v")
                reg_cmd = regression_command
                if not reg_cmd and (self.repo_dir / "tests").exists():
                    reg_cmd = "pytest tests/ -v"

                if reg_cmd:
                    regression_res = self.regression_verifier.verify(reg_cmd)
                    all_passed = acceptance_res.passed and regression_res.passed
                else:
                    regression_res = acceptance_res
                    all_passed = acceptance_res.passed
                verification_report = VerificationReport(
                    acceptance_passed=acceptance_res.passed,
                    regression_passed=regression_res.passed,
                    all_tests_passed=all_passed,
                    acceptance_summary=acceptance_res.summary,
                    regression_summary=regression_res.summary,
                    evidence_diff=last_attempt.unified_diff
                )
                trace_builder.record_tool_span(
                    "independent_verification",
                    {"acceptance_cmd": acceptance_res.command, "regression_cmd": reg_cmd},
                    {"acceptance_passed": acceptance_res.passed, "regression_passed": regression_res.passed}
                )

                if all_passed:
                    if sm.current_state != AgentState.VERIFIED:
                        sm.transition_to(AgentState.VERIFIED, "Independent acceptance and regression suites confirmed fix.")
                    overall_success = True
                else:
                    sm.transition_to(AgentState.FAILED, "Regression tests failed after patch.")
            else:
                if sm.current_state != AgentState.FAILED:
                    sm.transition_to(AgentState.FAILED, "No patch attempt satisfied test verification.")

        except Exception as e:
            if sm.can_transition_to(AgentState.FAILED):
                sm.transition_to(AgentState.FAILED, f"Unhandled exception: {str(e)}")

        total_duration = round(time.time() - start_time, 3)

        # 6. Flush Telemetry to Neatlogs
        trace_id = trace_builder.finish(
            final_output={"success": overall_success, "final_state": sm.current_state.value}
        )

        run_summary = (
            f"Run {run_id}: Issue #{issue.id} verified and resolved in {total_duration:.2f}s "
            f"across {len(attempts_list)} attempt(s)."
            if overall_success
            else f"Run {run_id}: Fix attempt for Issue #{issue.id} failed after {len(attempts_list)} attempt(s)."
        )

        report = RunReport(
            run_id=run_id,
            issue=issue,
            final_state=sm.current_state,
            reproduction=reproduction_res,
            investigation=investigation_plan,
            attempts=attempts_list,
            verification=verification_report,
            neatlogs_trace_id=trace_id,
            total_duration_seconds=total_duration,
            success=overall_success,
            summary=run_summary
        )

        # 7. Persist Checkpoint to SQLite
        self.checkpoint_store.save_run(report)
        return report
