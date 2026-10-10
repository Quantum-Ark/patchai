# PatchPilot AI — Business Plan & Unit Economics
*neatHacks 2026 Submission Document*

---

## 1. Value Proposition & Customer Pain

Software engineering teams spend **25% to 40% of their total engineering hours** triaging, debugging, and patching software defects. Current LLM coding tools generate patches that hallucinate and introduce regressions into production.

**PatchPilot AI delivers verified autonomous fixes**:
- Reproduces defects against automated tests before touching code.
- Automatically rolls back any patch that breaks an existing test.
- Delivers PR-ready diffs accompanied by cryptographic Entire checkpoints and live Neatlogs execution traces.

---

## 2. Pricing Tiers

```
+---------------------------------------------------------------------------------------+
| Plan           | Price / Month | Verified Fixes | Repositories | Enterprise Features  |
+----------------+---------------+----------------+--------------+----------------------+
| Developer Free | $0            | 5 fixes / mo   | 1 public     | Standard LLM         |
| Pro Individual | $49           | 50 fixes / mo  | 3 private    | Priority Models      |
| Team           | $499          | 500 fixes / mo | Unlimited    | Neatlogs & Entire CI |
| Enterprise     | Custom Quote  | Unlimited      | Multi-org    | On-prem & VPC Docker |
+---------------------------------------------------------------------------------------+
```

---

## 3. Unit Economics per Verified Fix

- **Average Tokens per Fix Run (1.6 attempts average):** 7,500 tokens
- **Inference Cost (OpenAI / Claude API):** $0.038
- **Compute (Sandboxed Test Runner):** $0.005
- **Observability (Neatlogs HTTP Injection):** $0.002
- **Total Cost of Goods Sold (COGS):** **$0.045 per fix**
- **Average Revenue per Fix (Team Tier):** **$1.00**
- **Gross Margin:** **95.5%**

---

## 4. 24-Month Financial Forecast

| Metric | Month 3 (Beta) | Month 6 (GA) | Month 12 | Month 18 | Month 24 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Paid Accounts** | 15 | 60 | 250 | 700 | 1,600 |
| **Monthly Revenue (MRR)** | $1,800 | $16,800 | $95,000 | $308,000 | $816,000 |
| **Annualized Run Rate (ARR)**| $21,600 | $201,600 | **$1.14M** | **$3.69M** | **$9.79M** |
| **Gross Margin %** | 90.0% | 91.0% | 91.0% | 91.2% | 91.2% |
| **Net Cash Flow** | -$10,380 | -$6,700 | +$31,500 | +$141,000 | +$434,000 |

*Cash Flow Break-Even achieved by Month 9 on initial angel buffer of $250,000.*

---

## 5. cfo.ai Integration Note
- Platform evaluated at `https://cfo.ai/neathacks`.
- Direct card billing setup withheld during automated run to safeguard live financial credentials.
- Financial unit economics, CAC/LTV models, and pricing tiers synthesized above following Ari/cfo.ai model specifications.
