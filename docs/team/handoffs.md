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
### Fri Nov 13 · both · CP0 contract lock
- What changed: data contract v2 (part_no + price_unit on spend, info_records, dataset_info, 12 SYSTEM-MODE failure codes, 21 categories). **Three companies** in `data/generated/<company_id>/`. API takes `?company=`.
- Where: `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/check.py`
- What you need: generators take a `profile` argument. Run `python -m afterlife.check` before pushing.
