"""
GitHub Issue Intake Tool.
Parses local issue files or fetches issues from GitHub repositories.
Extracts reproduction steps, stack traces, and candidate file hints.
"""

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from patchpilot.models import Issue

_ISSUE_URL_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)"
)

_FILE_HINT_RE = re.compile(
    r"(?<![\w\-])(?:(?:src|app|lib|pkg|tests?|benchmarks?|examples?|scripts?)/[\w.\-/]*?[\w.\-]+\.(?:py|js|ts|tsx|jsx|json|go|rs|java)(?![\w.\-])|[\w.\-]+\.(?:py|go|rs|java)(?![\w.\-]))"
)

_REPRO_CMD_PATTERNS = [
    re.compile(r"```(?:bash|sh|powershell|console|shell|text|pytest)?\s*((?:pytest|python\s+-m\s+pytest)[^\n`]+?)\s*```", re.IGNORECASE),
    re.compile(r"(?m)^\s*((?:pytest|python\s+-m\s+pytest)\s+[^\n#;|&]+?)\s*$"),
    re.compile(r"\b((?:pytest|python\s+-m\s+pytest)\s+[\w\-./\\:]+\.py[\w\-./\\: ]{0,200})", re.IGNORECASE),
]


def _extract_file_hints(body: str) -> List[str]:
    if not body:
        return []
    seen: List[str] = []
    for m in _FILE_HINT_RE.findall(body):
        hint = m.strip().strip("./")
        if hint and hint not in seen and len(hint) < 200:
            seen.append(hint)
    return seen[:20]


def _extract_repro_command(body: str) -> Optional[str]:
    if not body:
        return None
    for pat in _REPRO_CMD_PATTERNS:
        m = pat.search(body)
        if m:
            cmd = re.sub(r"\s+", " ", m.group(1)).strip()
            # strip trailing prompt artifacts
            cmd = re.split(r"\s(?:&&|\|\||;|\|)\s", cmd)[0].strip()
            if cmd and len(cmd) < 500:
                return cmd
    return None


class GitHubIssueTool:
    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> Issue:
        """Create an Issue from a dictionary payload."""
        file_hints = list(data.get("file_hints", []) or [])
        body = data.get("body", "") or ""

        # Auto-extract file hints from issue body if not explicitly provided
        if not file_hints and body:
            file_hints = _extract_file_hints(body)

        return Issue(
            id=str(data.get("id", "issue-001")),
            title=str(data.get("title", "Untitled Issue")),
            body=body,
            repo_url=data.get("repo_url"),
            file_hints=file_hints,
            reproduction_command=data.get("reproduction_command") or _extract_repro_command(body),
        )

    @staticmethod
    def load_from_file(file_path: Path) -> Issue:
        """Load an issue from a JSON or Markdown file."""
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix.lower() == ".json":
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in issue file {file_path}: {e}") from e
            if not isinstance(data, dict):
                raise ValueError(f"Issue JSON must be an object: {file_path}")
            return GitHubIssueTool.load_from_dict(data)

        # Markdown issue format
        lines = content.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else "Markdown Issue"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        # Extract code blocks or reproduction command if annotated
        reproduction_cmd = _extract_repro_command(body)

        return GitHubIssueTool.load_from_dict({
            "id": file_path.stem,
            "title": title or "Markdown Issue",
            "body": body,
            "reproduction_command": reproduction_cmd,
        })

    @staticmethod
    def parse_issue_url(url: str) -> Tuple[str, str, int]:
        """Parse a GitHub issue URL into (owner, repo, number)."""
        m = _ISSUE_URL_RE.search(url or "")
        if not m:
            raise ValueError(
                f"Invalid GitHub issue URL: {url!r}. "
                "Expected https://github.com/<owner>/<repo>/issues/<number>"
            )
        return m.group("owner"), m.group("repo"), int(m.group("number"))

    @staticmethod
    def load_from_url(url: str, token: Optional[str] = None) -> Issue:
        """Fetch a live GitHub issue via the REST API."""
        import os
        import requests

        owner, repo, number = GitHubIssueTool.parse_issue_url(url)
        auth_token = token or os.getenv("GITHUB_TOKEN", "")
        headers = {"Accept": "application/vnd.github+json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
        try:
            resp = requests.get(api_url, headers=headers, timeout=15.0)
        except Exception as e:
            raise RuntimeError(f"Failed to reach GitHub API: {e}") from e
        if resp.status_code == 404:
            raise ValueError(f"GitHub issue not found: {url}")
        if resp.status_code == 401:
            raise ValueError("GitHub API unauthorized. Set a valid GITHUB_TOKEN.")
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            raise RuntimeError("GitHub API rate limit exceeded. Set GITHUB_TOKEN.")
        if resp.status_code != 200:
            raise RuntimeError(
                f"GitHub API error {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()
        body = data.get("body") or ""
        return GitHubIssueTool.load_from_dict({
            "id": str(data.get("number", number)),
            "title": data.get("title") or f"Issue #{number}",
            "body": body,
            "repo_url": data.get("html_url") or url,
            "reproduction_command": _extract_repro_command(body),
        })


class GitHubPRTool:
    """Tool for verifying GitHub authentication tokens and generating PRs."""

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify GitHub Personal Access Token and return authenticated user details."""
        import requests
        if not token:
            return {"valid": False, "error": "No token provided"}
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            resp = requests.get("https://api.github.com/user", headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "valid": True,
                    "login": data.get("login"),
                    "name": data.get("name") or data.get("login"),
                    "avatar_url": data.get("avatar_url"),
                    "html_url": data.get("html_url"),
                    "public_repos": data.get("public_repos", 0),
                }
            return {"valid": False, "error": resp.json().get("message", f"HTTP {resp.status_code}")}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def create_pull_request(
        repo_owner: str,
        repo_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Pull Request via GitHub REST API or generate pre-filled compare link."""
        import os
        import requests
        import urllib.parse

        auth_token = token or os.getenv("GITHUB_TOKEN", "")
        compare_url = (
            f"https://github.com/{repo_owner}/{repo_name}/compare/{base_branch}...{head_branch}"
            f"?expand=1&title={urllib.parse.quote(title)}&body={urllib.parse.quote(body)}"
        )

        if not auth_token:
            return {
                "success": False,
                "mode": "manual_url",
                "pr_url": compare_url,
                "branch": head_branch,
                "title": title,
                "body": body,
                "message": "Token not provided. Ready to raise PR via pre-filled GitHub compare link."
            }

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {auth_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
        }
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=15.0)
            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "success": True,
                    "mode": "api",
                    "pr_number": data.get("number"),
                    "pr_url": data.get("html_url"),
                    "state": data.get("state"),
                    "branch": head_branch,
                    "title": title,
                    "body": body,
                }
            else:
                err_data = resp.json()
                err_msg = err_data.get("message", f"HTTP {resp.status_code}")
                return {
                    "success": False,
                    "mode": "manual_fallback",
                    "error": err_msg,
                    "pr_url": compare_url,
                    "branch": head_branch,
                    "title": title,
                    "body": body,
                }
        except Exception as e:
            return {
                "success": False,
                "mode": "manual_fallback",
                "error": str(e),
                "pr_url": compare_url,
                "branch": head_branch,
                "title": title,
                "body": body,
            }

