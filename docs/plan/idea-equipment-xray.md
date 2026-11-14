# Equipment X-Ray (working name): plan for Brandon to review

**Status:** PROPOSED pivot (Sat Nov 14, ~11:45 AM). Asher + Claude, after the judge review. **Brandon: read, push back, and say yes or no.** Nothing in the code has changed yet.

> **Update (~4:30 PM):** market research repositioned us: **evaluating your own plants is the business; acquisitions are one entry point.** The current version is the **[roadmap](roadmap-equipment-xray.md)**. Sections below that frame this as deal-only are superseded.
>
> **Update (~12:30 PM):** a mentor reviewed the idea, said keep digging, and steered us toward a **platform roadmap** (diagnostic MVP → central machine/part registry → **parts sourcing** → PE portfolio network). See **[roadmap-equipment-xray.md](roadmap-equipment-xray.md)**.

---

## 1. Why we're pivoting
A Kearney judge reviewed Afterlife and was blunt:
- **Our scope was way too wide** ("trying to cure cancer").
- **Half the room is building "make a consultancy more efficient"**, which won't win.
- **Nobody is doing the Startup track.**
- **The biggest holes are in old companies** that coast on their name and have **acquired lots of smaller companies**.

What did land with him: **reading documents/contracts** and **testing against a planted answer key**. We keep both.

## 2. The idea in one paragraph
Big, old manufacturers grow by **buying smaller companies, largely for their production capacity**. But a buyer can't easily see whether the target's machinery is about to need millions in replacements, especially the **hidden parts inside the machines** (controllers, drives, screens) that manufacturers have **stopped making**, where one failure can stop a whole production line for weeks. **Equipment X-Ray** takes the target plant's equipment list and photos of each machine's nameplate and control cabinet, identifies every machine and the key components inside, checks each against manufacturer lifecycle data, and gives the deal team **a "CapEx cliff" (equipment spending needed, year by year), how much less to pay, and the top single points of failure**, with the evidence behind every number.

**One-line pitch:** *"Anyone can ask an AI what a machine is. We tell a buyer which hidden parts will stop which production lines, what it'll cost and when, and we show the evidence behind every number."*

**Track:** **Startup** (empty track; the judge pointed at it; it asked for hardware and/or software). Kearney industries: **Industrial Goods** and **Private Equity**. Can still nod to Track 3 (it's cost linkage for equipment instead of parts).

## 3. The problem, and why it's big
- **Buyers acquire for production capacity**, but the condition of that capacity is hard to judge in a short diligence window.
- **Equipment ages invisibly:** a machine can look fine while it runs on a **controller the manufacturer discontinued years ago**, with no spare anywhere. When it fails, the line can be down for weeks while engineers hunt for used parts.
- **Old, acquisitive companies are the worst case:** many plants, many brands, inconsistent records, nobody with a full picture.
- **Today's answer is slow and manual:** equipment appraisers walk the plant for days or weeks, focused on what machines would *sell* for, not on what breaks next and what it costs to keep running.
- Buyers do struggle with it: e.g. a buyer on a search-fund forum asking how to even get factory equipment assessed, because it's outside their finance background ([thread](https://searchfunder.com/post/does-anyone-have-experience-with-due-diligence-on-machinery-and-equipment)).

## 4. User and moment
- **User:** the **deal team buying a manufacturer**: a private equity firm (often rolling up several old companies) or a corporate M&A / corporate development team.
- **Moment:** pre-signing diligence, typically a short site visit with limited access and messy data.
- **Decision we change:** the **price**, the **deal terms** (e.g. holdback for equipment risk), or **walking away**.

## 5. Workflow (the full product)
| # | Step | What happens | Notes |
|---|---|---|---|
| 1 | **Intake** | Target's equipment list (spreadsheet/export), maintenance logs if any, **photos of each machine's nameplate and control cabinet**; optional short-term clip-on sensors | Works with messy data, no system integration |
| 2 | **Quality check** | Blurry, glare, cut-off nameplate → ask for a retake | Real-product necessity |
| 3 | **Identify** | **Vision AI (Claude)** reads make, model, catalog no., serial, year, ratings; lists components it sees inside the cabinet (controllers, drives, HMIs) with confidence | No model training needed (see §7) |
| 4 | **Normalize** | Clean messy names ("A-B" = "Allen-Bradley"), standardize catalog numbers | Reuses our matching/normalize code |
| 5 | **Lifecycle lookup** | Each machine and component vs. a **knowledge base**: discontinued or not, typical lifespan, replacement cost, spare availability | The knowledge base is the real moat |
| 6 | **Condition** | Age, maintenance history, downtime; sensors on the roadmap | |
| 7 | **Value** | Replacement cost new, current value range, remaining useful life | Ranges, not fake precision |
| 8 | **Forecast** | **CapEx cliff** by year; **single points of failure** per production line; spare availability and sourcing options | Rolls up across brands and machines |
| 9 | **Deal output** | **"Pay $X less"** / holdback, risk list, a 100-day replacement plan | Deal language, not maintenance language |
| 10 | **Human review** | Low-confidence readings and big-ticket items are flagged for a person | Nothing goes into an investment memo unreviewed |

## 6. What already exists (and the gaps)
| Who | What they do | Gap for our use case |
|---|---|---|
| **Equipment appraisal firms:** [Hilco](https://hilcoglobal.com/services/asset-appraisals/machinery-and-equipment-appraisals/), [Gordon Brothers](https://www.gordonbrothers.com/industry/machinery-equipment/), [Kroll](https://www.kroll.com/en/services/valuation-services/machinery-and-equipment-valuation), [B. Riley](https://brileyfin.com/capabilities/field-examination-services/machinery-equipment), [Plante Moran](https://www.plantemoran.com/how-we-can-help/services/valuation-services/machinery-and-equipment-appraisals) | Human appraisers value machinery, incl. pre-deal diligence; Hilco has modeled post-acquisition CapEx for a PE buyer ([case](https://hilcoglobal.com/case-studies/assessing-quality-and-scalability-to-project-post-acquisition-costs/)) | Slow and manual; focused on **sale/liquidation value**, not **what breaks next and what it costs to keep running** |
| **Machine-health sensors** (e.g. [Augury](https://www.augury.com/blog/machine-health/the-right-questions-to-ask-when-evaluating-an-ai-powered-condition-monitoring-solution/)) | Sensors predict failures from vibration, heat, sound | Need **ownership + months of installed sensors**; useless in a 2-week diligence window |
| **Manufacturer lifecycle tools** ([Rockwell](https://www.rockwellautomation.com/en-gb/capabilities/industrial-maintenance-support/modernization/legacy-product-support.html), [Siemens](https://industrialmonitordirect.com/blogs/knowledgebase/siemens-s7-plc-phase-out-checking-product-lifecycle-status)) | Look up whether a part is discontinued | **One part number, one brand at a time**; no plant-wide view, no dollars, no "which line dies first" |
| **Maintenance software** (SAP's maintenance module, IBM Maximo, …) | Records of machines you already own | The target's records are usually messy, partial or missing |
| **Early AI diligence experiments** ([searcher beta](https://searchfunder.com/post/looking-for-searchers-to-test-ai-powered-technical-due-diligence-on-live-deals), a [$15k readiness audit](https://cdn.fabtechexpo.com/products/28160/ai-and-automation-readiness-audit)) | General AI help for small-deal diligence | Not focused on equipment lifespan, obsolescence or spending |

*Sources are mostly company/vendor pages; good enough to show the landscape, not for hard numbers.*

## 7. Why us vs. "Joe Schmo with the same idea"
The AI model is **not** the differentiator; anyone can send a photo to Claude. Joe builds: *photo → "CNC lathe, ~15 years old, worth $40–60k."* We build:
1. **We look where the risk hides:** the **components inside** (discontinued controllers, drives, screens) and whether a spare exists, rolled up per production line. A 30-year-old press with a supported controller is fine; a 10-year-old machine on a discontinued controller is a bomb.
2. **Deal language, not machine facts:** CapEx cliff, **"pay $X less"**, top 3 single points of failure.
3. **Plant-wide, cross-brand roll-up:** 40 machines, 6 brands → one view. Manufacturer tools do one part number at a time.
4. **Evidence behind every number:** nameplate photo, manufacturer lifecycle notice, asset record, confidence; weak readings go to a human.
5. **Measured accuracy:** a test set with known answers (the approach the judge liked).
6. **Moat in a real company:** every diligence adds labeled photos, real component lists and **what actually failed after closing** → a proprietary database, and later our own trained detector.

## 8. How the AI part works (no training needed)
- Modern vision models already read nameplates, labels and cabinet components. We send a photo and ask for **structured output** (fields + confidence + "unclear" when unsure). Model pinned: `claude-sonnet-5-5`.
- **The hard part is the knowledge base, not the AI:** reading "1756-L61" is easy; knowing it's a discontinued controller family, what a replacement costs, and the typical life of that machine type is data work. Hackathon: a **curated, sourced table for ~30 machine/component types**.
- **Training only later (roadmap):** a component detector for crowded cabinet photos needs hundreds–thousands of labeled photos. Not a weekend task.

## 9. What we actually build this weekend (working slice, end to end)
| # | Piece | Real or simplified |
|---|---|---|
| 1 | **Fake "target factory"**: equipment list for ~40 machines across lines/brands + an **answer key** (true model, components, discontinued status, planted single points of failure) | Synthetic, honest about it |
| 2 | **Photo → Claude vision → structured readings** | **Real**, live |
| 3 | **Knowledge base** (~30 types: lifecycle status, lifespan, replacement cost, spare availability, with sources) | Curated, sourced where possible |
| 4 | **Normalize + match** readings to the knowledge base | Real (reuse matching code) |
| 5 | **Scoring:** remaining life, obsolete components, single points of failure per line | Real |
| 6 | **Deal output:** CapEx cliff chart, "pay $X less", top 3 risks | Real (ranges) |
| 7 | **Evidence view:** click a number → photo, reading, source, confidence | Real |
| 8 | **Measured accuracy** on a test set (own photos + generated nameplate images with known text) | Real |
| 9 | **Live moment:** photograph a real machine in the room on stage; it appears in the report | Real |

**Simplified / roadmap (say so on stage):** sensors, live market valuations, a trained component detector, maintenance-log reading at scale.

**What carries over from Afterlife:** app shell (Next.js + FastAPI; SQLite for the demo, see pivot-plan/06-tech-stack.md), CI + `checkpoint.sh`, the synthetic generator + answer-key approach, normalize/matching, document reading, the Velocity research habit.

## 10. Pitch outline (Startup track)
1. **Hook:** "Buyers pay for a factory's production capacity, and can't see the equipment cliff coming."
2. **Problem + who feels it:** PE and corporate M&A buying old manufacturers.
3. **Demo:** target factory → CapEx cliff → "pay $X less" → evidence → live photo of a real machine.
4. **Why not existing options:** appraisers (slow, value-focused), sensors (need months), manufacturer tools (one part at a time).
5. **Business model:** fee per diligence + subscription for PE firms doing many deals (rough numbers only).
6. **Roadmap:** sensors → trained detector from our photo library → post-deal monitoring.
7. **Why now:** aging industrial equipment, acquisition-heavy roll-ups, vision AI finally good enough.

## 11. Plan for ~20 hours
| When | Asher | Brandon |
|---|---|---|
| Next ~3 h | Knowledge base (types, lifecycle, costs, sources) | Photo → Claude vision → structured output; test on real photos |
| Next ~4 h | Fake target factory generator + answer key | Normalize + match readings to the KB; scoring |
| Next ~4 h | CapEx cliff + deal outputs + API | Evidence view + accuracy measurement |
| Evening | Screens + pitch deck + business model slide | Live-capture flow + demo dry runs |
| Sun AM | Run-through, backup video, **submit by 8:30** | |

Batch-review checkpoints still apply (CP3 / CP5 / CP6 in `docs/team/workflow.md`), adjusted to the new plan.

## 12. Risks and open questions
- **Track switch:** confirm with organizers we can move to the Startup track now.
- **Real lifecycle data:** how much can we source in hours? (Rockwell/Siemens lifecycle tools exist; may need a curated subset.)
- **Photo reading accuracy** on old, dirty, worn nameplates: measure it, don't assume it.
- **Valuations** are ranges from a curated table; say so.
- **Usage history** ("how it was used") needs logs/sensors: roadmap, not demo.
- **Physical demo:** find a real machine with a nameplate at the venue (HVAC unit, printer, projector, vending machine, power tool).
- **Market/evidence slides:** run Velocity on "how equipment is assessed in M&A diligence today" and "how often buyers are surprised by post-deal CapEx".

## 13. Questions for Brandon
1. **Yes / no / modify** on the pivot?
2. **Split:** happy with the plan in §11, or swap (e.g. you take the KB, Asher takes vision)?
3. **Anything the judge said that this misses?** You may have heard things Asher didn't.
4. **Name ideas:** "Equipment X-Ray" is a placeholder.
5. **Any hardware** you want in the demo (e.g. a cheap clip-on sensor as a bonus)?
