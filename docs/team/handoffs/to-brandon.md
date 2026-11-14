# Inbox: to Brandon

**Written by Asher, read by Brandon.** Newest on top. Brandon: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

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
