# Afterlife: the concept

**Track:** Corporate Track 3, BOM Cost Linkage (Kearney × PERLab, Nov 13–15 2026)

**One-liner:** *Every BOM team will show you what a product costs. We show you the warranty problem coming before it costs you, and which supplier to take it to.*

## The problem
A manufacturer's parts lists (BOMs), production purchases, spare-part purchases, and warranty claims live in four places owned by three teams (engineering, procurement, service). They don't link:

- **Spare parts** are often bought by the service team in small batches with no contract. The company pays 2–5× more for the *same part* it buys cheaply for production, and nobody notices because the part numbers don't match.
- **Warranty claims** are recorded by symptom and repair code ("hydraulic leak, replaced seal kit, 2.5 hrs"), not by the supplier's part number. So the company can't tell which supplier's part failed, and can't bill the supplier for it (*supplier warranty recovery*).
- **Each product team sees only its own claims.** A shared part failing a bit more often in 7 different products looks like noise to each team.

## What Afterlife does
1. **Links** BOM parts ↔ production spend ↔ service spend ↔ warranty claims, including claims with no reliable part number (inferred from failure codes plus claim text plus the product's BOM).
2. **Early warning:** because claims are linked across products through shared parts, it spots one supplier's part failing across many products after a specific build month. When a part is **dual-sourced**, it uses which supplier lot each build consumed to say *which supplier and which PO*, not just which part.
3. **Lifecycle cost:** build cost vs. true cost including spares and warranty, per product.
4. **Supplier brief:** a one-page, deal-ready document per supplier with the two levers:
   - **Warranty recovery review:** "N claims since the March build are linked to your seal kit, with this evidence and confidence. We request a returned-part review." It's a lead with evidence, not an accusation.
   - **Spare-part price harmonization:** "We pay $4.12 in production and $15 as a spare for the same part."

## Why this holds up in front of an SAP-savvy judge
- **"POs already carry the material number, so why match?"** Production POs at the main plant mostly do. The hard cases are an **acquired plant** on a legacy ERP (Ironridge), **service text items**, and **warranty claims**. That's where Afterlife works.
- **"Is it overfit to your own fake data?"** Three companies with different vocabularies, part-number styles and data formats (one arrives as a raw SAP extract). A test fails if the matching code mentions any company, part or supplier.
- **"How do you know it's that supplier?"** Lot-level supply records: the spike appears on one supplier's lots from a specific PO onward, and not on the other supplier's.

## What Afterlife does NOT do (say this out loud)
- **It doesn't decide fault or liability.** A failure code describes the symptom, not the cause. Whether a supplier pays depends on returned-part analysis, engineering review, and the supply contract, none of which are in our data.
- **Its $ are opportunities, not money owed.** "Recovery opportunity" = linked claim cost × a **scenario** capture rate (25–50%), shown as a range and labeled as such.
- The value: it turns thousands of unlinked claims into a short, ranked list of **evidence-backed cases worth investigating**, in days instead of weeks.

## The demo moment
> ⚠ **Seal kit SK-220 (Supplier X):** claims up 3× across 7 products since the March build. Linked claim cost $2.1M, pending review. **[Generate brief]**

## How this differs from a plain cost-rollup ("Teardown")
| | Teardown (what most teams will build) | Afterlife |
|---|---|---|
| Hard problem | BOM ↔ PO matching (part numbers on both sides) | + claims with **no** part number |
| Output | A cost chart | An alert plus a brief someone can act on Monday |
| Money found | Production purchasing (already scrutinized) | Spares and warranty (falls between teams) |
| Proof | "Trust us" | Accuracy measured against planted correct answers |

## Honest framing for judges
There's no provided dataset. We generate **three realistic companies**, each calibrated to a real public benchmark from SEC warranty filings:
- a utility-vehicle maker (≈ Polaris)
- a compact-equipment maker (≈ CNH)
- an HVAC maker (≈ Carrier), which has **no** planted problem, as a control

We tune on one company and report accuracy on the other two, so it isn't overfit. The control company checks that we don't raise false alarms. We plant the correct answers so we can **measure** our accuracy. The tool reads standard ERP-style flat files, so it would run on a real client's exports.
