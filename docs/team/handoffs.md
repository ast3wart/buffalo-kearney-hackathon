# Handoffs

Use this when you hand something to the other person or change something they depend on. Newest entries go at the top. Keep each one short.

## Template
```
### <time> · <from> → <to> · <what>
- What changed / what's ready:
- Where it is (file, branch, command):
- What you need from them:
- Known issues:
```

## Planned handoffs
| When | From → To | What |
|---|---|---|
| Fri night | both | Data contract agreed (`docs/build/data-contract.md`) |
| Fri night | both | API contract agreed (`docs/build/api.md`), app layout committed |
| Sat ~12:30 | 💲 Asher → 🛠 Brandon | `generate_spend` output (bom, builds) so the claims generator can use the real BOM |
| Sat ~6 PM | both | Full `afterlife.run` on generated data, both screens live, accuracy numbers |
| Sat ~10 PM | 💲 Asher → 🛠 Brandon | Deck draft for review |

## Log
### Sat Nov 14, early AM · Asher → Brandon · Data contract v3 (from your CP0 review)
- What changed: merged your `plan/cp0-additions` into `test-data-batch`, then applied #10–15, #17, and the #19 schema. New tables: `build_supply.csv`, `abbreviations.csv`. `truth_spikes.from_po_line_id`, links v2 columns, `runs` table, SAP adapter. Northwind has HVAC codes and categories (24 categories, 16 failure codes in the union).
- Where: `docs/build/data-contract.md` (v3 section + SAP table), `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/adapters/sap.py`, `afterlife/check.py`, `scripts/make_sample.py`, `tests/`
- What you need: `git checkout test-data-batch && git pull`. Your sample now has a dual-sourced seal kit (Keystone S-022 / Bluewater S-023) with the spike only on Keystone's April lot `PO-450005-010`, so build `detect.py` against that. Please confirm or push back at CP1.
- Known issues: none. `./scripts/checkpoint.sh` is green, 7 tests pass.

### Fri Nov 13 · both · CP0 contract lock
- What changed: data contract v2 (part_no + price_unit on spend, info_records, dataset_info, 12 SYSTEM-MODE failure codes, 21 categories). **Three companies** in `data/generated/<company_id>/`. API takes `?company=`.
- Where: `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/check.py`
- What you need: generators take a `profile` argument. Run `python -m afterlife.check` before pushing.
