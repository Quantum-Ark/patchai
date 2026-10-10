"""
Controlled Patch Application & Rollback Tool.
Generates unified diffs, creates automated backups before mutations, and supports instant rollback on failed attempts.
"""

import difflib
from pathlib import Path
from typing import Tuple, Optional


class PatchTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir.resolve()
        self.backup_store: dict[str, str] = {}

    def apply_replacement(
        self,
        rel_path: str,
        original_snippet: str,
        patched_snippet: str
    ) -> Tuple[bool, str, str]:
        """
        Applies a code replacement to a target file.
        Returns: (success: bool, unified_diff: str, error_message: str)
        """
        target_file = (self.repo_dir / rel_path).resolve()
        if not target_file.is_relative_to(self.repo_dir):
            return False, "", f"Path traversal error: {rel_path} outside repo root"
        if not target_file.exists():
            return False, "", f"Target file does not exist: {rel_path}"

        current_content = target_file.read_text(encoding="utf-8")

        # Save backup in memory for rollback
        if rel_path not in self.backup_store:
            self.backup_store[rel_path] = current_content

        if original_snippet not in current_content:
            return False, "", f"Original snippet not found in {rel_path}."

        new_content = current_content.replace(original_snippet, patched_snippet, 1)

        # Compute unified diff
        current_lines = current_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff_lines = list(difflib.unified_diff(
            current_lines,
            new_lines,
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}"
        ))
        unified_diff = "".join(diff_lines)

        # Write patched content to file
        target_file.write_text(new_content, encoding="utf-8")
        return True, unified_diff, ""

    def rollback(self, rel_path: str) -> bool:
        """Roll back a modified file to its initial state."""
        if rel_path not in self.backup_store:
            return False

        target_file = (self.repo_dir / rel_path).resolve()
        target_file.write_text(self.backup_store[rel_path], encoding="utf-8")
        return True

    def rollback_all(self):
        """Roll back all modified files in this run."""
        for rel_path, original_content in self.backup_store.items():
            target_file = (self.repo_dir / rel_path).resolve()
            target_file.write_text(original_content, encoding="utf-8")
        self.backup_store.clear()
