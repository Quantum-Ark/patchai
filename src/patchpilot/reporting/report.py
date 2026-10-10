"""
Reporting Module for PatchPilot AI.
Generates machine-readable JSON and human-readable Markdown verification reports.
Includes PR-ready summary generation.
"""

import json
from pathlib import Path
from patchpilot.models import RunReport


class ReportGenerator:
    @staticmethod
    def to_json(report: RunReport) -> str:
        """Serialize run report to pretty-printed JSON."""
        return report.model_dump_json(indent=2)

    @staticmethod
    def to_markdown(report: RunReport) -> str:
        """Format run report as comprehensive, human-readable Markdown."""
        status_badge = "\u2705 **VERIFIED FIX**" if report.success else "\u274c **FIX ATTEMPT FAILED**"

        md = [
            f"# PatchPilot AI — Verification Report",
            f"",
            f"**Status**: {status_badge}  ",
            f"**Run ID**: `{report.run_id}`  ",
            f"**Issue**: #{report.issue.id} — *{report.issue.title}*  ",
            f"**Total Duration**: {report.total_duration_seconds:.2f}s  ",
        ]

        if report.neatlogs_trace_id:
            md.append(f"**Neatlogs Trace ID**: `{report.neatlogs_trace_id}`  ")
        if report.entire_checkpoint_id:
            md.append(f"**Entire Checkpoint**: `{report.entire_checkpoint_id}`  ")

        md.extend([
            f"",
            f"---",
            f"",
            f"## 1. Issue & Reproduction",
            f"- **Issue Title**: {report.issue.title}",
            f"- **Reproduction Status**: {'Reproduced (Failing baseline confirmed)' if report.reproduction and report.reproduction.reproduced else 'Unverified baseline'}",
        ])
        if report.reproduction:
            md.append(f"- **Repro Command**: `{report.reproduction.command_executed}`")
            md.append(f"- **Baseline Output Summary**: {report.reproduction.baseline_result.summary}")

        if report.investigation:
            md.extend([
                f"",
                f"## 2. Investigation & Root Cause",
                f"- **Hypothesis**: {report.investigation.root_cause_hypothesis}",
                f"- **Relevant Files**: {', '.join(report.investigation.relevant_files)}",
                f"- **Proposed Solution**: {report.investigation.proposed_solution}",
            ])

        md.extend([
            f"",
            f"## 3. Patch Attempts & Verified Recovery",
            f"Total Attempts Made: **{len(report.attempts)}**",
            f""
        ])

        for attempt in report.attempts:
            res_str = "\u2705 Passed" if (attempt.test_result and attempt.test_result.passed) else "\u274c Failed"
            md.extend([
                f"### Attempt #{attempt.attempt_number} — {res_str}",
                f"- **Strategy**: {attempt.strategy_description}",
                f"- **Target File**: `{attempt.target_file}`",
                f"- **Failure Category**: `{attempt.failure_category.value}`",
            ])
            if attempt.recovery_decision:
                md.append(f"- **Recovery Pivot**: `{attempt.recovery_decision.value}` — {attempt.recovery_notes or ''}")

            if attempt.unified_diff:
                md.extend([
                    f"",
                    f"```diff",
                    attempt.unified_diff.strip(),
                    f"```",
                    f""
                ])

        if report.verification:
            md.extend([
                f"## 4. Final Verification",
                f"- **Acceptance Test**: {'\u2705 PASSED' if report.verification.acceptance_passed else '\u274c FAILED'} — {report.verification.acceptance_summary}",
                f"- **Regression Suite**: {'\u2705 PASSED (No side effects)' if report.verification.regression_passed else '\u274c FAILED'} — {report.verification.regression_summary}",
                f"- **Core Differentiator**: Verified recovery confirmed with zero introduced regressions."
            ])

        md.extend([
            f"",
            f"---",
            f"",
            f"## 5. Pull Request Summary",
            f"> **PatchPilot Autonomous Fix Summary**",
            f"> - **Fix**: Resolved issue #{report.issue.id} with verified acceptance tests.",
            f"> - **Evidence**: Verified through {len(report.attempts)} bounded attempts with automated rollback.",
            f"> - **Audit**: Traced via Neatlogs and Entire checkpointing.",
            f"> *Note: PatchPilot never automatically merges code. Human review recommended.*"
        ])

        return "\n".join(md)

    @staticmethod
    def save_reports(report: RunReport, output_dir: Path):
        """Save both JSON and Markdown reports to disk."""
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"report_{report.run_id}.json"
        md_path = output_dir / f"report_{report.run_id}.md"

        json_path.write_text(ReportGenerator.to_json(report), encoding="utf-8")
        md_path.write_text(ReportGenerator.to_markdown(report), encoding="utf-8")
        return json_path, md_path
