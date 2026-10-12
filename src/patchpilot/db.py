"""
PatchPilot AI — Persistent SQLite Database Engine.
Stores authenticated GitHub credentials, repository metadata, repair runs,
fine-grained execution events, patch attempts, and Pull Request records.
"""

import json
import logging
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger("patchpilot.db")


def _get_fernet():
    """Return a Fernet instance if PATCHPILOT_TOKEN_KEY is set, else None."""
    key = os.getenv("PATCHPILOT_TOKEN_KEY", "")
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(key.encode("utf-8"))
    except Exception as e:
        logger.warning(f"PATCHPILOT_TOKEN_KEY invalid, storing tokens plaintext: {e}")
        return None


def _encrypt_token(token: str) -> Tuple[str, bool]:
    f = _get_fernet()
    if f is None:
        return token, False
    try:
        return f.encrypt(token.encode("utf-8")).decode("utf-8"), True
    except Exception:
        return token, False


def _decrypt_token(stored: str, encrypted: bool) -> str:
    if not encrypted:
        return stored
    f = _get_fernet()
    if f is None:
        logger.error("Token stored encrypted but PATCHPILOT_TOKEN_KEY is now missing.")
        return ""
    try:
        return f.decrypt(stored.encode("utf-8")).decode("utf-8")
    except Exception:
        logger.error("Failed to decrypt stored GitHub token.")
        return ""


class PatchPilotDB:
    def __init__(self, db_path: Path = Path(".patchpilot_state.db")):
        self.db_path = db_path.resolve()
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            yield conn
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            # 1. GitHub Authentication Table (per-tenant: one PAT per tenant_id)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS github_auth (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    tenant_id TEXT DEFAULT 'default',
                    username TEXT NOT NULL,
                    name TEXT,
                    avatar_url TEXT,
                    token TEXT NOT NULL,
                    token_encrypted INTEGER DEFAULT 0,
                    scopes TEXT,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Migrations for DBs created before these columns existed.
            for _col, _ddl in (
                ("token_encrypted", "ALTER TABLE github_auth ADD COLUMN token_encrypted INTEGER DEFAULT 0"),
                ("tenant_id", "ALTER TABLE github_auth ADD COLUMN tenant_id TEXT DEFAULT 'default'"),
            ):
                try:
                    cursor.execute(f"SELECT {_col} FROM github_auth LIMIT 1")
                except Exception:
                    try:
                        cursor.execute(_ddl)
                    except Exception:
                        pass
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_github_auth_tenant ON github_auth(tenant_id)")
            except Exception:
                pass

            # 2. Repair Runs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    tenant_id TEXT DEFAULT 'default',
                    issue_id TEXT NOT NULL,
                    issue_title TEXT NOT NULL,
                    repo_owner TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    repo_url TEXT,
                    target_branch TEXT DEFAULT 'main',
                    reproduction_command TEXT,
                    final_state TEXT DEFAULT 'INTAKE',
                    status TEXT DEFAULT 'RUNNING',  -- RUNNING, VERIFIED, FAILED, UNVERIFIED, BLOCKED
                    success INTEGER DEFAULT 0,
                    total_duration REAL DEFAULT 0.0,
                    neatlogs_trace_id TEXT,
                    entire_checkpoint_id TEXT,
                    summary TEXT,
                    diff_text TEXT,
                    full_report_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Safe schema migration for existing runs table
            cursor.execute("PRAGMA table_info(runs)")
            existing_columns = {row["name"] for row in cursor.fetchall()}
            columns_to_add = [
                ("status", "TEXT DEFAULT 'RUNNING'"),
                ("repo_owner", "TEXT DEFAULT 'Quantum-Ark'"),
                ("repo_name", "TEXT DEFAULT 'patchai'"),
                ("repo_url", "TEXT DEFAULT ''"),
                ("target_branch", "TEXT DEFAULT 'main'"),
                ("reproduction_command", "TEXT DEFAULT ''"),
                ("diff_text", "TEXT DEFAULT ''"),
                ("updated_at", "TEXT DEFAULT ''"),
                ("tenant_id", "TEXT DEFAULT 'default'"),
            ]
            for col_name, col_def in columns_to_add:
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE runs ADD COLUMN {col_name} {col_def};")
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_tenant ON runs(tenant_id)")
            except Exception:
                pass

            # Backfill status for existing records
            cursor.execute("UPDATE runs SET status = CASE WHEN success = 1 THEN 'VERIFIED' ELSE 'FAILED' END WHERE status IS NULL OR status = '' OR status = 'RUNNING';")


            # 3. Fine-Grained Execution Events Table (For Real-Time Dashboard Streams)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,        -- LOG, STATE_CHANGE, TEST_OUTPUT, RECOVERY, VERIFY
                    state TEXT NOT NULL,             -- INTAKE, INVESTIGATING, REPRODUCING, PATCHING, etc.
                    message TEXT NOT NULL,
                    payload_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
            """)

            # 4. Patch Attempts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    target_file TEXT,
                    applied INTEGER DEFAULT 0,
                    passed INTEGER DEFAULT 0,
                    failure_category TEXT,
                    recovery_decision TEXT,
                    unified_diff TEXT,
                    attempt_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
            """)

            # 5. Pull Requests Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pull_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    repo_owner TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    pr_number INTEGER NOT NULL,
                    pr_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT,
                    branch TEXT NOT NULL,
                    base_branch TEXT DEFAULT 'main',
                    state TEXT DEFAULT 'open',
                    is_draft INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
            """)

            # 6. Repository Cache Table (scoped per tenant so cached private
            # repo metadata from tenant A is never served to tenant B)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY,
                    tenant_id TEXT DEFAULT 'default',
                    owner TEXT NOT NULL,
                    name TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    default_branch TEXT DEFAULT 'main',
                    private INTEGER DEFAULT 0,
                    description TEXT,
                    open_issues_count INTEGER DEFAULT 0,
                    html_url TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_repos_tenant_full ON repositories(tenant_id, full_name)")
            except Exception:
                pass
            # Migration: repositories table predates tenant_id; add + backfill.
            try:
                cursor.execute("PRAGMA table_info(repositories)")
                repo_cols = {row["name"] for row in cursor.fetchall()}
                if "tenant_id" not in repo_cols:
                    cursor.execute("ALTER TABLE repositories ADD COLUMN tenant_id TEXT DEFAULT 'default'")
            except Exception:
                pass

            conn.commit()
            logger.info("Database schema initialized successfully.")

    # --------------------------------------------------------------------------
    # GitHub Authentication Operations
    # --------------------------------------------------------------------------
    def save_github_auth(self, username: str, name: str, avatar_url: str, token: str, scopes: str = "repo", tenant_id: str = "default"):
        stored, encrypted = _encrypt_token(token)
        tid = (tenant_id or "default")[:64]
        with self._connect() as conn:
            cursor = conn.cursor()
            # Per-tenant upsert: at most one PAT per tenant.
            cursor.execute("SELECT id FROM github_auth WHERE tenant_id = ?", (tid,))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE github_auth SET username=?, name=?, avatar_url=?, token=?,
                        token_encrypted=?, scopes=?, connected_at=CURRENT_TIMESTAMP
                    WHERE tenant_id=?
                """, (username, name, avatar_url, stored, 1 if encrypted else 0, scopes, tid))
            else:
                cursor.execute("""
                    INSERT INTO github_auth (tenant_id, username, name, avatar_url, token, token_encrypted, scopes, connected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (tid, username, name, avatar_url, stored, 1 if encrypted else 0, scopes))
            conn.commit()

    def get_github_auth(self, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            if tenant_id is None:
                # Back-compat: legacy single-tenant callers get the default row.
                cursor.execute("SELECT username, name, avatar_url, token, token_encrypted, scopes, connected_at, tenant_id FROM github_auth WHERE tenant_id = 'default' LIMIT 1")
                row = cursor.fetchone()
                if row is None:
                    cursor.execute("SELECT username, name, avatar_url, token, token_encrypted, scopes, connected_at, tenant_id FROM github_auth LIMIT 1")
                    row = cursor.fetchone()
            else:
                cursor.execute("SELECT username, name, avatar_url, token, token_encrypted, scopes, connected_at, tenant_id FROM github_auth WHERE tenant_id = ? LIMIT 1", ((tenant_id or "default")[:64],))
                row = cursor.fetchone()
            if row:
                keys = row.keys()
                raw = row["token"] or ""
                enc = bool(row["token_encrypted"]) if "token_encrypted" in keys else False
                token = _decrypt_token(raw, enc)
                return {
                    "username": row["username"],
                    "name": row["name"] or row["username"],
                    "avatar_url": row["avatar_url"],
                    "token": token,
                    "masked_token": f"****{token[-4:]}" if len(token) > 8 else "***",
                    "scopes": row["scopes"],
                    "connected_at": row["connected_at"]
                }
            return None

    def delete_github_auth(self, tenant_id: Optional[str] = None):
        with self._connect() as conn:
            if tenant_id is None:
                conn.execute("DELETE FROM github_auth WHERE tenant_id = 'default'")
            else:
                conn.execute("DELETE FROM github_auth WHERE tenant_id = ?", ((tenant_id or "default")[:64],))
            conn.commit()

    # --------------------------------------------------------------------------
    # Dashboard Aggregation & Statistics
    # --------------------------------------------------------------------------
    def get_dashboard_stats(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        with self._connect() as conn:
            cursor = conn.cursor()
            scope = ""
            params: List[Any] = []
            if tenant_id is not None:
                scope = " WHERE tenant_id = ?"
                params = [(tenant_id or "default")[:64]]

            cursor.execute(f"SELECT COUNT(*) FROM runs{scope}", params)
            total_runs = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM runs WHERE status = 'RUNNING'{(' AND tenant_id = ?') if tenant_id is not None else ''}", params)
            running_jobs = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM runs WHERE status = 'VERIFIED'{(' AND tenant_id = ?') if tenant_id is not None else ''}", params)
            verified_repairs = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM runs WHERE status IN ('FAILED', 'UNVERIFIED', 'BLOCKED'){(' AND tenant_id = ?') if tenant_id is not None else ''}", params)
            failed_repairs = cursor.fetchone()[0]

            if tenant_id is not None:
                cursor.execute("""
                    SELECT COUNT(*) FROM pull_requests
                    WHERE run_id IN (SELECT run_id FROM runs WHERE tenant_id = ?)
                """, params)
            else:
                cursor.execute("SELECT COUNT(*) FROM pull_requests")
            total_prs = cursor.fetchone()[0]

            if tenant_id is not None:
                cursor.execute("SELECT COUNT(DISTINCT repo_owner || '/' || repo_name) FROM runs WHERE tenant_id = ?", params)
            else:
                cursor.execute("SELECT COUNT(DISTINCT repo_owner || '/' || repo_name) FROM runs")
            active_repos = cursor.fetchone()[0]

            return {
                "total_runs": total_runs,
                "running_jobs": running_jobs,
                "verified_repairs": verified_repairs,
                "failed_repairs": failed_repairs,
                "total_prs": total_prs,
                "active_repos": active_repos,
            }

    # --------------------------------------------------------------------------
    # Run Management & Real-Time Events
    # --------------------------------------------------------------------------
    def create_run(
        self,
        run_id: str,
        issue_id: str,
        issue_title: str,
        repo_owner: str,
        repo_name: str,
        repo_url: Optional[str] = None,
        target_branch: str = "main",
        reproduction_command: Optional[str] = None,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        tid = (tenant_id or "default")[:64]
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runs (
                    run_id, tenant_id, issue_id, issue_title, repo_owner, repo_name,
                    repo_url, target_branch, reproduction_command, final_state, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'INTAKE', 'RUNNING')
            """, (
                run_id, tid, issue_id, issue_title, repo_owner, repo_name,
                repo_url, target_branch, reproduction_command
            ))
            conn.commit()
            return self.get_run(run_id)

    def append_event(self, run_id: str, event_type: str, state: str, message: str, payload: Optional[Dict[str, Any]] = None):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO run_events (run_id, event_type, state, message, payload_json)
                VALUES (?, ?, ?, ?, ?)
            """, (run_id, event_type, state, message, json.dumps(payload) if payload else None))
            # Also update final_state on the run
            cursor.execute("UPDATE runs SET final_state = ?, updated_at = CURRENT_TIMESTAMP WHERE run_id = ?", (state, run_id))
            conn.commit()

    def get_run_events(self, run_id: str, after_id: int = 0, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if tenant_id is not None:
            # Ownership check: events are only visible to the owning tenant.
            owner = self.get_run(run_id, tenant_id=tenant_id)
            if owner is None:
                return []
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, run_id, event_type, state, message, payload_json, created_at
                FROM run_events
                WHERE run_id = ? AND id > ?
                ORDER BY id ASC
            """, (run_id, after_id))
            events = []
            for row in cursor.fetchall():
                payload = json.loads(row["payload_json"]) if row["payload_json"] else None
                events.append({
                    "id": row["id"],
                    "run_id": row["run_id"],
                    "event_type": row["event_type"],
                    "state": row["state"],
                    "message": row["message"],
                    "payload": payload,
                    "created_at": row["created_at"]
                })
            return events

    def update_run_finished(
        self,
        run_id: str,
        status: str,
        success: bool,
        duration: float,
        neatlogs_trace_id: Optional[str] = None,
        entire_checkpoint_id: Optional[str] = None,
        summary: Optional[str] = None,
        diff_text: Optional[str] = None,
        full_report_json: Optional[str] = None
    ):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE runs SET
                    status = ?,
                    success = ?,
                    total_duration = ?,
                    neatlogs_trace_id = ?,
                    entire_checkpoint_id = ?,
                    summary = ?,
                    diff_text = ?,
                    full_report_json = ?,
                    final_state = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE run_id = ?
            """, (
                status,
                1 if success else 0,
                duration,
                neatlogs_trace_id or "",
                entire_checkpoint_id or "",
                summary or "",
                diff_text or "",
                full_report_json or "{}",
                "VERIFIED" if success else "FAILED",
                run_id
            ))
            conn.commit()

    def get_run(self, run_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            if tenant_id is None:
                cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            else:
                cursor.execute("SELECT * FROM runs WHERE run_id = ? AND tenant_id = ?", (run_id, (tenant_id or "default")[:64]))
            row = cursor.fetchone()
            if not row:
                return None
            run_dict = dict(row)

            # Fetch attempts
            cursor.execute("SELECT * FROM attempts WHERE run_id = ? ORDER BY attempt_number ASC", (run_id,))
            run_dict["attempts"] = [dict(a) for a in cursor.fetchall()]

            # Fetch associated PR if any
            cursor.execute("SELECT * FROM pull_requests WHERE run_id = ? ORDER BY id DESC LIMIT 1", (run_id,))
            pr_row = cursor.fetchone()
            run_dict["pull_request"] = dict(pr_row) if pr_row else None

            return run_dict

    def list_runs(self, limit: int = 50, offset: int = 0, status: Optional[str] = None, query: Optional[str] = None, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM runs WHERE 1=1"
            params: List[Any] = []

            if tenant_id is not None:
                sql += " AND tenant_id = ?"
                params.append((tenant_id or "default")[:64])

            if status:
                sql += " AND status = ?"
                params.append(status)

            if query:
                sql += " AND (issue_title LIKE ? OR repo_name LIKE ? OR issue_id LIKE ?)"
                like_q = f"%{query}%"
                params.extend([like_q, like_q, like_q])

            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, params)
            runs = []
            for r in cursor.fetchall():
                d = dict(r)
                # Check PR
                cursor.execute("SELECT pr_number, pr_url, branch FROM pull_requests WHERE run_id = ? LIMIT 1", (d["run_id"],))
                pr = cursor.fetchone()
                d["pull_request"] = dict(pr) if pr else None
                runs.append(d)
            return runs

    # --------------------------------------------------------------------------
    # Pull Requests Operations
    # --------------------------------------------------------------------------
    def save_pull_request(
        self,
        run_id: str,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        pr_url: str,
        title: str,
        body: str,
        branch: str,
        base_branch: str = "main",
        is_draft: bool = False
    ) -> Dict[str, Any]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pull_requests (
                    run_id, repo_owner, repo_name, pr_number, pr_url,
                    title, body, branch, base_branch, state, is_draft
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """, (
                run_id, repo_owner, repo_name, pr_number, pr_url,
                title, body, branch, base_branch, 1 if is_draft else 0
            ))
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "run_id": run_id,
                "pr_number": pr_number,
                "pr_url": pr_url,
                "branch": branch,
                "title": title
            }

    def list_pull_requests(self, limit: int = 20, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            if tenant_id is None:
                cursor.execute("SELECT * FROM pull_requests ORDER BY created_at DESC LIMIT ?", (limit,))
            else:
                cursor.execute("""
                    SELECT pr.* FROM pull_requests pr
                    JOIN runs r ON r.run_id = pr.run_id
                    WHERE r.tenant_id = ?
                    ORDER BY pr.created_at DESC LIMIT ?
                """, ((tenant_id or "default")[:64], limit))
            return [dict(row) for row in cursor.fetchall()]

    # --------------------------------------------------------------------------
    # Repositories Cache Operations
    # --------------------------------------------------------------------------
    def cache_repositories(self, repos: List[Dict[str, Any]], tenant_id: str = "default"):
        tid = (tenant_id or "default")[:64]
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM repositories WHERE tenant_id = ?", (tid,))
            for r in repos:
                cursor.execute("""
                    INSERT OR REPLACE INTO repositories (
                        tenant_id, owner, name, full_name, default_branch, private, description, open_issues_count, html_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tid,
                    r.get("owner", {}).get("login") if isinstance(r.get("owner"), dict) else r.get("owner", ""),
                    r.get("name", ""),
                    r.get("full_name", ""),
                    r.get("default_branch", "main"),
                    1 if r.get("private") else 0,
                    r.get("description", ""),
                    r.get("open_issues_count", 0),
                    r.get("html_url", "")
                ))
            conn.commit()

    def get_cached_repositories(self, query: Optional[str] = None, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            tid = (tenant_id or "default")[:64] if tenant_id is not None else None
            if query and tid is not None:
                like_q = f"%{query}%"
                cursor.execute("SELECT * FROM repositories WHERE tenant_id = ? AND (full_name LIKE ? OR description LIKE ?) ORDER BY name ASC", (tid, like_q, like_q))
            elif query:
                like_q = f"%{query}%"
                cursor.execute("SELECT * FROM repositories WHERE full_name LIKE ? OR description LIKE ? ORDER BY name ASC", (like_q, like_q))
            elif tid is not None:
                cursor.execute("SELECT * FROM repositories WHERE tenant_id = ? ORDER BY name ASC", (tid,))
            else:
                cursor.execute("SELECT * FROM repositories ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = PatchPilotDB()
