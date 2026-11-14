# Handoffs: how we pass work to each other

We build in parallel and hand work across through **two inboxes**. Each file is written by only one person, so they never conflict when both of us push branches at the same time.

| File | Written by | Read by |
|---|---|---|
| [to-brandon.md](to-brandon.md) | 💲 Asher | 🛠 Brandon |
| [to-asher.md](to-asher.md) | 🛠 Brandon | 💲 Asher |

**Rules**
- Write an entry when you hand something over, or when you change something the other person depends on (data contract, shared code, API shapes).
- **Only edit the other person's inbox.** The reader may change an entry's **Status** line (🆕 new → 👀 reviewing → ✅ done), nothing else.
- Newest entry at the top. Short. Always link the PR.
- **The PR** says *what to review and merge*. **The inbox entry** says *what changed for you and what you need to do*.
- Check your own inbox at every checkpoint (`docs/team/checkpoints.md`).

## Template
```
### <date, time> · <what>
**Status:** 🆕 new · PR #<n>
- What's ready / what changed:
- Where (files, branch, command):
- What you need to do:
- Known issues:
```

## Planned handoffs
| When | From → To | What |
|---|---|---|
| Fri night | both | Data contract agreed (`docs/build/data-contract.md`) ✅ |
| Fri night | both | API contract agreed (`docs/build/api.md`), app layout committed ✅ |
| Sat ~11:30 (CP2) | 💲 Asher → 🛠 Brandon | `generate_spend` output, so the claims generator can use the real BOM ✅ (early, PR #3) |
| Sat ~6 PM | both | Full `afterlife.run` on generated data, both screens live, accuracy numbers |
| Sat ~10 PM | 💲 Asher → 🛠 Brandon | Deck draft for review |

## History (before the inboxes)
### Fri Nov 13 · both · CP0 contract lock
- What changed: data contract v2 (part_no + price_unit on spend, info_records, dataset_info, 12 SYSTEM-MODE failure codes, 21 categories). **Three companies** in `data/generated/<company_id>/`. API takes `?company=`.
- Where: `docs/build/data-contract.md`, `docs/build/api.md`, `afterlife/taxonomy.py`, `afterlife/profiles.py`, `afterlife/check.py`
- What you need: generators take a `profile` argument. Run `python -m afterlife.check` before pushing.
