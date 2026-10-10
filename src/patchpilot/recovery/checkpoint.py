"""SQLite Checkpoint Store.
Persists run checkpoints, state transitions, patch attempts, and verification results.
"""

import json
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from patchpilot.models import RunReport, PatchAttempt


class CheckpointStore:
    def __init__(self, db_path: Path = Path(".patchpilot_state.db")):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    issue_id TEXT,
                    issue_title TEXT,
                    final_state TEXT,
                    success INTEGER,
                    total_duration REAL,
                    neatlogs_trace_id TEXT,
                    entire_checkpoint_id TEXT,
                    summary TEXT,
                    full_report_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    attempt_number INTEGER,
                    target_file TEXT,
                    applied INTEGER,
                    passed INTEGER,
                    failure_category TEXT,
                    recovery_decision TEXT,
                    unified_diff TEXT,
                    attempt_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                )
            """)
            conn.commit()

    def save_run(self, report: RunReport):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attempts WHERE run_id = ?", (report.run_id,))
            cursor.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, issue_id, issue_title, final_state, success,
                    total_duration, neatlogs_trace_id, entire_checkpoint_id,
                    summary, full_report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.run_id,
                report.issue.id,
                report.issue.title,
                report.final_state.value,
                1 if report.success else 0,
                report.total_duration_seconds,
                report.neatlogs_trace_id or "",
                report.entire_checkpoint_id or "",
                report.summary,
                report.model_dump_json()
            ))

            for attempt in report.attempts:
                test_passed = 1 if (attempt.test_result and attempt.test_result.passed) else 0
                cursor.execute("""
                    INSERT INTO attempts (
                        run_id, attempt_number, target_file, applied, passed,
                        failure_category, recovery_decision, unified_diff, attempt_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.run_id,
                    attempt.attempt_number,
                    attempt.target_file,
                    1 if attempt.applied_successfully else 0,
                    test_passed,
                    attempt.failure_category.value,
                    attempt.recovery_decision.value if attempt.recovery_decision else "",
                    attempt.unified_diff,
                    attempt.model_dump_json()
                ))
            conn.commit()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            if not row:
                return None
            run_dict = dict(row)
            cursor.execute("SELECT * FROM attempts WHERE run_id = ? ORDER BY attempt_number ASC", (run_id,))
            run_dict["attempts"] = [dict(a) for a in cursor.fetchall()]
            return run_dict

    def list_runs(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT run_id, issue_id, issue_title, final_state, success, total_duration, neatlogs_trace_id, entire_checkpoint_id, created_at FROM runs ORDER BY created_at DESC")
            return [dict(r) for r in cursor.fetchall()]
