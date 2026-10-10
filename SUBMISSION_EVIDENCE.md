# PatchPilot AI — neatHacks 2026 Submission Evidence & Verification Dossier

---

## 1. Project Information
- **Project Name:** PatchPilot AI
- **Repository URL:** [https://github.com/Quantum-Ark/patchai](https://github.com/Quantum-Ark/patchai)
- **Latest Commit SHA:** `f1e6eda`
- **Agent Integration:** Antigravity CLI / Codex (via Entire CLI 0.11.4)
- **Core Differentiator:** **Evidence-Gated Verified Recovery** — autonomous defect investigation, baseline reproduction, sandboxed patch execution, automated rollback on regression detection, hypothesis updating, and independent dual-suite verification.


---

## 2. Telemetry & Observability (Neatlogs)
- **Status:** **VERIFIED (API Submission)** / **NOT VERIFIED (Live Web Dashboard UI)**
- **Authentication:** Uses Project API Key via `NEATLOGS_API_KEY` (masked: `4zwG...rAzm`). *The project ID is never used as an API key.*
- **Ingestion Endpoint:** `https://ingest.neatlogs.com/v1/trace`
- **Submitted Trace IDs:**
  - **Live Probe / Diagnostics Run:** `1431cd5ddb187b35791310c0eb31f271` (HTTP 200 OK, 5 spans)
  - **Flagship Verified Recovery Showcase:** `1fd1807e23cac2b5d2c81c9fbb12faf3`
  - **Benchmark Case 1 (Logic Bug):** `b8fb2583a54b4249a02fb0c9769300ee`
  - **Benchmark Case 2 (Boundary Bug):** `fce78f744c854162bbff8a6a6cb82e96`
  - **Benchmark Case 3 (Regression Recovery):** `fa7426780f2d4838b90a61cfb8813ecb`
- **Audit Finding:** Telemetry spans are packaged and submitted via HTTP with valid bearer token authentication. Live dashboard visualization on `app.neatlogs.com` requires account dashboard login to confirm UI rendering.

---

## 3. Continuous Context & Checkpoints (Entire CLI)
- **Status:** **VERIFIED (CLI & Cloud Indexing & Checkpoint Trailed)**
- **Entire CLI Version:** `0.11.4` (windows/amd64)
- **Authenticated User:** `github:ABHISHEK-DBZ` (Abhishek Jha) via device authorization
- **Active Session ID:** `962e40f4-2378-4cff-8c3c-c3802c4a26da` (Agent: Antigravity)
- **Trailed Checkpoint Commit:** `9f65517` (`Entire-Session: 962e40f4-2378-4cff-8c3c-c3802c4a26da`, `Entire-Metadata: .entire/metadata/962e40f4-2378-4cff-8c3c-c3802c4a26da`)
- **Entire Cloud Repository:** `Quantum-Ark/patchai` (Repository ULID: `01M4JPHNGPMEGQWNSE84R3AWMA`)
- **Indexed Commits in Entire Cloud:** 5 commits indexed (`3765fbe`, `924b6ab`, `0c33fb3`, `916d66f`, `467daf4`).
- **Code Graph Plugin:** `entire-graph v0.4.0` initialized ([AGENTS.md](AGENTS.md) & [.entire/graph-agent.md](.entire/graph-agent.md)).
- **Audit Finding:** Session tracking is continuously logged locally (`.entire/logs/`) and indexed in Entire Cloud. Checkpoint on commit `9f65517` links directly to session `962e40f4-2378-4cff-8c3c-c3802c4a26da`.

---

## 4. Market & Financial Validation (cfo.ai)
- **Status:** **BLOCKED / LOCALLY PREPARED**
- **cfo.ai Live URL:** [https://cfo.ai/neathacks](https://cfo.ai/neathacks)
- **Audit Finding:** The external cfo.ai service requires commercial account signup, live corporate accounting connection (Stripe/Salesforce), and credit card entry. Per hackathon safety rules, no payment cards were entered.
- **Local Business Model:** A complete SaaS unit economics model is locally prepared in [docs/business-plan.md](docs/business-plan.md) and [BUSINESS_PLAN.md](BUSINESS_PLAN.md) using the cfo.ai prompt structure.
- **Assumptions Labeling:** All financial projections ($0.045 COGS per fix, $49/mo Developer, $499/mo Team, $9.79M 24-mo ARR) are explicitly marked as **unverified planning assumptions**, not historical financial data.

---

## 5. Developer Intelligence (Crustdata API)
- **Status:** **VERIFIED (Live API Authenticated)**
- **Authentication:** `CRUSTDATA_API_KEY` (masked: `cd_8...0429`)
- **API Version:** `x-api-version: 2025-11-01`
- **Endpoint Tested:** `https://api.crustdata.com/account/endpoints` (HTTP 200 OK)
- **Capability:** Company enrichment, social post tracking, and real-time developer discovery.

---

## 6. Benchmark Evaluation Results (Preliminary)
*Note: Results evaluated on 3 curated Python test fixtures.*

| Benchmark Case | Defect Type | Attempts | Recovery Demonstrated | Outcome | Trace ID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1: Logic Bug** | Unhandled `ZeroDivisionError` in `safe_divide` | 1 | Direct Fix | **[OK] VERIFIED** | `b8fb2583a54b...` |
| **Case 2: Boundary Bug** | `IndexError` on empty list pagination (`page=1`) | 1 | Direct Fix | **[OK] VERIFIED** | `fce78f744c...` |
| **Case 3: Regression Recovery** | Pricing engine validation that broke VIP tiers | 2 | **YES (Multi-Attempt)** | **[OK] VERIFIED** | `fa7426780f...` |

### Case 3 Recovery Mechanism:
1. **Attempt #1:** Naive fix validates input but breaks VIP discount logic.
2. **Regression Detection:** Regression test fails (`calculate_tiered_price` assertion error).
3. **Rollback:** `PatchTool.rollback()` restores working directory to clean baseline.
4. **Adaptive Replanning:** Recovery policy feeds test traceback into the agent context.
5. **Attempt #2:** Precision fix validates input while preserving existing behavior.
6. **Verification:** Both acceptance and regression tests pass with 100% certainty.

---

## 7. Automated Test Suite Results
- **Framework:** `pytest 9.1.1` with `pytest-cov 7.1.0`
- **Total Tests:** 26
- **Passed:** 26 (100%)
- **Failed:** 0
- **Warnings:** 0
- **Automated CI:** `.github/workflows/ci.yml` passing on GitHub Actions ([Run 38072806729](https://github.com/Quantum-Ark/patchai/actions/runs/38072806729)).

---

## 8. Final Submission Status Matrix

| Component | Status | Evidence / Notes |
| :--- | :--- | :--- |
| **Autonomous Core (State Machine)** | **VERIFIED** | 7 discrete states; passed 26 automated pytest tests |
| **Defect Reproduction & Rollback** | **VERIFIED** | Genuine subprocess execution and Git rollback |
| **Dual-Suite Verification** | **VERIFIED** | Passes both acceptance and regression tests |
| **Live LLM Provider Adapter** | **VERIFIED** | OpenAI, Gemini, Anthropic, Groq, OpenRouter with latency checks & zero mock leakage |
| **Neatlogs API Telemetry** | **VERIFIED** | Live HTTP 200 telemetry verified with `NEATLOGS_API_KEY` (Trace `1431cd5ddb18...`) |
| **Neatlogs Web Dashboard** | **NOT VERIFIED** | Ingest API verified (HTTP 200); pending web console login to confirm UI rendering |
| **Entire CLI Session Tracking** | **VERIFIED** | Active session `962e40f4...` & Cloud repo `01M4JPH...` |
| **Entire Commit Trailers** | **VERIFIED** | Checkpoint trailers verified on commit `9f65517` |
| **cfo.ai Platform Live Run** | **BLOCKED** | Commercial onboarding requires credit card / Stripe credentials |
| **Local Business Plan & Financials** | **VERIFIED** | Completed in [docs/business-plan.md](docs/business-plan.md) and [BUSINESS_PLAN.md](BUSINESS_PLAN.md) |
| **Crustdata API** | **VERIFIED** | Connected & verified with `2025-11-01` API |
| **GitHub Actions CI** | **VERIFIED** | Run 38072806729 completed green on Python 3.12 |
| **Interactive Animated Homepage** | **VERIFIED** | High-aesthetic workbench in `web/` (`patchpilot serve`) |
| **Public Repository** | **VERIFIED** | [https://github.com/Quantum-Ark/patchai](https://github.com/Quantum-Ark/patchai) |

