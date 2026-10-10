# PatchPilot AI — 3-Minute Hackathon Demo Script
*neatHacks 2026 Submission Presentation*

**Duration:** 2 minutes 50 seconds

---

### Part 1: Problem & The Blind Patch Trap [0:00 – 0:30]
- **Visual:** Terminal showing an AI-generated patch that broke a production checkout.
- **Narrator:**
  > "Every engineer has seen this: an AI coding tool generates a patch that looks great, but silently introduces a regression into production. Generative models don't know if their code actually works unless they test it.
  > What software teams need isn't more code generation—it's **Verified Recovery**."

---

### Part 2: How PatchPilot AI Works [0:30 – 1:05]
- **Visual:** Architecture state machine diagram.
- **Narrator:**
  > "PatchPilot AI is an autonomous issue-to-verified-fix agent.
  > Instead of blindly opening PRs:
  > 1. It confirms the defect with a baseline test first.
  > 2. It tests every patch in isolation.
  > 3. If a patch introduces a regression, PatchPilot **instantly rolls back**, analyzes the failure, pivots its strategy, and tries again.
  > 4. Only when both reproduction tests and the existing test suite pass 100% clean does PatchPilot generate a PR draft."

---

### Part 3: Live Showcase: Genuine Recovery [1:05 – 2:15]
- **Visual:** Terminal running `python demo_recovery.py`.
- **Narrator:**
  > "Watch this live on a tiered pricing engine.
  > - **The Defect:** Missing validation for negative quantities.
  > - **Attempt 1:** The agent creates a patch that fixes negative quantities, but accidentally breaks the VIP gold and silver discount calculations!
  > - **The Detection:** PatchPilot executes the regression suite. The regression test fails.
  > - **The Recovery:** PatchPilot catches the regression, rolls back `pricing.py` to its clean baseline, and pivots its strategy.
  > - **Attempt 2:** It protects the tier multipliers and injects the quantity guard.
  > - **Verification:** Both the acceptance test and the entire regression suite pass. The state transitions to **VERIFIED**!"

---

### Part 4: Neatlogs & Entire Governance [2:15 – 2:50]
- **Visual:** Markdown report showing Neatlogs Trace ID (`1fd1807e...`) and Entire CLI status.
- **Narrator:**
  > "Every step is traced live to Neatlogs with granular spans and execution metrics, and checkpointed with Entire continuous memory.
  > PatchPilot never auto-merges: it provides verified proof for senior developers to review with confidence.
  > Thank you!"
