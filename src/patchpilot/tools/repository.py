"""
Repository Tool.
Discovers relevant source files, safely reads code context, and validates repository structure.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional


class RepositoryTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir.resolve()

    def discover_files(self, extensions: List[str] = [".py"]) -> List[Path]:
        """Scan repository for source files, ignoring caches and venvs."""
        ignore_dirs = {
            ".git", ".venv", "venv", "ENV", "__pycache__", ".pytest_cache",
            "build", "dist", "node_modules", ".tox", ".mypy_cache",
            ".patchpilot_backups", "artifacts", "htmlcov",
        }
        results = []
        seen = set()
        for p in self.repo_dir.rglob("*"):
            try:
                if p.is_symlink():
                    continue
                if not p.is_file():
                    continue
            except OSError:
                continue
            if p.suffix in extensions:
                if any(part in ignore_dirs for part in p.parts):
                    continue
                if p.name.startswith(".coverage"):
                    continue
                try:
                    rp = p.resolve()
                except OSError:
                    continue
                if rp in seen:
                    continue
                seen.add(rp)
                results.append(p)
        return sorted(results)

    def read_file_safe(self, rel_path: str) -> str:
        """Safely read file content within repository bounds."""
        target = (self.repo_dir / rel_path).resolve()
        if not target.is_relative_to(self.repo_dir):
            raise ValueError(f"Path traversal detected: {rel_path} escapes repository root.")
        if not target.exists():
            raise FileNotFoundError(f"File not found: {rel_path}")
        return target.read_text(encoding="utf-8")

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbol or string across repository files."""
        matches = []
        for file_path in self.discover_files():
            try:
                content = file_path.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    rel_path = file_path.relative_to(self.repo_dir)
                    matches.append({
                        "file": str(rel_path),
                        "snippet": content[:300]
                    })
            except Exception:
                continue
        return matches
