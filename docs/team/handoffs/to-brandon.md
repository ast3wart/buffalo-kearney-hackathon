# Inbox: to Brandon

**Written by Asher, read by Brandon.** Newest on top. Brandon: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, ~5 PM · DECIDED: own-plant evaluation is the main way in; acquisition is just one way in
**Status:** 🆕 new
- **The decision (Asher):**
  1. **The main way in is a manufacturer evaluating its own plants.** No deal needed.
  2. **An acquisition is *a* way in, not *the* way in.** The diligence market (~670 reviewed deals a year, ≤ ~$10M) is too small to rely on.
  3. **The target customer is multi-plant manufacturers *and* PE portfolios**, not PE first.

  This matches `docs/plan/roadmap-equipment-xray.md`.
- **What to update in your pivot-plan docs (your thread):**
  - **index.md, decision 1:** "Diligence is the entry point" → "**Own-plant evaluation is the main entry point; diligence is one of several.**"
  - **03-flywheel-growth.md:**
    - Add an **"own-plant assessment"** row as the main *Land* motion: VP Ops / plant manager, per-plant fee, no deal. Keep the diligence add-on as a second *Land* row.
    - Retitle "Why PE is the right first customer" to **"Why multi-plant manufacturers and PE"**: multi-plant manufacturers have the same mess (mixed brands, separate storerooms) without needing a deal.
    - Start the flywheel with "plant scan (own plant *or* acquisition)".
  - **05-poc-scope.md demo script:**
    - Open with ownership: "**Fund X owns Plant A and Plant B**…"
    - Then show the registry → CapEx cliff → evidence → single point of failure → **Plant B spare** → accuracy → live photo.
    - End with "**and when they buy their next plant, the same scan prices the deal**" (pay $X less as the second lens).
  - **04 deck map + mockup, numbers:**
    - The diligence wedge is **~$10M ceiling** (~670 reviewed deals × $15k, `docs/research/deep-dive-numbers.md`), not $3M (that was the Axial listings model).
    - Add the **own-plant number**: **25,799 US plants with 100+ employees** (Census 2022) → **$13–32M ARR at 5% adoption**, with a $258–645M ceiling.
    - Pick **one deal add-on price** ($10–20k fits the consulting breakeven; "low thousands" doesn't).
  - **Slide 5 (Customer):** the trigger is "plant risk / CapEx planning *or* an acquisition", not only an acquisition.

### Sat Nov 14, ~4:45 PM · Merged your pivot plan (#13) + adopted your schema; one change to the split
**Status:** 🆕 new · PR #12
- **Merged:** #11 (research) → your #13 (pivot plan) → #12 (roles + registry format).
- **Adopted from your plan:** the **2-plant portfolio** (for the Plant B spare moment), **SQLite + seed files**, and your schema (`fund`, `spare_stock`, ranges, `lead_time_wks`, `authorized`). It's all in `docs/build/registry-format.md`, with each column tagged by owner.
- **Changed: the split.** Your doc 05 split was written before we split the work by strength. **Asher (CS + stats) takes data, vision, matching, accuracy and the app. You (finance + accounting) take valuation (`xray/valuation.py`), the cost columns, sourcing (`xray/sourcing.py`), the estimates and the pitch numbers.** I put a note on doc 05. See `docs/team/roles.md`.
- **For you to settle (money thread):** your doc 03 prices the deal add-on at "low thousands", but the deep dive's consulting breakeven assumes a **$10–20k** module (`docs/research/deep-dive-numbers.md`). Pick one number for the deck.
- **What you need to do now (CP0):** sign off on `registry-format.md`, especially the 💲 columns and outputs.

### Sat Nov 14, ~4 PM · Roles for Equipment X-Ray + registry format to sign off (CP0)
**Status:** 🆕 new · branch `plan/roles-and-registry`
- **Roles** (`docs/team/roles.md`): you take **💲 the money thread**:
  - `xray/valuation.py`: CapEx cliff, "pay $X less" / holdback, deferred CapEx as a hidden liability
  - the cost columns in the knowledge base and lines
  - sourcing offers + the buy / migrate / monitor rule (`xray/sourcing.py`)
  - refining the estimates with Velocity
  - pitch numbers + judge Q&A

  I take **🛠 the machine thread**: fake factory + answer key, knowledge base identity/lifecycle, vision extraction, accuracy, the app, and the live photo demo.
- **Checkpoints:** CP0 ~4:30 (format), CP1 ~7:30 (slices work alone), CP2 ~10:30 (end to end), CP3 ~1 AM (freeze), CP4 ~7 AM (rehearse). Submit by 8:30.
- **What you need to do now:** read `docs/build/registry-format.md` (draft), especially the 💲 columns and the outputs you'd produce, and edit anything you'd model differently (e.g. how the holdback is computed). Then we mark it ✅ agreed.
- **Context for your numbers:** `docs/research/deep-dive-numbers.md` + `scripts/market_model.py` (PR #11).

### Sat Nov 14, afternoon · `main` cleaned up for Equipment X-Ray
**Status:** 🆕 new
- **What changed:** Afterlife-only code, data and docs are gone from `main`. These reusable pieces stay:
  - **`xray/matching.py`**: normalize + fuzzy matching, generalized from `match_spend`, for matching nameplate text to the knowledge base
  - **`xray/evaluate.py`**: precision/recall against an answer key
  - the FastAPI and Next.js shells, CI, and `checkpoint.sh`

  The README and AGENTS.md now describe Equipment X-Ray. Nothing is lost: everything is in the tag `archive/afterlife-main`, and the old branches are in `archive/*` tags.
- **What you need to do:** `git checkout main && git pull && git fetch --prune --tags`. If you have unpushed local Afterlife work, push it to a branch first.

### Sat Nov 14, ~11:45 AM · 🔄 PROPOSED PIVOT after the judge review: please read and decide
**Status:** 🆕 new
- **What the judge said:**
  - our scope is too wide
  - half the room is doing "consultancy efficiency"
  - nobody is on the Startup track
  - old, acquisition-heavy companies have the biggest holes
- **The proposal:** pivot to **Equipment X-Ray**, pre-deal equipment diligence on the Startup track. It gives a CapEx cliff, "pay $X less", and the single points of failure from discontinued components.
- **Where:** `docs/plan/idea-equipment-xray.md`
- **What you need to do:** answer §13: yes, no or modify, how we split the work, and anything the judge said that it misses.
- **Update ~12:30 PM:** a mentor liked it and said keep digging. They want a **roadmap and a clear MVP plan, not a full build**, with **parts sourcing** as a key feature and a **PE portfolio** angle. See `docs/plan/roadmap-equipment-xray.md`.

*Older Afterlife entries are in the tag `archive/afterlife-main`.*
