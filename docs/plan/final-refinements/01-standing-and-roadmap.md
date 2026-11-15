# 1 · Where we stand, and what makes the platform complete

[← index](index.md)

## 1. Where the project stands (checked Sat ~10 PM on `brandon/rare-part`)
**The Phase 0 MVP is built and runs.**

| Piece | State |
|---|---|
| Demo portfolio | 6 plants, 3 companies, 1 fund; 129 critical parts in `demo.db` |
| Reading photos | 127 / 129 part numbers read exactly, **on rendered test photos** (not worn real plates) |
| Review flags | 17 parts flagged: 16 "no KB match", 1 "low confidence". **No screen to act on them.** |
| Money model | CapEx by year, line stoppers, sourcing (shelf first), savings and price, deal view |
| App | 6 screens (portfolio, plant, machine, part, live scan, sources); 14 API routes |
| Checks | 26 tests pass; `scripts/demo.sh` runs the stage build |

**Loose ends found:**
- `README.md` still says "MVP not built yet" and lists only the old files. `AGENTS.md` layout is stale too.
- The rare part (Westinghouse Numa-Logic PC-1100, 0 listings) is **not in `kb.csv` or `alternatives.csv` yet**.
- **Three different prices per plant** are in circulation (see §5, objection 4).
- The Sources page still shows the old Tillman numbers ($73k cut + $130k holdback); the model now gives a $429k cut.

## 2. What is missing for a complete platform
The image reading works. A platform also needs a way **in** for messy data, a way for a person to **correct** it, a way **out** for results, and a way to **stay current**.

| Gap | Why a judge cares | Fix | When |
|---|---|---|---|
| **Review queue** | We say "a person reviews low-confidence readings" and show no screen for it | A page listing flagged parts: photo, reading, reason, confirm / correct, who and when | **Tonight** (read-only is enough) |
| **Data ladder + reconciliation** | "Real plants have bad data" | A rung badge per plant, and three counts: on the list but not found, found but not on the list, same spare under two names | **Badge tonight**; full in Phase 1 |
| **Report out** | Appraisers, CapEx committees and deal teams work from a document | PDF / CSV of findings with an evidence column | Phase 1 (CSV tonight only if ahead) |
| **Equipment-list import** | Plants export from maintenance systems, with their own column names | CSV upload with column mapping; later direct connections | Phase 1–2 |
| **Staying current** | A registry that is only right on scan day is a report, not a system of record | Lifecycle alerts, rescans, sync with the maintenance system, then condition sensing | Phase 2, then expansion |
| **Knowledge-base growth** | 30 parts will not cover a real plant | AI drafts an entry with a source link; a person approves; every scan adds parts | Phase 1–2 |
| **Live sourcing + spare transfers** | 42 listings were collected by hand | Official marketplace and distributor APIs; a transfer request between plants | Phase 3 |
| **Logins and data separation** | A fund sees several companies; each owns its data | Accounts, roles, per-company separation, audit log | Phase 2 |

## 3. Plants with very bad data
**Position: bad data is the reason to buy, not a blocker.** The photo is the ground truth, so we do not depend on the plant's records. We measure how wrong they are.

1. **Start at rung 0.** Photos alone give a registry of critical parts, their lifecycle status and a wide CapEx range. See the ladder in the [index](index.md).
2. **Ranges widen honestly.** Missing date code → age from the machine's year built. Missing machine year → range by machine type (the model already does this for whole machines in `valuation.machine_capex`). Less data means a wider range, never a made-up point.
3. **Reconciliation is an output.** "Your list has 40 machines; we found 46, and 5 on the list are not on the floor." That number is a finding the plant can act on.
4. **Unknown parts are sorted, not hidden.** 16 of our 17 flags are "no KB match". Split them on screen into *commodity part, no risk* and *unknown, needs a person*.
5. **Every correction teaches the knowledge base.** A confirmed reading becomes a labeled example and, where new, a KB entry.

**What we have not proven:** accuracy on worn, painted-over or glare-covered real plates. Say so, and make it the first pilot measurement.

## 4. Supporting software and tools
Keep the stack. Add only what each phase needs.

| Need | Demo today | Product (Phase 1–3) |
|---|---|---|
| App and API | Next.js + FastAPI | Same |
| Database | SQLite file | Postgres, one schema per company |
| Photos | Files in the repo | Object storage with access control |
| Reading photos | Claude vision, cached | Same, run as batch jobs with a queue; retake prompt for blur and glare |
| Field capture | Web upload | Installable web app that works offline on a site walk |
| Equipment lists | Seed CSVs | CSV mapping, then SAP PM, IBM Maximo, Fiix, Limble, UpKeep |
| Storeroom stock | Seed CSVs | SAP MM, Oracle, NetSuite exports |
| Lifecycle status | 30 curated entries with source links | Rockwell and Siemens lifecycle data ⚠️ check access terms; AI-drafted entries with human approval |
| Outside offers | 42 hand-collected listings | eBay Browse API, Nexar / Octopart; partner feeds from refurbishers ⚠️ agreements needed |
| Accounts | None | Single sign-on, roles, audit log |
| Reports | None | PDF and CSV with evidence |
| Condition sensing | None | Off-the-shelf thermal cameras first (see §6) |

## 5. Major objections and how we answer them
| # | Objection | Answer | What backs it today | Gap to close |
|---|---|---|---|---|
| 1 | "Plants have terrible data." | We start from photos. Bad records are what we find and fix. | Duplicate spares and cross-plant matches found under different names | Rung badge + reconciliation counts on screen |
| 2 | "Anyone can ask an AI what a machine is." | Reading is step one. The value is the registry, lifecycle knowledge base, money model and cross-plant view. | The whole app after the scan | None; say it in one line |
| 3 | "Does it work on real, worn nameplates?" | Measured 127 / 129 on rendered labels; low-confidence readings go to a person; real-plate accuracy is the first pilot test. | Accuracy route, answer key | Review queue screen; keep the "rendered" label visible |
| 4 | "Your numbers are small / don't agree." | The demo plants are the smallest size band and only control parts are counted. Downtime avoided is not counted. | Money model with sources | **Pick one price and one ARR**: model base is **$5.9k / plant → $7.6M ARR at 5%**; the roadmap says $10–25k → $13–32M; the Sources page says ~$10k (Toledo) |
| 5 | "Rockwell and Siemens already audit their installed base." | They audit their own brand, once. We are multi-brand, from the panel, kept current, across plants. | Mixed-brand KB | Competition slide |
| 6 | "A registry goes stale." | Lifecycle alerts, rescans, maintenance-system sync, then condition sensing. | Roadmap only | Show the data ladder slide |
| 7 | "Health by age is a guess." | Correct, and we show it as a range. Condition sensing replaces age with measurement where it matters. | Ranges everywhere | Thermal research (§6) |
| 8 | "Sensors are a crowded, hard business." | We do not start with hardware. The registry tells you **where** a sensor pays: line stoppers with no spare. Off-the-shelf cameras first. | Line-stopper ranking | Asher's research |
| 9 | "Why would companies share spares?" | Inside one company it is the same owner. Across a fund's companies it is a priced transfer the fund can encourage. | Fort Wayne → Toledo, Lima → Waukesha in the demo | Data-ownership rule (each company owns its data; the fund sees totals) |
| 10 | "Marketplace parts are counterfeit; scraping breaks terms." | Official APIs and partners only; trust score; low-trust listings kept out of the price; a person approves purchases. | `n_low_trust`, `authorized` flag | None |
| 11 | "In a deal you are an extra cost." | Agreed. Own plants are the business; a deal is one way in. | Market model | None |

## 6. Expansion: clip-on thermal camera / sensor (Asher's research, in progress)
**Framing until the research lands** (everything below is a hypothesis ⚠️):
- **Why heat:** failing drives, power supplies and loose connections usually run hot before they stop. Thermal inspection of electrical cabinets is already standard maintenance practice ⚠️ cite a source before it goes on a slide.
- **Where it fits:** rung 4 of the data ladder. It turns "Replace soon, by age" into "Replace soon, measured".
- **Why us:** the registry already ranks which cabinets matter (line stopper, discontinued, no spare anywhere). A plant needs a handful of sensors, not hundreds.
- **How to start:** a phone-attached or handheld thermal camera on the same site walk as the photos. A fixed clip-on unit comes later. No own hardware at first.
- **What it changes in the money model:** downtime avoided becomes a counted number (the roadmap already says Phase 5 is when that happens).

**Questions for Asher's research to answer:**
1. Which failure modes of drives, PLC power supplies and contactors show up as heat, and how early?
2. Can a cabinet be read with the door closed (window, internal mount), given arc-flash rules?
3. Off-the-shelf devices and price per point; who already sells this, and to whom?
4. One periodic walk with a handheld camera vs a fixed sensor: what does each catch?
5. What is the smallest thing we could show: one thermal image attached to a part's evidence page?

## 7. Proposed edits to the roadmap doc (for both of us to agree)
- Add the **data ladder** under "How the system works".
- Phase 1: add **review queue, reconciliation, report export, list import**.
- Phase 2: add **accounts and data separation, KB growth with human approval**.
- Split the phase table into **Roadmap (0–3, committed)** and **Expansion vision (4–5+)**, as in [02-roadmap-vs-expansion.html](02-roadmap-vs-expansion.html).
- Phase 5: rename to **Condition sensing**, starting with thermal.
- Market row: replace "$10–25k / plant" with whichever price we pick in objection 4.
