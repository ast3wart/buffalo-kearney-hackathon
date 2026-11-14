# Afterlife: project brief (Team Buffalo)

**Read this first.** This is the master context document for Team Buffalo's project at the Kearney × PERLab Hackathon (Nov 13–15, 2026). The other sources in this library go deeper on specific parts.

## The hackathon and track
- **Event:** Kearney × PERLab Hackathon, sponsored by Growth Signals. Submissions are due **Sunday Nov 15, 8:30 AM**. Judging is at 9:30 AM and finalist pitches at 3:30 PM.
- **Track:** Corporate Track 3, **BOM Cost Linkage.** *"Build a tool that connects a company's BOMs to its spend cube, the massive list of every part it buys and from whom, including spare and warranty parts. Today the two don't tie, and BOMs share some of the same parts. That makes the true financial impact of any one BOM hard to see, so companies can't easily compare prices across suppliers and products or find cost savings."*
- **No dataset was provided**, so we generate realistic synthetic data calibrated to public benchmarks.
- Use of the Velocity / Growth Signals platform is required.

## Team
- **Asher:** 💲 Spend thread (BOMs, production and spare-part purchasing, true cost, spare-part markups)
- **Brandon:** 🛠 Warranty thread (warranty claims, claim-to-part matching, early-warning spike detection)

## The idea: Afterlife
**One-liner:** *Every BOM team will show you what a product costs. We show you the warranty problem coming before it costs you, and which supplier to take it to.*

A manufacturer's **BOMs** (engineering), **production purchases** (procurement), **spare-part purchases** (service), and **warranty claims** (service) don't link to each other:
1. **Spare parts** are often bought by a separate service team from distributors, as free-text purchase lines with no internal part number. The company pays 1.5–5× more for the *same part* it buys cheaply for production, and nobody sees it.
2. **Warranty claims** record the symptom (e.g. "hydraulic leak, replaced seal kit") and a failure code, not the supplier's part number. So the company can't tell which supplier's part failed, and can't charge the supplier back (*supplier warranty recovery*).
3. **Each product team only sees its own claims.** A shared part failing slightly more often across 7 products looks like noise to each team.

**Afterlife:**
- **Links** BOM parts ↔ production spend ↔ spare-part spend ↔ warranty claims, including claims with no part number. These are inferred from failure code + claim text + that product's BOM.
- **Early warning:** spots a shared part from one supplier failing across many products after a specific build month.
- **Lifecycle cost:** build cost vs. true cost including spares and warranty, per product.
- **Supplier brief:** a one-page, deal-ready document per supplier with two asks:
  - **warranty recovery review** ("N claims since March builds are linked to your seal kit. Here's the evidence; we request a returned-part review"). Afterlife produces evidence-backed **leads**, not findings of supplier fault
  - **spare-part price harmonization** ("we pay $4.12 in production and $15 as a spare for the same part")

**Demo moment:** ⚠ *Seal kit SK-220 (Supplier X): claims up 3× across 7 products since the March build. Linked claim cost $2.1M, pending review. [Generate brief]*

**What Afterlife does NOT do:** it doesn't determine supplier fault or liability. A failure code is a symptom, not a cause, and recovery depends on returned-part analysis, engineering review, and contract terms. Dollar figures are **recovery opportunities** (linked claim cost × a 25–50% *scenario* capture rate), not money owed.

## Three synthetic companies (to show it generalizes)
| Company | Industry | Warranty % of revenue (calibrated to 2024 SEC filer) | Role | What makes it different |
|---|---|---|---|---|
| Prairie Utility Vehicles | Utility vehicles, compact tractors | 2.5% (Polaris 2.56%) | Tune matching here, main demo spike | ERP shorthand (`BRG,BALL,6204-2RS`), `100-4471-02` part numbers |
| Ironridge Compact Equipment | Skid steers, mini excavators | 2.9% (CNH Industrial 2.87%) | Holdout test, different spike | Arrives as a **raw SAP extract** (EKPO/EKKO/LFA1/MARA field names). Has an **acquired plant** on a legacy ERP with no internal part numbers. `IR-04471` part numbers |
| Northwind Climate Systems | Commercial rooftop HVAC | 1.5% (Carrier 1.54%) | Holdout test, **no spike** (false-alarm control) | HVAC vocabulary: failure codes `REF-ELP`, `CMP-FTS`, `CMP-NOI`, `FAN-VIB`, shorthand `CMPR`/`TXV`/`RTU`, `NW4471A` part numbers |

Builds run Jan 2025 – Sep 2026, data as of Oct 31 2026, 24-month warranty.

## Key design decisions (data contract v3, Sat Nov 14)
- **Months in service (MIS):** spikes are measured as claims within the first 3 months in service per 1,000 units built, using only build months old enough to have 3 months of data. Raw claims-by-build-month is also shown, to illustrate why it misleads: recent builds look artificially healthy.
- **SAP-realistic spend data:**
  - an internal part number (SAP material number) on ~85% of production lines but only ~15% of service lines
  - a supplier-part-number crosswalk (SAP purchasing info records) for production suppliers only
  - prices "per N units" (SAP price unit)
- **Failure codes** follow ISO 14224-style failure modes (`SYSTEM-MODE`, e.g. `HYD-ELP` = hydraulic external leakage). The mode is the observed symptom, not the cause.
- **24 part categories:** bearing, seal, gasket, hose, fitting, hydraulic_component, filter, belt, gear, wheel_tire, brake, cooling, fuel, electrical, harness, sensor, battery, lighting, fastener, structural, plastic, compressor, refrigerant_component, motor. **16 failure codes** in the union, and each company uses a subset.
- **Real supplier attribution:** key parts are **dual-sourced**, and lot records (`build_supply`) show which supplier's purchase order each product/month consumed. The planted spike sits on **one supplier's lots from a specific PO onward**, so the alert names the supplier *and* the lot. In the sample data, seal-kit claims jump about 3× on builds using only Keystone's April lot, and about 2× on a product using it half the time.
- **Evidence on every link:** each link records its method (exact part number, supplier part-number crosswalk, spec code, failure code + BOM, fuzzy text, LLM tie-break, human), a confidence, the source system, a JSON of the signals that agreed, and the pipeline run that produced it.
- **Not overfit, enforced:** each company has its own abbreviations and failure-code subset as *data*, and a test fails if the matching code mentions any company, part or supplier ID.
- **Accuracy is measured:** the generator plants the correct links, so we report precision and recall. We tune on Prairie and report holdout accuracy on the other two.
- **Stack:** Python (pandas, DuckDB, rapidfuzz) → FastAPI → Next.js app with 4 screens (Overview, Linking explorer, Early warning, Supplier brief). Claude API writes the brief.

## Benchmarks we already have
- 217 US public companies reported warranty payments in 2024 (SEC XBRL `ProductWarrantyAccrualPayments`). Ford paid $5.83B, Caterpillar $824M, Cummins $704M. The median is ≈0.6% of revenue, but equipment and vehicle makers run 1.3–3%.
- Warranty Week: suppliers bore about **10–15%** of tracked automotive warranty costs (about 12% in early 2023). The often-quoted **37%** is only a hypothetical ceiling based on suppliers' share of sales, **not** a recoverable amount. The OEM/supplier split was ~84/16 in 2017. GM recovered at least 90% of the Chevy Bolt recall cost from its battery supplier.

## What we want from Velocity
1. **Supplier warranty recovery:** how manufacturers recover warranty costs from suppliers, and what prevents them (data gaps, contracts, causal-part attribution).
2. **Spare-part price gap:** evidence on how much more OEMs pay for spare and aftermarket parts than for the same parts in production.
3. **Prior art and patents** on linking warranty claims to causal parts and suppliers using BOM data, and on early detection of emerging field failures.
4. **Market:** warranty-analytics and aftermarket/spend-analytics software, who already sells it, and where the gap between procurement tools and warranty tools is.
5. **Concept strength:** compare Afterlife against simpler alternatives, e.g. a plain BOM cost rollup ("Teardown") and a tariff-exposure simulator ("Tariff Radar").
6. **Judge questions:** what Kearney procurement and operations consultants would challenge about this approach.
