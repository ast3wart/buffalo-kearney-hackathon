# Data decisions: attribution, recovery and evaluation

Status: **RECOMMENDED by Brandon (Sat Nov 14). Asher to confirm or push back in the PR.** Once confirmed, the contract-level rules go into [../build/data-contract.md](../build/data-contract.md) and the accounting ones into [../research/warranty-accounting.md](../research/warranty-accounting.md).

Visual version: [../build/data-map.html](../build/data-map.html) (download and open in a browser). The "Decisions", "Supplier attribution", "Alert to recovery" and "Evaluation gate" sections there show the same rules with real sample rows.

**Where this came from:** an outside review of data map v1. Its main point: monthly supplier shares in `build_supply` can't prove which supplier made one failed part. We agree. Every decision below follows from that, or closes a question the review left open.

## What the demo claims
Afterlife finds a part-and-lot cohort whose claim rate jumped, shows the data behind it, and drafts a supplier brief for a person to review. It does **not** claim that monthly supplier shares make a supplier liable for each individual claim.

## Decisions

| # | Area | Decision (recommended) | Why | Threads |
|---|---|---|---|---|
| D1 | Ingestion | CSV extracts + SAP adapter, no live connectors. `check.py` is a **hard stop**: any failed check blocks the run. | Row-level quarantine (load good rows, hold bad ones) is production work. The adapter tests already cover PO-line IDs, zero padding, decimal commas and price units. | 💲 Spend, shared |
| D2 | Claim → part links | A link is a suggestion with evidence and confidence. **Alerts** use links with confidence ≥ 0.5. **Recovery** uses only links at or above the *recovery threshold*, or confirmed by a person. | Recovery threshold = the lowest confidence that reaches **99% precision** on holdout data. Spend links reach that at 0.8 today; claim links get their own number once `match_claims` is built. | 🛠 Warranty |
| D3 | Supplier attribution | Supplier shares estimate a **cohort's** exposure. A **single claim** is assigned to a supplier only when its product-month used one supplier's lot. Claims from mixed months are labeled **supplier unresolved** and shown with count and cost. | Sample, seal kit, builds Apr–Jun 2026: 58 of 74 claims ($14,664.78) can be tied to Keystone; the 16 UV-600 claims (50/50 Keystone/Bluewater) cannot. Production use needs serial-to-batch records. | 🛠 Warranty (detect, brief), 💲 Spend (build_supply stays as is) |
| D4 | Early warning | An alert triggers an investigation and names no one externally until reviewed. Rule: mature build months only, ≥ 2 baseline months, ratio ≥ 1.5, ≥ 10 claims after the step, Benjamini–Hochberg q < 0.05 across every series tested. Alerts show denominators and q-value. | Already built in detect v1 (PR #4), except maturity, which should also allow for the reporting lag (3 months in service + typical lag). | 🛠 Warranty |
| D5 | Cost | Warranty cost = parts + labor + other cost, counted once. Warranty-repair service purchases only reconcile. Overview lifecycle cost = build cost + spare-part purchases + gross warranty cost. Net warranty cost (gross − settled `recovered_usd`) is shown beside it, not instead of it. | Keeps the double-count rule (21b) and shows recoveries only once they're settled. | 💲 Spend (cost.py, Overview), 🛠 Warranty (claim cost) |
| D6 | Agreement terms | A person reviews **every agreement once** before its terms value any recovery. Amended clauses, missing fields and low-confidence values are flagged for that review. | Stricter than the review suggested (only flagged fields), and still cheap: one agreement per supplier, reused for every claim. Missing Keystone's amendment would overstate recovery (100% → 80%) and the filing window (90 → 45 days). | 🛠 Warranty (extract_terms) |
| D7 | Supplier brief | Always a draft. Keeps four evidence levels apart: observed claims, inferred part links, cohort exposure for the supplier, and claims individually attributable to the supplier. Only the last level can enter a recovery submission. | Stops a persuasive brief from overstating what the data proves. | Shared (brief.py: 🛠 warranty section, 💲 pricing section) |
| D8 | Dates | Time in service counts from build month (demo limitation; production needs the retail sale or registration date). Filing deadlines count from `paid_date` (contract v4). | The review assumed payment dates were missing. They're in v4, so deadlines can be computed now. | 🛠 Warranty |
| D9 | Recovery workflow | Five states: **Alert → Opportunity → Eligible** (computed by the app) **→ Submitted → Settled** (people). Eligible = warranty claim, paid, link ≥ recovery threshold or confirmed, single-supplier lot, agreement reviewed, inside warranty window, before filing deadline. Finance books money outside Afterlife. | Separates "estimated opportunity" from "recoverable claim". Maps onto the existing `recovery_status` (none / submitted / recovered); Opportunity and Eligible are computed, not stored. | 🛠 Warranty, shared (brief, app) |

### Owners named in the brief and workflow
| Step | Owner at a real manufacturer |
|---|---|
| Review an alert before a supplier is named | Supplier quality engineer |
| Review extracted agreement terms | Procurement |
| Negotiate with the supplier | Procurement / category manager |
| Submit the recovery claim | Warranty recovery manager |
| Sign off cost reconciliation, book recoveries | Finance |

## Evaluation gate (demo-ready when every row passes)
Each step is scored separately against the generated answer keys.

| Check | Target | Status (Nov 14) | Thread |
|---|---|---|---|
| Purchase line → part, holdout companies | precision and recall ≥ 97% | ✅ 97.8–100% (PR #5) | 💲 |
| Claim → part, holdout companies | ≥ 99% precision at the recovery threshold; recall reported | ⏳ match_claims not built | 🛠 |
| Alert names the right supplier and first lot | Prairie and Ironridge, 3 seeds each | 🟡 sample passes; generated data waits on generate_claims | 🛠 |
| Negatives stay quiet | Bluewater never flagged; Northwind 0 alerts | 🟡 Bluewater passes on sample; Northwind pending | 🛠 |
| False alerts on clean data | 0 across 300 clean series and 3 seeds per company | 🟡 0 on 300 synthetic series; per company pending | 🛠 |
| Supplier-unresolved share | reported with count and cost | 🟡 sample: 16 of 74 seal-kit claims (22%) | 🛠 |
| Agreement terms, field by field | 100% on the 9 sample agreements, amendments included | ⏳ extract_terms not built | 🛠 |

## Follow-up work these decisions create
| Task | Thread | Files |
|---|---|---|
| Sample generator only marks a claim submitted/recovered when its product-month is single-supplier (today a 50/50 month falls to the first supplier, e.g. WC-2026-00090) | 🛠 | `scripts/make_sample.py`, `generate_claims.py` docstring |
| Split alert exposure into attributable vs supplier unresolved (count and $) | 🛠 | `afterlife/detect.py`, alerts in data contract |
| Maturity allows for reporting lag | 🛠 | `afterlife/detect.py` |
| Eligibility check per claim (D9) and recovery threshold from holdout precision (D2) | 🛠 | `afterlife/brief.py` (or a new `recovery.py`), `evaluate.py` |
| Lifecycle cost per D5, net warranty beside gross | 💲 | `afterlife/cost.py`, Overview screen |
| Review status on extracted terms (D6) | 🛠 | `afterlife/extract_terms.py`, `supplier_terms` |
| Brief keeps the four evidence levels apart (D7) | shared | `afterlife/brief.py` |
| Copy confirmed rules into the contract and accounting doc | 🛠 | `docs/build/data-contract.md`, `docs/research/warranty-accounting.md` |

## Where we differ from the review
- **Agreement review:** the review suggested reviewing only amended, missing and low-confidence terms. We review every agreement once (D6).
- **Dates:** the review treated payment dates as missing. v4 has `paid_date`, so filing deadlines work in the demo; only the warranty start date is a limitation (D8).
- **Validation:** the review left hard stop vs. quarantine open. Hard stop for the demo (D1).
