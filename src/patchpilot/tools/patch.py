"""
Controlled Patch Application & Rollback Tool.
Generates unified diffs, creates automated backups before mutations, and supports instant rollback on failed attempts.
Backups are kept in-memory and mirrored to .patchpilot_backups/ for crash safety.
"""

import difflib
import hashlib
from pathlib import Path
from typing import Tuple

MAX_FILE_BYTES = 2_000_000


class PatchTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir.resolve()
        self.backup_store: dict[str, str] = {}
        self.backup_dir = self.repo_dir / ".patchpilot_backups"
        try:
            self.backup_dir.mkdir(exist_ok=True)
        except OSError:
            pass

    def _resolve(self, rel_path: str) -> Path:
        if not rel_path or rel_path.strip() in {"", ".", "/"}:
            raise ValueError("Empty target path.")
        target = (self.repo_dir / rel_path).resolve()
        if not target.is_relative_to(self.repo_dir):
            raise ValueError(f"Path traversal error: {rel_path} outside repo root")
        if target == self.repo_dir:
            raise ValueError("Refusing to patch repository root.")
        return target

    def _read_text_safe(self, target: Path, rel_path: str) -> str:
        try:
            size = target.stat().st_size
        except OSError as e:
            raise FileNotFoundError(f"Target file does not exist: {rel_path}") from e
        if size > MAX_FILE_BYTES:
            raise ValueError(f"Refusing to patch large file ({size} bytes): {rel_path}")
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(f"Refusing to patch non-UTF8/binary file: {rel_path}") from e
        if "\x00" in content:
            raise ValueError(f"Refusing to patch binary file: {rel_path}")
        return content

    def _mirror_backup(self, rel_path: str, content: str) -> None:
        try:
            digest = hashlib.sha256(rel_path.encode()).hexdigest()[:16]
            safe = rel_path.replace("/", "_").replace("\\", "_")[:80]
            (self.backup_dir / f"{digest}_{safe}.bak").write_text(content, encoding="utf-8")
        except OSError:
            pass

    def apply_replacement(
        self,
        rel_path: str,
        original_snippet: str,
        patched_snippet: str,
    ) -> Tuple[bool, str, str]:
        """
        Applies a code replacement to a target file.
        Returns: (success: bool, unified_diff: str, error_message: str)
        """
        try:
            target_file = self._resolve(rel_path)
        except ValueError as e:
            return False, "", str(e)
        if not target_file.exists() or not target_file.is_file():
            return False, "", f"Target file does not exist: {rel_path}"

        if not original_snippet or not original_snippet.strip():
            return False, "", "Original snippet is empty; refusing no-op patch."
        if original_snippet == patched_snippet:
            return False, "", "Original and patched snippets are identical; refusing no-op patch."

        try:
            current_content = self._read_text_safe(target_file, rel_path)
        except (FileNotFoundError, ValueError) as e:
            return False, "", str(e)
        except OSError as e:
            return False, "", f"Cannot read {rel_path}: {e}"

        # Save backup in memory for rollback (first-write-wins per run)
        if rel_path not in self.backup_store:
            self.backup_store[rel_path] = current_content
            self._mirror_backup(rel_path, current_content)

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
            tofile=f"b/{rel_path}",
        ))
        unified_diff = "".join(diff_lines)

        # Write patched content to file
        try:
            target_file.write_text(new_content, encoding="utf-8")
        except OSError as e:
            return False, "", f"Cannot write {rel_path}: {e}"
        return True, unified_diff, ""

    def rollback(self, rel_path: str, *, clear: bool = False) -> bool:
        """Roll back a modified file to its initial state."""
        if rel_path not in self.backup_store:
            return False

        try:
            target_file = self._resolve(rel_path)
        except ValueError:
            return False
        try:
            target_file.write_text(self.backup_store[rel_path], encoding="utf-8")
        except OSError:
            return False
        if clear:
            del self.backup_store[rel_path]
        return True

    def rollback_all(self):
        """Roll back all modified files in this run."""
        for rel_path, original_content in list(self.backup_store.items()):
            try:
                target_file = self._resolve(rel_path)
            except ValueError:
                continue
            try:
                target_file.write_text(original_content, encoding="utf-8")
            except OSError:
                continue
        self.backup_store.clear()

    def discard_backup(self, rel_path: str) -> None:
        """Drop a backup after a verified fix (keeps store small)."""
        self.backup_store.pop(rel_path, None)
