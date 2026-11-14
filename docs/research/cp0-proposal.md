# CP0 proposal: contract changes from research

**Status: DECIDED at CP0 (Fri Nov 13, Asher + Brandon). Applied** to `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/check.py`, `scripts/make_sample.py`.

| # | Decision |
|---|---|
| 1 | ✅ **Both views:** raw claims-per-1,000 by build month shown as the intuitive chart, and the **MIS-window method drives the alerts**. Side by side in the app to show why raw misleads |
| 2–4 | ✅ `part_no` on spend lines, ✅ `info_records.csv`, ✅ `price_unit` |
| 5 | ✅ 12 `SYSTEM-MODE` failure codes |
| 6 | ✅ All 21 categories |
| 7 | ✅ Builds Jan 2025 – Sep 2026, data as of Oct 31 2026, 24-month warranty, MIS window 3 |
| 8–9 | ❌ Claim line items and BOM uom stay out (Q&A "next step") |
| API | ✅ Shapes accepted as drafted (`/claim-rates` returns both views) |
| Style | ✅ Clean industrial: light neutral, teal accent, red alerts, mono part numbers |
| Branches | ✅ `spend/...` and `warranty/...` |
| Companies | ✅ **Added after CP0: 3 companies, not 1** (`afterlife/profiles.py`). Prairie (tune), Ironridge (holdout), Northwind (holdout, no-spike control). One folder per company, same contract |

🛠 = Brandon (Warranty) · 💲 = Asher (Spend)

## TL;DR
| # | Change | Who | Why it matters | Recommend |
|---|---|---|---|---|
| 1 | **Measure spikes by months-in-service, not raw claims by build month** | 🛠 | Our current method would flag a fake drop for recent builds and could hide the real spike. This is the one real flaw | ✅ must |
| 2 | Add a nullable `part_no` to spend lines (SAP "material number") | 💲 | Real POs carry the internal part number *most* of the time. The real gap is the free-text lines without one | ✅ |
| 3 | Add `info_records.csv` (part ↔ supplier part number crosswalk) | 💲 | That's how SAP links supplier PNs to internal parts. Production buys have it, service buys mostly don't | ✅ |
| 4 | Add `price_unit` to spend lines | 💲 | SAP prices are "per N units". A classic trap, cheap to add | ✅ |
| 5 | Failure codes = system + failure **mode** (ISO 14224 style) | 🛠 | Modes describe the symptom, not the part, which is *why* claims don't name a part | ✅ |
| 6 | Lock the part **category list** (below) | both | `failure_codes.likely_categories` depends on `part_master.category` | ✅ must |
| 7 | Add `dataset_info.csv` (`data_as_of`, company, currency) | both | Needed for #1, and shown in the app header | ✅ |
| 8 | Claim line items (SAP WTY style: parts / labor / sublet) | 🛠 | More realistic, but costs time | ❌ keep flat for MVP |
| 9 | BOM `uom` column | 💲 | Only matters for hoses/wire sold by length | ❌ skip (all EA) |

---

## 1. Months in service (the real flaw) 🛠
**What we found.** Warranty analysts group units by build month, but they compare claim rates **at the same months in service (MIS)**. A unit built last month has had one month to fail, while a unit built a year ago has had twelve. Counting raw claims per build month makes recent builds look artificially healthy. One quality forum notes build-month counts can take 18+ months to stabilize. The standard view is a build-period × failure-period (or × MIS) matrix, with alerts on cells well above expectation. SAS Field Quality Analytics' early-warning analysis works this way.

**What breaks in our plan.** `detect.py` was going to compare claims per 1,000 by build month against a baseline median. With a realistic generator, recent build months would show *fewer* claims just because they're young. That would cover up exactly the "since the March build" spike we want to show.

**Proposed fix (still simple):**
- `MIS = months between build_month and failure_date`
- Compare **claims within the first K months in service per 1,000 built** (K = 3), only for build months with at least K months of exposure as of `data_as_of`.
- Optionally show a small build-month × MIS heatmap. Judges from a quality background will recognize it immediately.
- Contract impact: no new claim columns. Needs `data_as_of` (#7).
- Generator impact (🛠): claims spread across MIS with a hazard curve (more early-life failures), and stop at `data_as_of`, so recent builds are genuinely immature.

**Pitch line:** "We compare like with like: claims in the first 3 months of service per 1,000 built, the way field-quality teams do it."

## 2. `part_no` on spend lines 💲
**What we found.** In SAP, a PO line *can* reference a material number. When it doesn't (a "text item"), the buyer types a short description and a material group by hand, the Material column is blank, and spend reports suffer because people pick material groups loosely. That free text is the main classification problem.

**Proposal:** add `part_no` (nullable) to `production_spend` and `service_spend`.
- Production: filled for about 85% of lines (stocked parts bought against the part number).
- Service: filled for about 15% (distributor buys are mostly free-text).

**Why it's better:** it makes the story honest. Production spend mostly ties already, and the *gap* is service spend plus claims, which is exactly Afterlife's pitch. The spend matcher's job becomes: trust `part_no` when present (check it), match the rest.

## 3. `info_records.csv` 💲
**What we found.** SAP keeps the supplier's own part number on the purchasing info record (EINA, field IDNLF, "Material Number Used by Vendor"), and it can flow into the PO line. That's the real-world crosswalk.

**Proposal:** a new table `info_records.csv`: `part_no, supplier_id, supplier_pn`. Present for production suppliers, **missing for the service distributor**. The matcher uses it as a high-confidence step.

## 4. `price_unit` 💲
**What we found.** SAP stores the net price (NETPR) per a **price unit** (PEINH), for example $58.90 *per 10*. The formula (value ≈ NETPR / PEINH × qty) is the standard interpretation, but our search didn't find official confirmation, so treat it as convention.

**Proposal:** add `price_unit` (int, default 1) to both spend tables. Price per EA = `unit_price / price_unit / pack_size(uom)`. Plant a few lines with `price_unit = 100` so a naive average breaks visibly. That's a nice "we know the traps" detail.

## 5. Failure codes as modes 🛠
**What we found.** ISO 14224 (the reliability-data standard) separates the **failure mode**, meaning the observed effect (external leakage `ELP`, vibration `VIB`, fail to start `FTS`, overheating `OHE`), from the **cause**. A claim records what the technician saw, not which part's supplier caused it. That's *why* the causal part is so often missing. We confirmed those four mode codes from secondary sources, not the standard itself.

**Proposal:** `failure_code = <SYSTEM>-<MODE>`, e.g. `HYD-ELP` (hydraulic external leak), `DRV-VIB`, `ELE-FTS`, `ENG-OHE`, `BRK-NOI`. Columns are unchanged. SAP's warranty module also has a "part that causes damage" flag on claim items, which is what our `causal_part_no` stands in for.

| failure_code | system | mode | likely_categories |
|---|---|---|---|
| HYD-ELP | hydraulic | external leakage | seal;hose;fitting;hydraulic_component |
| HYD-LOP | hydraulic | low output / pressure | hydraulic_component;seal;filter |
| DRV-VIB | drivetrain | vibration | bearing;belt;gear;wheel_tire |
| DRV-NOI | drivetrain | noise | bearing;gear;belt |
| ENG-ELP | engine | external leakage (oil) | filter;seal;gasket |
| ENG-OHE | engine | overheating | cooling;belt;sensor |
| ELE-FTS | electrical | fail to start | electrical;battery;fuel;sensor |
| ELE-INT | electrical | intermittent operation | electrical;sensor;harness |
| BRK-NOI | brakes | noise | brake |
| BRK-DEG | brakes | degraded performance | brake;hydraulic_component |
| BDY-STR | body | structural / cracking | structural;fastener;plastic |
| LGT-FTF | lighting | fails to function | lighting;harness |

## 6. Category list (lock it tonight) both
Owned by 💲 in `part_master.category`, consumed by 🛠 in `failure_codes.likely_categories`. Proposed 21:

`bearing, seal, gasket, hose, fitting, hydraulic_component, filter, belt, gear, wheel_tire, brake, cooling, fuel, electrical, harness, sensor, battery, lighting, fastener, structural, plastic`

Cut any we won't generate. `afterlife/check.py` already flags failure-code categories that don't exist in `part_master`.

We didn't map these to UNSPSC codes. We couldn't verify the official class codes, so don't put them on a slide.

## 7. `dataset_info.csv` both
`key,value` rows: `company_name` (Prairie Utility Vehicles), `data_as_of` (e.g. 2026-10-31), `currency` (USD), `warranty_months` (24). Read by `detect.py`, shown in the app header.

## 8–9. Rejected for MVP
- **Claim line items** (SAP warranty claims have item types: MAT = parts, FR = labor, SUBL = sublet/external). It's realistic, but it doubles 🛠's generator and matcher work. Mention it in Q&A as "the next step".
- **BOM unit of measure.** All quantities stay in EA.

---

## Draft API shapes (for CP0 sign-off)
```jsonc
// GET /overview  💲
{
  "company": "Prairie Utility Vehicles", "data_as_of": "2026-10-31",
  "coverage": { "production_spend_pct": 0.97, "service_spend_pct": 0.81, "claims_pct": 0.74 },
  "products": [
    { "product_id": "UV-400", "build_cost": 2140.5, "spares_per_unit": 96.2,
      "warranty_per_unit": 118.4, "lifecycle_cost": 2355.1 }
  ],
  "spare_overspend_usd": 412000
}

// GET /alerts  🛠
[
  { "part_no": "200-1180-01", "description": "SEAL KIT,HYD CYL,40MM BORE",
    "supplier_id": "S-022", "supplier_name": "Keystone Seal Works",
    "products_affected": ["UV-400", "UV-600", "TR-250"],
    "start_build_month": "2026-04", "mis_window": 3,
    "baseline_rate": 4.1, "current_rate": 14.6, "ratio": 3.6,   // claims per 1,000 built within 3 MIS
    "claims": 29, "exposure_usd": 2100000, "recoverable_usd": 1450000 }
]

// GET /claim-rates/{part_no}  🛠  (chart + optional heatmap)
{ "mis_window": 3,
  "by_build_month": [ { "build_month": "2026-03", "units": 640, "claims": 3, "rate": 4.7, "mature": true, "is_spike": false } ],
  "heatmap": [ { "build_month": "2026-03", "mis": 1, "cum_rate": 1.6 } ] }
```

## Pitch numbers from this research (for the deck)
From Warranty Week's analyses of US companies. Treat them as indicative, since they vary by year and company:
- Suppliers paid **about 10%** of industry warranty costs in 2019, while a "fair share" could be **as high as 37%**. That gap is the recovery opportunity Afterlife goes after.
- 2017: the OEM/supplier split was about **84% / 16%**.
- Big recoveries do happen: GM recovered **at least 90%** of the Chevy Bolt battery recall cost from its supplier.
- → Use a **conservative capture rate** (e.g. 25–50% of attributable cost) for `recoverable_usd`, and say so.

## Sources
- SAP EKPO fields (NETPR, PEINH): [leanx.eu EKPO](https://leanx.eu/en/sap/table/ekpo.html), [se80 PEINH](https://www.se80.co.uk/sap-data-element/?name=peinh)
- Vendor material number IDNLF / info records: [sapdatasheet IDNLF](https://www.sapdatasheet.org/abap/dtel/idnlf.html), [SAP Community](https://answers.sap.com/questions/397123/populating-vendor-material-number-ekpo-idnlf-again.html)
- PO text items without a material: [SAP Help: PO without master record](https://help.sap.com/saphelp_46C/helpdata/EN/75/ee0db555c811d189900000e8322d00/content.htm), [SAP Community Q&A](https://community.sap.com/t5/enterprise-resource-planning-q-a/procurement-of-a-material-without-a-material-master-in-sap-mm/qaa-p/13976755/highlight/true), [SAP learning: consumables](https://learning.sap.com/courses/business-processes-in-sap-s-4hana-sourcing-and-procurement/creating-a-purchase-order-for-consumable-material_ef18e834-009e-4b76-a138-8134b7f7bd53)
- BOM item table STPO: [leanx.eu STPO](https://leanx.eu/sap/table/stpo/), [sapstack STPO](https://www.sapstack.com/tables/tabledetails.php?table=STPO)
- SAP warranty (WTY) causal part / item types: [ERPLingo: part causing damage](https://www.erplingo.com/sap-glossary/en/lo-wty/part-causing-damage), [leanx PVWTY](https://leanx.eu/en/sap/table/pvwty.html), [SAP warranty claim process](https://blogs.sap.com/2022/07/06/sap-warranty-claim-creation-business-process/)
- Months in service / maturity / early warning: [SAS Global Forum 2019 paper](https://support.sas.com/resources/papers/proceedings19/3877-2019.pdf), [Elsmar quality forum](https://elsmar.com/elsmarqualityforum/threads/10-2-5-warranty-management-process-measures.89661/), [Umbrex warranty claim rate](https://umbrex.com/resources/company-analysis/product-management/warranty-claim-rate-by-product/), [ReliaSoft warranty analysis](https://help.reliasoft.com/reference/life_data_analysis/lda/warranty_data_analysis.html)
- ISO 14224 failure modes: [Fabrico](https://www.fabrico.io/blog/iso-14224-failure-taxonomy-codes/), [Tetra Pak](https://maintenance.tetrapak.com/service/tpms/help/b-features/ampc/maintenance-plan-development/failure-analysis-configuration/failure-modes/failure-modes.html)
- Supplier recovery: [Warranty Week 2019](https://www.warrantyweek.com/archive/ww20190418.html), [Warranty Week 2017](https://www.warrantyweek.com/archive/ww20170622.html), [Warranty Week 2013](https://warrantyweek.com/archive/ww20130411.html)
