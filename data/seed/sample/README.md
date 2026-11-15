# Sample portfolio (hand-made stand-in)

Small slice of Asher's `data/seed/demo/` (branch `asher/demo-data`), same columns and IDs, so Brandon's `sourcing.py` / `valuation.py` / `pricing.py` tests run before the full demo merges. Delete or keep as a test fixture once `demo/` lands.

| Plant | Company | Role in the sample |
|---|---|---|
| **PA Toledo** | Halvorsen (Stone Rose Capital) | Line 2 Aida servo press runs on a discontinued **Kinetix 6000** (KB-009), no spare at Toledo → line-stopping single point of failure. Compressor on Line 1 has a **CompactLogix 1769-L32E** (KB-002) + **PowerFlex 40** (KB-006). Storeroom holds the PowerFlex 40 twice under two names (duplicate). |
| **PB Fort Wayne** | Halvorsen | Shelf row `PB-S001` "SERVO DRV KIN6K IAM 460V 6KW" ×2 = the Kinetix 6000 Toledo needs (the portfolio moment). Also a PowerFlex 525 (the PF40 successor). |
| **PE Rockford** | Tillman (acquisition **target**, deal $28–34M) | Two Okuma lathes on **Siemens S5 CPU 943** (KB-029, the no/few-listings path). Has Kinetix 6000 spares, but it isn't owned yet, so `recommend_sourcing` must **not** use them. Use it to test `deal_adjustment`. |

- 3 plants, 5 lines, 8 machines, 11 components, 5 shelf rows, 10 KB parts.
- `reference/kb.csv` and `reference/alternatives.csv` are copies of Asher's rows (the real files live in `data/reference/` on his branch).
- Answer key: `data/truth/sample/`. Money columns are the placeholder ranges from `interfaces.md` §2.
- Listings (real, by hand): `data/reference/listings.csv`, worksheets in `data/reference/listings_raw/`.
