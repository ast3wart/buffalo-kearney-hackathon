# Checkpoints: when we stop, review each other, and resync

Each checkpoint sits where a **dependency changes hands** or a **decision has to be made**, so a pause never wastes time.
Every one starts the same way: **merge to main → both run `./scripts/checkpoint.sh` → only then look at features.** If the script is red, fixing it *is* the checkpoint.

🛠 = Brandon (Warranty) · 💲 = Asher (Spend)

| # | When | Length | Why here |
|---|---|---|---|
| 0 | **Fri ~11:30 PM** | 45 min | Lock the contracts before anyone builds on them |
| 1 | **Sat 9:00 AM** | 15 min | Morning resync after overnight solo work |
| 2 | **Sat ~11:30 AM** | 30 min | 💲 hands the generated BOM/builds to 🛠 |
| 3 | **Sat 12:30 PM** (lunch) | 30 min | Integration #1: first full run, first accuracy numbers |
| 4 | **Sat ~3:30 PM** | 30 min | Screens + claims generator on the real BOM. Last cheap chance to change direction |
| 5 | **Sat 6:00 PM** (before dinner) | 45 min | Integration #2: the numbers become the story. Go/no-go on stretch |
| 6 | **Sat 9:30 PM** | 30 min | Demo walkthrough in click order, then freeze at 10 |
| 7 | **Sat ~11:30 PM** | 45 min | Pitch dry run #1 + deck swap review |
| 8 | **Sun 7:00 AM** | 60 min | Fresh-clone test, dry run #2, submit by 8:30 |

> Running behind? A checkpoint can slide **30 min at most**. Never skip #3, #5, or #8.

---

## CP0 · Contract lock (Fri ~11:30 PM, 45 min)
**Why:** the data contract and API contract are what let us work apart. Changing them later costs both of us.
**Start with [../research/cp0-proposal.md](../research/cp0-proposal.md)** (research-backed changes to accept or reject).
- [ ] Both have the repo running: `./scripts/checkpoint.sh` is green on both laptops
- [ ] Walk through `docs/build/data-contract.md` table by table. Each owner says "I can produce/consume this"
- [ ] 💲 confirms the claims side needs nothing more from spend than `bom`, `builds`, `part_master`, `products`
- [ ] 🛠 confirms `failure_codes.likely_categories` will use 💲's `part_master.category` values. **Agree the category list now**
- [ ] Walk through `docs/build/api.md`: response shapes for `/overview` and `/alerts` (rough is fine)
- [ ] App layout + style: colors, font, a nav with 4 routes, one shared `<Card>` / `<Stat>` component. One person commits it tonight
- [ ] Branch names agreed (`spend/...`, `warranty/...`)

**Exit:** contracts committed, layout committed, each person knows their first task.

## CP1 · Morning resync + confirm contract v3 (Sat 9:00 AM, 30 min)
- [ ] Brandon confirms or pushes back on **data contract v3** (`docs/plan/plan-updates.md`, Update 4). Decide when `test-data-batch` merges to main. Pin the LLM model ID
- [ ] Each person: what's done, what's next, anything blocking (2 min each)
- [ ] Any contract changes overnight? If yes, read them out loud and check `docs/team/handoffs.md`
- [ ] Confirm the times for CP2 and CP3

**Exit:** today's targets restated.

## CP2 · Spend → Warranty handoff (Sat ~11:30 AM, or when `generate_spend` works, 30 min)
**Why:** 🛠's claims generator needs the real BOM. This is the only hard dependency between us.
- [ ] 💲 demos `python -m afterlife.generate` output (spend side). `afterlife.check` passes the spend tables
- [ ] 🛠 **reviews 💲's data:** are categories usable for failure codes? Is there a good **shared part** (used in ≥3 products, one supplier) to plant the spike on? Pick it together now
- [ ] 💲 **reviews 🛠's code:** `match_claims` on sample data. Does the candidate narrowing make sense? Any normalize() changes that affect spend matching too?
- [ ] Agree any `ABBREVIATIONS` additions (shared file)

**Exit:** spike part chosen, 🛠 can start `generate_claims` on real data.

## CP3 · Integration #1 (Sat 12:30 PM, lunch, 30 min)
**Why:** first time both halves run together. Problems found here are cheap.
- [ ] `./scripts/checkpoint.sh` on generated spend + sample/partial claims
- [ ] Both API endpoints (`/overview`, `/alerts`) return real data. Open `localhost:8000/docs` together
- [ ] First accuracy numbers from `afterlife.evaluate`, written down even if bad
- [ ] Each person reads the other's main function for 5 min: "would I understand this at 3 AM?"
- [ ] Decide: is anything off schedule? Cut or swap now, not at 9 PM

**Exit:** pipeline runs end to end on at least partly generated data.

## CP4 · Screens + direction check (Sat ~3:30 PM, 30 min)
**Why:** the last moment a change of direction is still cheap.
- [ ] Both screens open side by side: do they look like **one app**? (same components, colors, number formatting: `$1.2M`, `3.0×`)
- [ ] 🛠: spike visible in generated claims? Show the claim-rate chart
- [ ] 💲: markups and lifecycle cost visible? Do the $ figures look believable?
- [ ] Matching accuracy trend. **Remind each other: tuning stops at 5 PM**
- [ ] Who starts which shared piece next: Linking explorer, `POST /brief`, Brief screen

**Exit:** shared pieces assigned, any direction change agreed.

## CP5 · Integration #2: numbers become the story (Sat 6:00 PM, 45 min)
**Why:** after this, the numbers in the pitch shouldn't change.
- [ ] `./scripts/checkpoint.sh` fully green on **fully generated** data, with no warnings left that we can't explain
- [ ] Sanity on the story numbers, written into `docs/pitch/demo-script.md`:
  - [ ] % of spend linked, % of claims linked, precision and recall **per company**. Holdout companies within a few points of Prairie?
  - [ ] Warranty ≈ 2.5% of revenue (SEC benchmark)?
  - [ ] Spike caught in Prairie + Ironridge? **Zero alerts for Northwind** (the control)?
  - [ ] Build cost vs. lifecycle cost per product, spare-part markup range
  - [ ] Recovery $ + harmonization $ per supplier, and do the two halves of the brief **add up consistently**?
- [ ] **Go/no-go on stretch:** only if everything above is solid
- [ ] Freeze the generator seed (`--seed 7`) so numbers stop moving

**Exit:** numbers locked, stretch decided.

## CP6 · Demo walkthrough + freeze (Sat 9:30 PM, 30 min)
- [ ] Run the demo **in click order** from `docs/pitch/demo-script.md`, timed
- [ ] Each person tries to break the other's screen (empty states, slow API, long names)
- [ ] Brief generation works with **and** without an API key (template fallback)
- [ ] List what's left: bug fixes only. **Feature freeze at 10 PM**

**Exit:** demo runs start to finish, frozen.

## CP7 · Pitch dry run #1 (Sat ~11:30 PM, 45 min)
- [ ] Swap: 🛠 reviews 💲's slides, 💲 reviews 🛠's slides. One voice, same terms (glossary from the primer)
- [ ] Full timed run with handoffs between speakers
- [ ] Velocity evidence in the deck (screenshots from `docs/research/velocity.md`)
- [ ] Practice the 5 hardest judge questions from `docs/pitch/judge-qa.md` on each other
- [ ] Record the backup demo video (or first thing at CP8)

**Exit:** deck v1 done, both know their lines.

## CP8 · Final check + submit (Sun 7:00 AM, 60 min)
- [ ] **Fresh clone** into a new folder → follow README exactly → does it run?
- [ ] README has: problem, screenshot, accuracy numbers, how to run, Velocity usage
- [ ] Backup video recorded and linked
- [ ] Dry run #2, timed
- [ ] Repo visibility right for submission (public if required)
- [ ] **Submit by 8:30 AM.** Aim for 8:00

---

## Between checkpoints (lightweight)
- **Shared files need the other person's 👍 before merging:** `match.py`, `brief.py`, `io.py`, `check.py`, `api/main.py` models, both contract docs. A quick PR or a chat message is enough.
- **Anything that changes a contract** gets a line in `docs/team/handoffs.md` *and* `afterlife/check.py`'s `CONTRACT`, in the same commit.
- **Stuck for more than 20 min** → message the other person, don't wait for the next checkpoint.

## Notes log
_Write 2–3 lines after each checkpoint: decisions, numbers, cuts._

- CP0 (Fri Nov 13, done): **3 companies, not 1** (Prairie = tune, Ironridge + Northwind = holdout, Northwind = no-spike control). all research proposals accepted except claim line items and BOM uom. Spikes shown both ways, alerts use the MIS window (3). Window Jan 2025–Sep 2026, as of Oct 31 2026. Clean industrial style. See docs/research/cp0-proposal.md.
- CP1:
- CP2:
- CP3:
- CP4:
- CP5:
- CP6:
- CP7:
- CP8:
