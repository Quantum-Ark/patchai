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
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.\-]+)/(?P<repo>[A-Za-z0-9_.\-]+)/issues/(?P<number>\d+)(?:[/?#].*)?$"
)

_BRANCH_NAME_RE = re.compile(r"^(?!-)[A-Za-z0-9/_.\-]{1,128}$")

_OWNER_REPO_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


def _validate_branch_name(branch: str) -> None:
    if not branch or not _BRANCH_NAME_RE.match(branch):
        raise ValueError(
            f"Invalid branch name: {branch!r}. Must match [A-Za-z0-9/_.-]{{1,128}}, not start with '-'."
        )
    if ".." in branch or "//" in branch or branch.endswith("/") or branch.endswith(".lock"):
        raise ValueError(f"Invalid branch name: {branch!r}.")


def _validate_owner_repo(value: str, label: str) -> None:
    if not value or len(value) > 100 or not _OWNER_REPO_RE.match(value):
        raise ValueError(f"Invalid {label}: {value!r}.")

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
        m = _ISSUE_URL_RE.match((url or "").strip())
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
        token: Optional[str] = None,
        draft: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a Pull Request via GitHub REST API or generate pre-filled compare link."""
        import os
        import requests
        import urllib.parse

        _validate_owner_repo(repo_owner, "repo owner")
        _validate_owner_repo(repo_name, "repo name")
        _validate_branch_name(head_branch)
        _validate_branch_name(base_branch)
        if not title or len(title) > 300:
            raise ValueError("PR title must be 1..300 characters.")
        if len(body or "") > 20000:
            raise ValueError("PR body too long (max 20000 characters).")

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

        # Check if an open PR already exists for this branch to prevent duplicate PR errors
        existing = GitHubPRTool.find_existing_pr(repo_owner, repo_name, head_branch, token=auth_token)
        if existing:
            return {
                "success": True,
                "mode": "api_existing",
                "pr_number": existing.get("number"),
                "pr_url": existing.get("html_url"),
                "state": existing.get("state"),
                "branch": head_branch,
                "title": existing.get("title", title),
                "body": existing.get("body", body),
                "is_existing": True,
                "message": f"Found existing open Pull Request #{existing.get('number')}"
            }

        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
            "draft": bool(kwargs.get("draft", False))
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
                    "is_draft": bool(kwargs.get("draft", False)),
                }
            else:
                err_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = err_data.get("message", f"HTTP {resp.status_code}")
                # If error is that a PR already exists, try to find it
                if "A pull request already exists" in err_msg:
                    dup = GitHubPRTool.find_existing_pr(repo_owner, repo_name, head_branch, token=auth_token)
                    if dup:
                        return {
                            "success": True,
                            "mode": "api_existing",
                            "pr_number": dup.get("number"),
                            "pr_url": dup.get("html_url"),
                            "state": dup.get("state"),
                            "branch": head_branch,
                            "title": dup.get("title", title),
                            "body": dup.get("body", body),
                            "is_existing": True,
                        }

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

    @staticmethod
    def find_existing_pr(
        repo_owner: str,
        repo_name: str,
        head_branch: str,
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Check if an open PR already exists for head_branch."""
        import os
        import requests
        auth_token = token or os.getenv("GITHUB_TOKEN", "")
        if not auth_token:
            return None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {auth_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        # Head parameter can be either branch or owner:branch
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=open&head={repo_owner}:{head_branch}"
        try:
            resp = requests.get(api_url, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                prs = resp.json()
                if prs and len(prs) > 0:
                    return prs[0]
            # Try simple head without owner prefix
            api_url2 = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=open&head={head_branch}"
            resp2 = requests.get(api_url2, headers=headers, timeout=10.0)
            if resp2.status_code == 200:
                prs2 = resp2.json()
                if prs2 and len(prs2) > 0:
                    return prs2[0]
        except Exception:
            pass
        return None

    @staticmethod
    def get_user_repos(token: str) -> List[Dict[str, Any]]:
        """Fetch accessible repositories for the authenticated user."""
        import requests
        if not token:
            return []
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        url = "https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member"
        try:
            resp = requests.get(url, headers=headers, timeout=15.0)
            if resp.status_code == 200:
                items = resp.json()
                result = []
                for it in items:
                    result.append({
                        "id": it.get("id"),
                        "name": it.get("name"),
                        "full_name": it.get("full_name"),
                        "owner": it.get("owner", {}).get("login", ""),
                        "owner_avatar": it.get("owner", {}).get("avatar_url", ""),
                        "private": bool(it.get("private")),
                        "html_url": it.get("html_url"),
                        "description": it.get("description") or "",
                        "default_branch": it.get("default_branch", "main"),
                        "open_issues_count": it.get("open_issues_count", 0),
                        "updated_at": it.get("updated_at"),
                    })
                return result
            return []
        except Exception:
            return []

    @staticmethod
    def get_repo_issues(repo_owner: str, repo_name: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch open issues for a repository."""
        import os
        import requests
        _validate_owner_repo(repo_owner, "repo owner")
        _validate_owner_repo(repo_name, "repo name")
        auth_token = token or os.getenv("GITHUB_TOKEN", "")
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=open&per_page=30&sort=updated"
        try:
            resp = requests.get(url, headers=headers, timeout=15.0)
            if resp.status_code == 200:
                issues = resp.json()
                result = []
                for it in issues:
                    # Ignore PRs returned in issues endpoint
                    if "pull_request" in it:
                        continue
                    result.append({
                        "id": str(it.get("number")),
                        "number": it.get("number"),
                        "title": it.get("title"),
                        "body": it.get("body") or "",
                        "html_url": it.get("html_url"),
                        "comments_count": it.get("comments", 0),
                        "labels": [l.get("name") for l in it.get("labels", []) if isinstance(l, dict)],
                        "created_at": it.get("created_at"),
                        "user": it.get("user", {}).get("login", "")
                    })
                return result
            return []
        except Exception:
            return []

    @staticmethod
    def push_branch_to_github(
        repo_dir: Path,
        head_branch: str,
        repo_owner: str,
        repo_name: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates branch and pushes to remote GitHub repository using token authentication."""
        import subprocess
        import os
        _validate_branch_name(head_branch)
        _validate_owner_repo(repo_owner, "repo owner")
        _validate_owner_repo(repo_name, "repo name")
        auth_token = token or os.getenv("GITHUB_TOKEN", "")
        try:
            # 1. Create local branch (-- guards against option injection)
            subprocess.run(
                ["git", "-c", "core.hooksPath=", "checkout", "-B", "--", head_branch],
                cwd=str(repo_dir),
                check=False,
                capture_output=True,
                text=True
            )
            # 2. Stage changes
            subprocess.run(
                ["git", "-c", "core.hooksPath=", "add", "-A"],
                cwd=str(repo_dir),
                check=False,
                capture_output=True,
                text=True
            )
            # 3. Commit
            subprocess.run(
                ["git", "-c", "core.hooksPath=", "commit", "-m", f"fix: autonomous repair by PatchPilot AI for {head_branch}"],
                cwd=str(repo_dir),
                check=False,
                capture_output=True,
                text=True
            )

            # 4. If token provided, push with authenticated remote
            if auth_token:
                remote_target = f"https://x-access-token:{auth_token}@github.com/{repo_owner}/{repo_name}.git"
                push_res = subprocess.run(
                    ["git", "-c", "core.hooksPath=", "push", "--", remote_target, f"{head_branch}:{head_branch}", "--force"],
                    cwd=str(repo_dir),
                    check=False,
                    capture_output=True,
                    text=True
                )
                if push_res.returncode == 0:
                    return {"success": True, "branch": head_branch, "pushed": True}
                else:
                    err = push_res.stderr.replace(auth_token, "***")
                    return {"success": False, "error": f"Git push failed: {err}", "pushed": False}
            return {"success": True, "branch": head_branch, "pushed": False, "message": "Committed locally; token required to push to remote."}
        except Exception as e:
            return {"success": False, "error": str(e), "pushed": False}



