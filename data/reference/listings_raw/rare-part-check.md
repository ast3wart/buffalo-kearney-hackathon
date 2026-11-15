# Rare-part check (5–10 min): which candidate has 0–2 listings?

**Goal:** find one real, genuinely scarce controller for the "no listings → alternatives" path. Asher adds the winner to the KB (with its lifecycle source) and puts it in a Tillman (Rockford) machine. **0–2 listings = pass. 3+ = fail.**

## Candidates (Asher's list)
| # | Part | Search these strings |
|---|---|---|
| 1 | Westinghouse **Numa-Logic PC-1100** CPU | `Numa-Logic PC-1100` · `Numalogic PC1100` · `Westinghouse PC-1100` |
| 2 | Square D **SY/MAX Model 400** processor | `SY/MAX 400` · `SYMAX 400` · `8020 SCP-4` |
| 3 | Texas Instruments **5TI-1000 / TI 520** CPU | `5TI-1000` · `5TI1000` · `TI 520 PLC` |
| 4 | Reliance Electric **AutoMax DCS 5000** processor | `AutoMax 57C4` · `57C430` · `57C435` · `DCS 5000 processor` |

## Steps per candidate
1. **eBay active:** `https://www.ebay.com/sch/i.html?_nkw=<search string>` → count exact-match listings (skip manuals, cables, I/O cards, "for parts" lots).
2. **eBay sold:** same URL + `&LH_Sold=1&LH_Complete=1` → count exact matches.
3. **Radwell:** search box at https://www.radwell.com → note "in stock / request a quote / not found".
4. Fill the table below. Screenshot each results page → `images/rare-<n>-ebay.png`, `images/rare-<n>-radwell.png`.
5. Stop at the first candidate with **0–2 total** across eBay active + sold + Radwell priced. If two pass, pick the one with a clear model number (easier to show on a nameplate).

## Results
| # | eBay active | eBay sold | Radwell | Total | Pass? | Notes / URLs |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | not found | **0** | ✅ | eBay active + sold: 0 exact matches; Radwell search: not found (2026-11-14) |
| 2 | – | – | – | – | not checked | stopped at first pass |
| 3 | – | – | not found | – | not checked on eBay | |
| 4 | – | – | listed (57C431A, under ABB / Baldor Reliance) | ≥ 1 | ❌ | AutoMax family still traded |

**Winner: #1 Westinghouse Numa-Logic PC-1100** (0 listings) → tell Asher (to-asher.md or chat): part number, total listings found, and paste any URLs. If **none** pass, say so; the fallback is to keep the alternatives path on a part with "low" confidence (1–2 listings) and label it.
