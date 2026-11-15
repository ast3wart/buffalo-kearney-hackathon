# Inbox: to Asher

**Written by Brandon, read by Asher.** Newest on top. Asher: update the **Status** line as you go (🆕 new → 👀 reviewing → ✅ done). How this works: [README.md](README.md).

### Sat Nov 14, late · Money model is in (PR `brandon/money-model`) + PROPOSED contract additions (additive only, nothing renamed)
**Status:** 🆕 new · `xray/params.py`, `sourcing.py`, `valuation.py`, `pricing.py`, `tests/test_money_model.py`. Smoke-tested on your `demo.db` too (seeded from `asher/demo-data`): runs, no code changes needed on your side.
- **Proposed: extra columns after the §7 ones** (the §7 columns are unchanged and come first):
  - `part_valuation` + `n_low_trust` (listings with trust_score < 0.35: flagged, kept out of the price range)
  - `sourcing_recommendation` + `plant_id, kb_id, spare_plant_id, transfer_cost_low/high, part_value_low/high`
  - `spof` + `plant_id, kb_id, action, annual_failure_rate_low/high, downtime_cost_per_hour_low/high` (`annual_failure_rate` = base)
  - `plant_savings` + `basis` (one-line formula text); `price` + `price_per_plant_base, recurring_savings_base`
- **Proposed: optional kwargs on the §1 signatures** (the documented calls still work): `capex_by_year(..., sourcing_recommendation=None, growth=None)`, `deal_adjustment(reg, capex_by_year, company_id=None, discount_rate=None)` (None → every target company), `plant_savings(reg, sourcing_recommendation, part_valuation=None, spof_table=None)`. Price check 4 (deal fee) is per company: `pricing.deal_fee_check(deal_adjustment, deal_fee)`.
- **Zero-listing part in the sample is KB-003** (MicroLogix 1764-LSP → `migrate`), not KB-029.

### Sat Nov 14, ~8:15 PM · Listings are in (42 real, 6 parts) + the S5 isn't a "no listings" part
**Status:** 🆕 new · branch `brandon/sample-data`
- **`data/reference/listings.csv`**: 42 hand-collected listings (eBay sold, Radwell, DO Supply), 2026-11-14, all `authorized = no`. Parts: KB-009 Kinetix 6000, KB-006 PowerFlex 40, KB-002 CompactLogix L32E, KB-029 S5 CPU 943, plus the successors **KB-022** (2198-D006-ERS3) and **KB-019** (25B-D010N104). Raw page text + screenshots: `data/reference/listings_raw/`. 3 bundles excluded; one "for parts" Kinetix kept as `for_repair`.
- **⚠️ KB-029 (S5 CPU 943) has 7 listings** (Radwell has 64 refurbished in stock at ~$949). Per your note: **please pick a rarer part for the alternatives path** (or tell me which one and I'll check it has 0–2 listings). Until then the zero-listing case has no real part.
- **Demo line:** a refurbished Kinetix 6000 costs **$4.3–6.5k**, more than a new-surplus successor Kinetix 5700 (~$4.3k, + migration). Fort Wayne's 2 shelf spares ≈ $9–13k at refurbished prices.
- **`data/seed/sample/`**: my small stand-in (Toledo, Fort Wayne, Rockford target; rows copied from your `demo/`, same IDs). Copies of your KB/alternatives rows sit in `data/seed/sample/reference/` so nothing collides with your `data/reference/kb.csv`. Answer key in `data/truth/sample/`.
- **Next from me:** `xray/sourcing.py`, `valuation.py`, `pricing.py` on the sample, then on your `demo.db` once `asher/demo-data` merges. `recommend_sourcing` checks every **owned** plant's shelf and skips `status = target` plants (Rockford's Kinetix spares don't count until it's bought).

*(Older Afterlife entries are in the tag `archive/afterlife-main`.)*
