# PatchPilot AI — 3-Minute Hackathon Demo Script
*neatHacks 2026 Official Video & Pitch Walkthrough*

**Target Video Duration:** 2 minutes 50 seconds (Target < 3:00)

---

### [0:00 – 0:30] Hook & Problem Statement
- **Visual:** Screen opens on a terminal showing a failed PR that broke production.
- **Audio / Speaker:**
  > "Hi everyone, I'm presenting **PatchPilot AI** for neatHacks 2026.
  > Today's generative AI coding tools can write code fast—but they suffer from a dangerous flaw: **unverified hallucinations**. In fact, over 90% of AI-generated bug fixes fail because they either miss the root cause or silently introduce regressions that break other parts of the system.
  > 
  > Merely generating a patch isn't enough. What developers actually need is **proof**."

---

### [0:30 – 1:05] The Solution: Verified Recovery
- **Visual:** Switch to architecture diagram (state machine & pipeline in README).
- **Audio / Speaker:**
  > "Meet **PatchPilot AI**—an autonomous GitHub issue-to-verified-fix agent whose core differentiator is **Verified Recovery**.
  > 
  > PatchPilot doesn't assume its first fix works. It operates as a deterministic state machine:
  > 1. It ingests an issue and **reproduces the failure** on a clean baseline.
  > 2. It formulates an investigation hypothesis and applies a sandboxed patch.
  > 3. It runs isolated test suites. If an attempt breaks existing tests—introducing a regression—it **instantly rolls back** the code, classifies the failure, pivots its strategy, and tries again.
  > 4. Finally, it independently verifies the fix across both acceptance and regression suites before generating a PR-ready report."

---

### [1:05 – 2:15] Live Demonstration: Genuine Recovery in Action
- **Visual:** Terminal window running `python demo_recovery.py`.
- **Audio / Speaker:**
  > "Let's see this in action on a real pricing engine with tiered VIP discounts.
  > 
  > An issue was filed: `calculate_tiered_price` allows negative and zero quantities.
  > 
  > Notice what happens:
  > - **Step 1:** PatchPilot runs the baseline test and confirms the bug exists.
  > - **Step 2 (Attempt 1):** The agent generates an initial naive patch that validates quantity, but inadvertently strips the VIP tier calculation.
  > - **Step 3 (Detection):** PatchPilot runs the regression test suite. It immediately detects that existing gold and silver tier tests broke!
  > - **Step 4 (Automated Recovery):** Instead of hallucinating success, PatchPilot classifies this as `REGRESSION_INTRODUCED`, cleanly rolls back `pricing.py`, and logs the pivot in its recovery policy.
  > - **Step 5 (Attempt 2):** It refines its strategy, preserves the tier multipliers, and injects the quantity guard.
  > - **Step 6 (Verification):** Both the reproduction test and the entire regression suite pass with zero side-effects. The state transitions to **VERIFIED**!"

---

### [2:15 – 2:45] Observability & Governance: Neatlogs & Entire
- **Visual:** Show exported Markdown report with Neatlogs Trace ID and Entire CLI checkpoints.
- **Audio / Speaker:**
  > "Every decision PatchPilot makes is transparent and tamper-evident:
  > - **Neatlogs Observability:** Every workflow stage—from issue intake to rollback decisions—is streamed live to Neatlogs with granular spans, token tracking, and duration metrics.
  > - **Entire Continuous Memory:** Every code change is versioned with Entire checkpoints and local code graphs, linking human commits directly to the agent's reasoning.
  > - **Safe Governance:** PatchPilot exports audit-ready reports and patch diffs. It *never* pushes or merges code automatically without human approval."

---

### [2:45 – 3:00] Conclusion & Wrap-up
- **Visual:** Terminal showing `pytest` suite passing 100% (18/18 tests, 0 warnings).
- **Audio / Speaker:**
  > "With 100% automated test coverage, proven multi-attempt recovery benchmarks, and full Neatlogs tracing, PatchPilot AI turns raw LLM code into trusted, verified engineering fixes.
  > 
  > Thank you!"
