"""
GitHub Issue Intake Tool.
Parses local issue files or fetches issues from GitHub repositories.
Extracts reproduction steps, stack traces, and candidate file hints.
"""

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from patchpilot.models import Issue


class GitHubIssueTool:
    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> Issue:
        """Create an Issue from a dictionary payload."""
        file_hints = data.get("file_hints", [])
        body = data.get("body", "")

        # Auto-extract file hints from issue body if not explicitly provided
        if not file_hints and body:
            matches = re.findall(r'[\w/\\]+\.(?:py|js|ts|json|go|md)', body)
            file_hints = list(set(matches))

        return Issue(
            id=str(data.get("id", "issue-001")),
            title=data.get("title", "Untitled Issue"),
            body=body,
            repo_url=data.get("repo_url"),
            file_hints=file_hints,
            reproduction_command=data.get("reproduction_command")
        )

    @staticmethod
    def load_from_file(file_path: Path) -> Issue:
        """Load an issue from a JSON or Markdown file."""
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix.lower() == ".json":
            data = json.loads(content)
            return GitHubIssueTool.load_from_dict(data)

        # Markdown issue format
        lines = content.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else "Markdown Issue"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Extract code blocks or reproduction command if annotated
        cmd_match = re.search(r'```(?:bash|sh|powershell)?\s*(pytest[^\n`]+)\s*```', body)
        reproduction_cmd = cmd_match.group(1).strip() if cmd_match else None

        return GitHubIssueTool.load_from_dict({
            "id": file_path.stem,
            "title": title,
            "body": body,
            "reproduction_command": reproduction_cmd
        })
