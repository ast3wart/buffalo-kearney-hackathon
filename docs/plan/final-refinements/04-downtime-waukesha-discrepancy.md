# 4 · Downtime rework: the Waukesha numbers in the report do not reproduce

[← index](index.md)

**Status:** OPEN, Sat Nov 14, ~11:30 PM. **Do not quote the Waukesha or portfolio downtime figures until this is closed.** Toledo's numbers match and are safe to use.

## What happened
The downtime number was rebuilt on `brandon/downtime-horizon` (no whole-plant scale-up, one failure per spare over 3 years, outage capped at 10–25 operating days, 40–80% of lost output counted). The report written with that work quoted figures that a clean rebuild of the demo database does not give.

**How I checked:** on that branch, `python scripts/seed.py data/seed/demo demo.db`, then the `/plants/{id}/savings` and `/plants/{id}/spof` routes for the 5 owned plants. 29 tests pass.

| | Report | Clean rebuild | Match |
|---|---|---|---|
| Toledo (PA) downtime avoided | $18k / yr | $18.7k / yr | ✅ |
| Waukesha (PD) downtime avoided | $22k / yr, 2 rescues | **$3.8k / yr, 1 rescue** | ❌ |
| Portfolio downtime avoided | $61k / yr ($9k–205k) | **$51k / yr ($8k–175k)** | ❌ |
| Line-stopper exposure, 5 plants | $80k–1.5M / yr | **$71k–1.18M / yr** | ❌ |
| Waukesha Line 2 example (PD-L2-M02-C2, spare PF-S001, $198k at stake, 22% in 3 yrs) | shown | **not in the rebuild** | ❌ |

Per plant in the clean rebuild (base, per year): Toledo $18.7k (4 rescues) · Fort Wayne $8.1k (2) · Lima $2.2k (1) · Waukesha $3.8k (1) · Oshkosh $18.5k (4).

## What the data says about the Waukesha example
- `PD-L2-M02-C2` is **KB-012** (Siemens MICROMASTER 440, `6SE6440-2UD24-0BA1`, discontinued).
- `PF-S001` is **KB-025** (SINAMICS G120C). It is a different part, not the same catalog number.
- In the clean rebuild, sourcing says for `PD-L2-M02-C2`: "no shelf spare it can use", action `buy_spare`. So there is no rescue and no downtime avoided for it.
- Waukesha's one rescue is `PD-L1-M01-C3`, also KB-012, covered by Lima's `PC-S001`.

## Likely causes (not confirmed)
1. The report's numbers came from a database that was not built from the seed files in the repo (the report itself says the checked-in `demo.db` was out of date and showed a different rescue count).
2. Somewhere a **successor part was treated as a usable spare** (G120C standing in for a MICROMASTER 440). That is a migration, not a swap: it needs engineering time, so it should not count as an 18–40 hour rescue.

## To close this
- [ ] Whoever produced the report: say which database and command gave $22k / $61k, and rerun on a clean rebuild.
- [ ] Decide the rule: **does a successor on a sister plant's shelf count as a rescue?** Recommended: no, or only with the migration hours added.
- [ ] Check that a spare with quantity 1 is not counted for two parts (Lima's `PC-S009`, quantity 2, covers two Toledo parts, which is fine).
- [ ] Rebuild `demo.db` on the demo laptop before rehearsal, so the app shows the same numbers as the deck.

## What the deck and app use meanwhile
Only figures that reproduce:
- **One event (deck slide 4, Sources page):** Toledo Line 2 servo drive `PA-L2-M01-C1`: 48–176 h down without a spare, 18–40 h with Fort Wayne's `PB-S001`; ~$84k at stake ($5–249k); ~17% chance within 3 years.
- **Toledo downtime avoided (deck slide 8, A4, Sources page):** ~$19k a year ($2–71k), shown, never priced.
- No portfolio-wide or Waukesha downtime figure appears in the deck.
