# Price sensitivity (Sat Nov 14)

What a plant would pay per year at 10 / 20 / 30% value capture, across low / base / high savings. Rerun: `python scripts/sensitivity.py`.
Data: Asher's 6-plant demo registry (`demo.db`, 5 owned plants), quoted as a **full-plant scan extrapolated from the register sample** (`plant_savings(full_plant=True)`).
Every input is a labeled range in `xray/params.py`; gross margin uses cost to serve $910 per plant (Velocity #18). **Model output on synthetic plants with real part prices.**

## Portfolio average (5 owned plants): price / payback / gross margin

| Capture % | low savings | base savings | high savings |
|---|---|---|---|
| 10% | $2.1k / 1.2 mo / 56% | $5.7k / 1.2 mo / 84% | $16.1k / 1.2 mo / 94% (quick-yes) |
| 20% | $4.1k / 2.4 mo / 78% | $11.5k / 2.4 mo / 92% (quick-yes) | $32.2k / 2.4 mo / 97% |
| 30% | $6.2k / 3.6 mo / 85% | $17.2k / 3.6 mo / 95% (quick-yes) | $48.3k / 3.6 mo / 98% |

Price = capture % x auditable recurring savings, so payback is fixed by the capture % (capture x 12 months) and ROI is 1 / capture (10x / 5x / 3.3x). What moves is the dollar price and the margin. Quick-yes = inside the $10–25k plant-manager approval zone (Velocity #19).

## Per plant at 20% capture

| Plant | Recurring savings (base) | Price low / base / high | Payback | ROI | Gross margin | Quick-yes ($10-25k) |
|---|---|---|---|---|---|---|
| PA | $95.7k | $6.8k / $19.1k / $53.5k | 2.4 mo | 5.0x | 95% | yes |
| PB | $60.6k | $4.9k / $12.1k / $30.2k | 2.4 mo | 5.0x | 92% | yes |
| PC | $49.9k | $3.6k / $10.0k / $28.2k | 2.4 mo | 5.0x | 91% | no |
| PD | $44.3k | $3.2k / $8.9k / $25.9k | 2.4 mo | 5.0x | 90% | no |
| PF | $36.4k | $2.3k / $7.3k / $23.4k | 2.4 mo | 5.0x | 88% | no |
| **Average** | $57.4k | $4.1k / $11.5k / $32.2k | 2.4 mo | 5.0x | 92% | yes |

Stress: list at the base price ($11.5k) and only low-case savings show up ($20.7k/yr): payback 6.6 months.

## One-time spares release (cash freed once, not priced)

| Plant | Low | Base | High |
|---|---|---|---|
| PA | $180.0k | $300.0k | $550.0k |
| PB | $140.0k | $232.5k | $425.0k |
| PC | $100.0k | $165.0k | $300.0k |
| PD | $90.0k | $150.0k | $275.0k |
| PF | $60.0k | $105.0k | $200.0k |

## What moves the price
- **Carrying cost on excess spares is two-thirds of recurring savings** (66% of base). It scales with the plant's spares inventory and the excess share (10–25%), so plant size drives price: PA is 2.6x PF.
- **Planned vs emergency replacement is the widest lever** ($0.5k–$53k per plant): it depends on failure rates of aging parts and the emergency multiplier, so it is most of the gap between the base and high cases.
- **Rush premiums avoided add 13%**; sister-plant spares only 4% in recurring dollars, though they're the most auditable lever (PO + transfer).
- Downtime avoided and the one-time spares release are shown, never priced.

## Recurring savings by lever (portfolio average, base)

| Lever | Low | Base | High | Share of base |
|---|---|---|---|---|
| carrying_cost_avoided | $17.1k | $38.1k | $87.5k | 66% |
| planned_vs_emergency | $0.5k | $9.5k | $52.9k | 17% |
| rush_premiums_avoided | $2.6k | $7.7k | $15.3k | 13% |
| sister_spare_purchases_avoided | $0.5k | $2.1k | $5.4k | 4% |

## For the slide
**List $10–20k per plant per year (portfolio base $11.5k); 20% value capture; payback under 3 months, under 7 even if only low-case savings show up.** Plus a one-time $105–300k spares release (base) the customer keeps.
