# PatchPilot AI — Security Architecture & Threat Model
*neatHacks 2026 Security Dossier*

---

## 1. Threat Model & Boundaries

PatchPilot AI executes in environments handling untrusted software repositories, public issue reports, and user-submitted code. The system enforces strict defense-in-depth principles:

### 1.1 Untrusted Content Handling
- **Prompt Injection Defense:** Issue descriptions, comments, and file contents are treated as untrusted data inputs. They are framed inside strict JSON schemas and system prompts with non-override instructions.
- **Path Traversal Guards:** All target file operations verify `.is_relative_to(repo_root)`. Any patch attempting to write outside the target repository is rejected immediately.
- **Diff Inspection:** Changes are calculated via standard unified diffs (`difflib.unified_diff`) with in-memory backups. Binary files and unexpected executable attributes are rejected.

### 1.2 Execution Sandbox
- **Timeout Caps:** Subprocess executions enforce hard timeouts (default `execution_timeout_seconds=60`) to prevent infinite loops, fork-bombs, and resource denial-of-service.
- **Credential Isolation:** Host API keys, tokens, and private SSH keys are never mounted into test execution subprocesses.
- **Zero Auto-Merge:** The agent **never automatically merges pull requests or pushes commits to production**. All generated diffs are presented as human-reviewable artifacts.

### 1.3 Telemetry & Data Hygiene
- **Secret Redaction:** Traces emitted to Neatlogs contain metadata (run ID, attempt count, test duration, status) and redact all environment secrets, `.env` values, and raw API tokens.
- **Git Hygiene:** Local databases (`*.db`), `.env` files, and virtual environments (`.venv/`) are strictly ignored via `.gitignore`.
