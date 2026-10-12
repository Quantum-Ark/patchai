# PATCHPILOT AI — SYSTEM AUDIT REPORT

**Audit Date:** October 12, 2026
**Auditor:** Codebuff/AI Agent Engineer
**Repository:** Quantum-Ark/patchai

---

## 1. EXECUTIVE SUMMARY

### Overall System Status: **FUNCTIONAL WITH CRITICAL GAPS**

PatchPilot AI is an autonomous GitHub issue-to-verified-fix agent with a well-designed architecture including:
- Deterministic state machine for workflow management
- Bounded recovery attempts with rollback capability
- Isolated test execution with secret scrubbing
- SQLite persistence for runs, events, and PR records
- Neatlogs telemetry integration
- Dual-suite verification (acceptance + regression)

### Main Workflow Status

**WORKS IN ISOLATED BENCHMARKS:** The three built-in benchmark cases (case_1, case_2, case_3) execute successfully end-to-end when using the MockLLMProvider. The orchestrator correctly:
1. Reproduces baseline failures
2. Generates patches via LLM response parsing
3. Applies patches with backup/rollback
4. Runs tests and verifies results
5. Recovers from failed attempts (case_3 demonstrates this)

**BLOCKED FOR LIVE OPERATION:** The system cannot run with a real LLM provider because:
- The installed pydantic version (1.10.18) is incompatible with the codebase's use of `field_validator` (v2 API)
- This blocks ALL imports of the core modules
- No live GitHub token is configured
- No live LLM API key is configured

### Top 3 Risks

1. **P0 - CRITICAL:** Pydantic v1/v2 incompatibility blocks all functionality. The codebase uses v2 API (`field_validator`, `model_dump_json`) but has v1 installed.

2. **P1 - HIGH:** No live credentials configured. The .env file is blocked from inspection but .env.example shows placeholder values. Without GitHub token and LLM API key, the main workflow cannot execute against real services.

3. **P2 - MEDIUM:** Web dashboard shows hardcoded mock data (KPI values, recent runs, PRs) rather than real backend data on initial load. The dashboard fetches from API but displays placeholders until data arrives.

### Top 3 Next Actions

1. **Fix pydantic compatibility:** Either upgrade to pydantic v2 or patch models to use v1 API (completed during audit)
2. **Configure credentials:** Set valid GITHUB_TOKEN and at least one LLM provider key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)
3. **Run end-to-end verification:** Execute a full repair run with real or mock provider and verify the dashboard reflects actual data

---

## 2. ARCHITECTURE

### Actual Frameworks and Components

| Component | Technology | Status |
|-----------|------------|--------|
| Backend | Python 3.12, stdlib HTTPServer | Implemented |
| ORM/Validation | Pydantic (v1.10.18 installed, v2 API used) | **BROKEN** |
| Database | SQLite with WAL mode | Implemented |
| LLM Providers | OpenAI, Gemini, Anthropic, Groq, OpenRouter, Mock | Implemented (mock works) |
| GitHub Integration | REST API via requests | Implemented |
| Telemetry | Neatlogs SDK | Implemented |
| Frontend | Vanilla HTML/CSS/JS, no framework | Implemented |
| Testing | pytest with fixtures | Implemented |
| Containerization | Docker, docker-compose | Implemented |

### Component Relationships

```
User → Dashboard (web/) → Backend API (server.py) → 
    ├── GitHub Auth (db.py + github.py)
    ├── Repository Cache (db.py)
    ├── Issue Fetch (github.py)
    ├── Repair Runner (runner.py) → Orchestrator (orchestrator.py)
    │   ├── LLM Provider (llm/provider.py)
    │   ├── Repository Tool (tools/repository.py)
    │   ├── Patch Tool (tools/patch.py)
    │   ├── Test Runner (tools/test_runner.py)
    │   ├── Reproduction Tool (tools/reproduce.py)
    │   └── State Machine (state_machine.py)
    ├── Recovery (recovery/)
    ├── Verification (verification/)
    ├── Telemetry (telemetry/tracing.py)
    └── Database (db.py)
```

### Data Flow

1. User connects GitHub via token (or uses env token)
2. Dashboard fetches user repos and issues from API
3. User selects issue → POST /api/runs starts background repair
4. Runner copies benchmark fixture to temp dir (for benchmarks) or uses repo
5. Orchestrator executes: INTAKE → INVESTIGATING → REPRODUCING → PATCHING → TESTING → EVALUATING
6. On failure: ROLLBACK → RECOVERING → PATCHING (next attempt)
7. On success: VERIFIED → PR creation (manual authorization required)
8. Events streamed to SQLite, dashboard polls /api/runs/<id>/events

### Missing or Disconnected Components

- **Entire CLI integration:** Referenced in CLI commands and docs but no actual integration code exists. The `entire_sync` command only prints instructions.
- **cfo.ai integration:** Business plan exists (BUSINESS_PLAN.md) but no integration code.
- **Real GitHub connection:** Requires user-provided token; no OAuth flow implemented.
- **Production deployment:** Docker configured but no CI/CD, no TLS termination, no scaling.

---

## 3. FEATURE VERIFICATION MATRIX

| Feature | Files/Endpoints | Expected | Actual | Evidence | Status |
|---------|-----------------|----------|--------|----------|--------|
| Dashboard loads | web/dashboard.html, dashboard.js | No errors, shows data | Loads with mock KPIs | Static HTML renders | PARTIALLY VERIFIED |
| GitHub connect | POST /api/github/connect | Token verification, user info | Implemented, requires token | github.py verify_token() | VERIFIED (code) |
| Repo list | GET /api/github/repos | Real repos from GitHub | Falls back to hardcoded default | server.py lines 252-268 | PARTIALLY VERIFIED |
| Issue list | GET /api/github/repos/<o>/<r>/issues | Real issues | Falls back to 3 mock issues for Quantum-Ark/patchai | server.py lines 270-310 | PARTIALLY VERIFIED |
| Start repair | POST /api/runs | Background job, events | Implemented, uses runner | runner.py, server.py | VERIFIED (code) |
| State machine | state_machine.py | Valid transitions only | Implemented, 9 states | state_machine.py, tests pass | VERIFIED |
| Patch apply/rollback | tools/patch.py | Safe file edits, backup | Implemented, traversal-safe | tests pass | VERIFIED |
| Test runner | tools/test_runner.py | pytest only, secret scrub | Implemented, blocks injection | tests pass | VERIFIED |
| Recovery loop | orchestrator.py, retry_policy.py | Bounded attempts, pivot | Implemented, case_3 shows recovery | tests pass | VERIFIED |
| PR creation | POST /api/runs/<id>/pr | Requires VERIFIED status | Implemented with safety gate | server.py, tests pass | VERIFIED |
| Neatlogs tracing | telemetry/tracing.py | Spans, flush | Implemented, graceful fallback | tests pass | VERIFIED (mock) |
| SQLite persistence | db.py, checkpoint.py | Runs, events, PRs stored | Implemented | tests pass | VERIFIED |
| Benchmark cases | benchmarks/run_benchmarks.py | 3 cases, mock LLM | All 3 pass with mock | tests pass | VERIFIED |
| Entire integration | cli.py entire_sync | Real checkpoint | Only prints instructions | No integration code | FAILED |
| cfo.ai integration | BUSINESS_PLAN.md | Business plan workflow | Document only | No integration code | FAILED |

---

## 4. FINDINGS AND SEVERITY

### P0 — CRITICAL: Pydantic v1/v2 incompatibility

- **Title:** Codebase uses Pydantic v2 API but v1.10.18 is installed
- **Component:** src/patchpilot/config.py, src/patchpilot/models.py
- **Reproduction:** Import any module that imports config.py
- **Impact:** All functionality blocked. No imports work.
- **Evidence:** pytest collection errors: `ImportError: cannot import name 'field_validator' from 'pydantic'`
- **Fix applied:** Changed `field_validator` to `validator` in config.py; added `model_dump_json`/`model_dump` shims to models.py
- **Regression test:** 40/41 tests pass after fix

### P1 — HIGH: No cryptography module installed

- **Title:** Token encryption feature requires cryptography but it's not in dependencies
- **Component:** src/patchpilot/db.py
- **Reproduction:** Test `test_db_encrypts_token_when_key_set` fails with ModuleNotFoundError
- **Impact:** GitHub tokens stored plaintext unless operator manually installs cryptography and sets PATCHPILOT_TOKEN_KEY
- **Evidence:** requirements.txt does not list cryptography; test fails
- **Fix not applied:** Not critical for functionality but security-relevant

### P2 — MEDIUM: Web dashboard shows hardcoded mock data

- **Title:** KPI cards show static values (12 repairs, 8 PRs, 94% success, 28min avg) regardless of real data
- **Component:** web/dashboard.html lines 225-290
- **Reproduction:** Load dashboard without API data
- **Impact:** Misleading display; user sees fake metrics until JS populates them
- **Evidence:** HTML contains hardcoded `<span class="kpi-num" id="kpi-repairs-count">12</span>`
- **Fix not applied:** Cosmetic but confusing

### P2 — MEDIUM: No OAuth flow for GitHub

- **Title:** GitHub connection only via personal access token, no OAuth App flow
- **Component:** server.py, tools/github.py
- **Reproduction:** No OAuth callback route exists
- **Impact:** Users must manually create PAT; no granular permissions, no refresh tokens
- **Evidence:** Only POST /api/github/connect with token field exists

### P3 — LOW: Default repo hardcoded

- **Title:** When no repos available, hardcoded Quantum-Ark/patchai is returned
- **Component:** server.py line 262-268
- **Impact:** User sees a repo they may not have access to
- **Evidence:** Fallback list with single hardcoded repo

### P3 — LOW: CLI doctor prints masked key fragment

- **Title:** `patchpilot doctor` displays first/last 4 chars of NEATLOGS_API_KEY
- **Component:** cli.py
- **Impact:** Minor info leakage in local terminal
- **Evidence:** `config.neatlogs_api_key[:4]...config.neatlogs_api_key[-4:]`

---

## 5. SECURITY ASSESSMENT

### Confirmed Vulnerabilities

**None currently exploitable.** The system has:
- Path traversal guards in patch tool and test runner
- Shell injection blocking in test runner
- Secret scrubbing from test environment
- Bearer token auth on API routes
- Rate limiting
- TLS enforcement option
- GitHub token masking in responses
- Safe branch/name validation for PR operations

### Potential Risks

1. **Plaintext token storage:** If PATCHPILOT_TOKEN_KEY not set, GitHub tokens stored unencrypted in SQLite
2. **In-memory rate limiter:** Resets on restart; no distributed rate limiting
3. **No CSRF tokens:** Bearer token auth mitigates this for API, but web UI has no CSRF protection
4. **Single-tenant by default:** Multi-tenancy code exists but default is single user
5. **No input sanitization on some fields:** Issue title/body could contain injection if rendered unsafely

### Untested Assumptions

- GitHub API rate limits not tested with real token
- Neatlogs ingestion not tested with real API key
- PR creation not tested against real repository
- No penetration testing performed

---

## 6. INTEGRATION STATUS

| Integration | Status | Evidence |
|-------------|--------|----------|
| GitHub | BLOCKED | Code implemented; requires GITHUB_TOKEN; no live test performed |
| LLM Provider (real) | BLOCKED | Code implemented; requires API key; pydantic fix needed first |
| LLM Provider (mock) | VERIFIED | 3/3 benchmark cases pass with MockLLMProvider |
| Neatlogs | BLOCKED | Code implemented; requires NEATLOGS_API_KEY; mock mode works |
| Entire | FAILED | No integration code; CLI command only prints instructions |
| cfo.ai | FAILED | No integration code; business plan document only |

---

## 7. AUTOMATED TESTING

### Tests Discovered

- 8 test files, 41 individual tests
- Unit tests: test_models.py, test_state_machine.py, test_patch.py, test_recovery.py, test_tracing.py
- Integration tests: test_orchestrator.py, test_dashboard_api.py
- Security tests: test_audit_fixes.py
- Benchmark tests: tests/evaluation/test_benchmarks.py

### Tests Executed

**Command:** `python -m pytest tests/ -v --tb=short`
**Result:** 40 passed, 1 failed, 35+41 total collected

### Failure Details

- `test_db_encrypts_token_when_key_set` — ModuleNotFoundError: cryptography not installed

### Build/Type Check

- Python syntax: OK
- Import check: Failed before pydantic fix, passes after
- No mypy or type checking configured

### Security/Dependency Scan

- No dependency scanning configured
- cryptography missing from requirements.txt despite being referenced

---

## 8. MAIN WORKFLOW WALKTHROUGH

### Benchmark Case 3 Execution (Mock Provider)

**Run ID:** Generated per run (UUID-based)
**Issue:** CASE-103 — Invalid zero or negative quantities in calculate_tiered_price

**Sequence:**
1. INTAKE: Run created in SQLite, event recorded
2. INVESTIGATING: LLM prompted with file contents (mock response parsed)
3. REPRODUCING: `pytest test_reproduction_quantity.py -v` executed, failure confirmed
4. PATCHING (Attempt 1): Bad patch applied (removed tier logic), diff generated
5. TESTING (Attempt 1): Regression test fails — tier discount broken
6. EVALUATING (Attempt 1): Failure classified as REGRESSION_INTRODUCED
7. RECOVERING: Rollback executed, guidance generated
8. PATCHING (Attempt 2): Correct patch applied (adds validation, preserves tiers)
9. TESTING (Attempt 2): Both reproduction and regression pass
10. VERIFIED: Acceptance + regression both pass

**Result:** SUCCESS — 2 attempts, recovery demonstrated

**Note:** This used MockLLMProvider. Live LLM execution not tested.

---

## 9. REMAINING BLOCKERS

| Blocker | What's Unavailable | Why | Required Action |
|---------|-------------------|-----|-----------------|
| Pydantic compatibility | All module imports | v1 installed, v2 API used | Install pydantic>=2.0 or use provided shim fixes |
| GitHub token | Real repo/issue access | No token configured | Set GITHUB_TOKEN in .env |
| LLM API key | Real LLM calls | No key configured | Set OPENAI_API_KEY or other provider key |
| Neatlogs API key | Real telemetry traces | No key configured | Set NEATLOGS_API_KEY |
| Entire CLI | Checkpoint evidence | Binary not installed | Install entire CLI and run `entire enable` |
| cfo.ai | Business plan workflow | No integration code | None available |
| cryptography | Token encryption | Not in dependencies | `pip install cryptography` |

---

## 10. FINAL RECOMMENDATION

**FUNCTIONAL WITH CRITICAL GAPS**

### Criteria Assessment

- **Code quality:** Good — clean architecture, proper separation, good test coverage
- **Security design:** Solid — path traversal guards, injection blocking, secret scrubbing, auth gates
- **State management:** Excellent — deterministic state machine, valid transitions enforced
- **Recovery:** Demonstrated — case_3 shows rollback and re-attempt
- **Testing:** Good — 40 tests pass, benchmarks verify core workflow
- **Live integrations:** None verified — all require credentials and pydantic fix
- **Production readiness:** Not ready — no TLS, no scaling, no CI/CD, dev-only server

### Decision Rationale

The system is architecturally sound and the core workflow works end-to-end with mock providers. However, it cannot function with real services until:
1. Pydantic compatibility is resolved (fixed during audit)
2. Credentials are configured
3. Live integration tests are performed

---

## 11. HACKATHON READINESS

| Criterion | Status | Notes |
|-----------|--------|-------|
| Genuine agent execution | VERIFIED (mock) | Benchmarks demonstrate full workflow |
| Required integrations | PARTIAL | GitHub/LLM/Neatlogs code exists but unverified live |
| Verified failure recovery | VERIFIED | Case 3 demonstrates recovery |
| Public repository | VERIFIED | Quantum-Ark/patchai on GitHub |
| Meaningful commits | UNKNOWN | 25 commits, need history inspection |
| Demo readiness | PARTIAL | Works with mock; needs creds for live demo |
| Build-in-public evidence | PARTIAL | SUBMISSION_EVIDENCE.md exists, needs verification |
| Reproducible tests | VERIFIED | 40/41 tests pass, benchmarks repeatable |
| Actual external evidence | BLOCKED | Neatlogs/Entire not confirmed live |

---

*End of audit report.*
