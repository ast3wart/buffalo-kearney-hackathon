# Velocity prompts for the financial model

[← index](index.md) · Paste into **Velocity Research** (Buffalo team space). Log each answer in [velocity.md](../../research/velocity.md). Put the numbers in the inputs with a `source` label (measured / survey / vendor / estimate / assumption).

**How:** run 4–6 at once (~5–10 min each). If Velocity asks scoping questions, reply "use defaults, go". If one fails, narrow it to 2–3 specific numbers and ask again.

**Every prompt has a fallback** (labeled *assumption*). Code against the fallback now and replace it when the answer lands.

| Batch | Prompts | When |
|---|---|---|
| **1 (now)** | #1–6, #15, #16, #17 | before CP1 |
| 2 | #18, #19, #20, then P2 #7–11, #14 from the [backlog](../../research/brandon-research-backlog.md) | CP1 → CP2 |

---

## Batch 1: P1, the model can't run without these
*(#1–6 are copied from the [backlog](../../research/brandon-research-backlog.md) so everything is in one place.)*

### #1 · Per-plant baseline (→ `plant_financials`)
```
For US discrete manufacturing plants with 100–249, 250–499 and 500+ employees, what are typical (a) MRO/spare-parts inventory values, (b) annual maintenance budgets, (c) annual MRO purchases? Use benchmarks such as SMRP (maintenance cost as % of replacement asset value), maintenance cost as % of revenue (e.g. 2–5%), and inventory turns for MRO. Give low/base/high per size band with sources, label measured vs vendor, and push back on commonly repeated but unsourced figures. Use defaults and don't ask clarifying questions.
```
**Fallback (assumption):** spares inventory $1–3M (base $2M), maintenance budget $3–7M (base $5M) for a ~250-employee plant. These are the registry defaults.

### #2 · Carrying cost % (→ `plant_financials.carrying_cost_pct`)
```
What is a defensible annual carrying cost rate for MRO and spare-parts inventory in manufacturing (cost of capital, storage, insurance, obsolescence/shrink)? Distinguish finished-goods rules of thumb (20–30%) from MRO specifically, and separate cash costs from accounting write-offs. Give a low/base/high with sources. Push back if the commonly cited 20–30% doesn't apply to MRO. Use defaults; no clarifying questions.
```
**Fallback (assumption):** 10% / 15% / 20%.

### #3 · Rush/expedite premiums (→ `plant_financials.rush_premium_annual`)
```
What share of MRO and spare-parts purchases in manufacturing are emergency or expedited, and what premium (freight, broker markup, overtime) do plants pay versus planned purchases? Find surveys or case studies with sample sizes, separate vendor claims from measured data, and give low/base/high per plant per year. Use defaults; no clarifying questions.
```
**Fallback (assumption):** $0 / $10k / $20k per plant per year (the deep-dive §D scenario).

### #4 · End-of-life components per plant + failure probability (→ `kb.annual_failure_rate`)
```
In a typical US mid-market manufacturing plant, how many PLCs, drives, HMIs and controllers are installed, what share are discontinued or end-of-life, and what is a reasonable annual failure probability for such components (MTBF data, field failure rates, age-dependent failure)? Use OEM reliability data, installed-base audit cases and academic sources. Give low/base/high and push back where data is missing. Also: does failure probability depend on lifecycle status, or mainly on age, duty and environment? Use defaults; no clarifying questions.
```
**Fallback (assumption):** failure probability by **age**: < 10 yrs 2–5%/yr, 10–20 yrs 5–10%/yr, > 20 yrs 10–20%/yr. Lifecycle status changes **how long you're down** (see model-spec §1), not the failure odds.

### #5 · Planned vs emergency replacement cost (→ `kb.migration_cost`, emergency multiplier)
```
Compare the all-in cost of a planned migration of an obsolete PLC or drive (hardware, engineering, scheduled downtime) with a failure-driven emergency replacement (expedited parts or broker, overtime, extended downtime). Find quotes, cases or engineering estimates with sources; express as a ratio and in dollars for a mid-market plant. Push back on unsupported '3x' style claims. Use defaults; no clarifying questions.
```
**Fallback (assumption):** emergency = 1.5× / 2× / 3× planned, before downtime.

### #6 · Value-capture share (→ `price.value_capture_pct`)
```
For B2B industrial software and asset-management / MRO-optimization services, what share of the customer's quantified savings do vendors typically capture in price (value-based pricing, gain-share contracts, typical ROI multiples buyers require such as 3–5x)? Include examples (SPARETECH, Verusen, CMMS vendors, MRO consultants with gain-share) and payback thresholds that procurement accepts. Give a defensible range with sources. Use defaults; no clarifying questions.
```
**Fallback (assumption):** 20% / 30% / 40%. Keep it a variable. Buyer ROI ≥ 3× and payback ≤ 12 months.

### #15 · Discount rate (→ present value of the CapEx cliff, price cut, holdback) · NEW
```
What discount rate should be used to present-value a 3–5 year equipment CapEx forecast for a US mid-market discrete manufacturer, (1) by the owner for planning and (2) by a private equity buyer pricing an acquisition? Give (a) industry WACC for industrial machinery / diversified manufacturing (e.g. Damodaran industry data, latest year), (b) typical PE buyout hurdle rates and target IRRs for industrial deals, and (c) which one practitioners use when pricing deferred CapEx or holdbacks in diligence. Low/base/high with sources. Use defaults; no clarifying questions.
```
**Options:**
- **A:** Damodaran's industry WACC (public and quotable).
- **B:** WACC for the own-plant lens, a PE hurdle rate for the deal lens.
- **Fallback (assumption):** 8% / 10% / 12% for the owner, 15% / 20% for the deal lens.

### #16 · Replacement and migration cost by component type (→ KB cost columns) · NEW
```
Give typical 2025–2026 US price ranges for replacing or migrating these industrial automation components in a mid-market plant: PLC CPU/controller (small and large chassis), I/O modules, variable frequency drives by size band (<10 HP, 10–100 HP, >100 HP), HMI panels (small and large), servo drives and motors, industrial power supplies. For each: new list or street price, refurbished/surplus price, and the engineering labor to migrate an obsolete unit to its successor (hours × rate). Use distributor list prices, refurbisher listings and OEM migration guides; label vendor vs measured. Use defaults; no clarifying questions.
```
**Options:**
- **A:** Velocity.
- **B:** your own listings research. It's the same work as `listings.csv`, so the price side comes for free.
- **Fallback (assumption, verify):** PLC CPU $3–15k, drive $1–20k depending on size, HMI $1–8k. Migration engineering: 20–80 hrs × $150–300/hr.

### #17 · Escrow, holdback and price conventions for equipment risk (→ `deal_adjustment`) · NEW
```
In US middle-market and lower-middle-market manufacturing acquisitions, how is identified equipment risk or deferred CapEx handled: a dollar-for-dollar purchase price reduction, a specific indemnity, a special escrow or holdback, or a debt-like item in the price? Give typical sizes (indemnity escrow and purchase-price-adjustment escrow as % of deal value, with and without R&W insurance), escrow durations, and how R&W insurance treats known issues. Also: is there any evidence that sell-side or vendor diligence reduces escrow size or time-to-close? Cite the exact report and year (SRS Acquiom deal terms study, ABA private target deal points study, R&W insurers). Use defaults; no clarifying questions.
```
**Options:**
- **A:** Velocity. Get the **exact** SRS Acquiom / ABA figures and the report year.
- **B:** treat deferred CapEx as a debt-like item: price cut = PV(low). Holdback = PV(high − low).
- **Fallback (assumption):** B, plus escrow-reduction scenarios of 0 / 0.5 / 1 point labeled "not evidenced".

---

## Batch 2: after CP1
### #18 · Cost to serve per plant (→ gross margin, slide 7) · NEW
```
For an AI-assisted equipment assessment of a plant with ~150 machines and ~400 photographed components, estimate the cost to deliver: (a) vision-model API cost per photo at current list prices, (b) human review hours per plant at typical reliability-engineer or analyst rates, (c) optional on-site photo capture labor if the customer doesn't take photos, and (d) annual cost to keep the registry current. Give per-plant totals low/base/high and the implied gross margin at $10k, $25k and $50k per plant per year. Use defaults; no clarifying questions.
```
**Options:**
- **A, best:** calculate it yourself. Use the API cost per image from Anthropic's pricing page, and reviewer hours from Asher's real runs at CP2.
- **Fallback (assumption):** API under $50/plant. Review 4–12 hrs × $75–150 ≈ $300–1,800. On-site capture, if needed: 1–2 days × $1–2k.

### #19 · Spending limit without capital approval (→ ceiling on price) · NEW
```
In US mid-market manufacturing companies, what are typical spending authority limits at plant manager, VP Operations and CFO level for operating expense and software or service purchases (i.e. the amount that can be approved without a capital request or board approval)? Also: typical procurement thresholds that trigger formal RFPs. Give ranges with sources (delegation-of-authority surveys, procurement benchmarks). Use defaults; no clarifying questions.
```
**Options:**
- **A:** Velocity.
- **B:** price just under the plant manager's limit as a go-to-market choice, with the reason on the slide.
- **Fallback (assumption):** plant manager ~$10–25k, VP Ops ~$50–100k. That makes **$10–25k per plant** the quick-yes zone.

### #20 · Cost of moving a spare between sister plants (→ nets the spare-sharing lever) · NEW
```
What does it cost to transfer a spare part between two plants of the same company or PE portfolio: freight (expedited vs ground) for small electronics like PLCs and drives, intercompany transfer pricing and paperwork, testing or re-certification before install, and admin hours? Compare with buying the same part new or refurbished. Give per-transfer low/base/high with sources or cases. Use defaults; no clarifying questions.
```
**Options:**
- **A:** Velocity.
- **B:** a carrier rate calculator for a 5–20 lb box, plus 1–2 admin hours.
- **Fallback (assumption):** $150–1,000 freight + ~$200 admin per transfer.

---

## Where each answer goes
| Prompt | Column / parameter | File |
|---|---|---|
| #1 | maintenance_budget, spares_inventory_value | `plant_financials.csv` |
| #2 | carrying_cost_pct | `plant_financials.csv` |
| #3 | rush_premium_annual | `plant_financials.csv` |
| #4 | annual_failure_rate (by age band) | `kb.csv` / a parameter in `valuation.py` |
| #5 | emergency multiplier, migration_cost | `kb.csv` / `valuation.py` |
| #6 | value_capture_pct, ROI/payback limits | `pricing.py` |
| #15 | discount_rate (owner, deal) | `valuation.py` |
| #16 | migration_cost, replacement ranges | `kb.csv` |
| #17 | price-cut rule, holdback rule, escrow scenarios | `valuation.py` |
| #18 | cost_to_serve | `pricing.py` (margin) |
| #19 | price ceiling check | `pricing.py` |
| #20 | transfer_cost | `sourcing.py` / `pricing.py` |
