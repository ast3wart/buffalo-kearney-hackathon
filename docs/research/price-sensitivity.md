# Price sensitivity (Sat Nov 14, ~10 PM: Velocity #1–3 plant finances + #16 migration costs)

What a plant would pay per year at 10 / 20 / 30% value capture, across low / base / high savings. Rerun: `python scripts/sensitivity.py`.
Data: Asher's 6-plant demo registry (`demo.db`, 5 owned plants), quoted as a **full-plant scan extrapolated from the register sample** (`plant_savings(full_plant=True)`).
Every input is a labeled range in `xray/params.py`; gross margin uses cost to serve $910 per plant (Velocity #18). **Model output on synthetic plants with real part prices.**

## Portfolio average (5 owned plants): price / payback / gross margin

| Capture % | low savings | base savings | high savings |
|---|---|---|---|
| 10% | $0.5k / 1.2 mo / -73% | $3.0k / 1.2 mo / 69% | $10.6k / 1.2 mo / 91% (quick-yes) |
| 20% | $1.1k / 2.4 mo / 14% | $5.9k / 2.4 mo / 85% | $21.2k / 2.4 mo / 96% (quick-yes) |
| 30% | $1.6k / 3.6 mo / 42% | $8.9k / 3.6 mo / 90% | $31.8k / 3.6 mo / 97% |

## Per plant at 20% capture

| Plant | Recurring savings (base) | Price low / base / high | Payback | ROI | Gross margin | Quick-yes ($10-25k) |
|---|---|---|---|---|---|---|
| PA | $47.7k | $1.8k / $9.5k / $32.9k | 2.4 mo | 5.0x | 90% | no |
| PB | $29.0k | $1.0k / $5.8k / $20.2k | 2.4 mo | 5.0x | 84% | no |
| PC | $23.2k | $0.7k / $4.6k / $17.3k | 2.4 mo | 5.0x | 80% | no |
| PD | $20.9k | $0.7k / $4.2k / $15.3k | 2.4 mo | 5.0x | 78% | no |
| PF | $27.3k | $1.0k / $5.5k / $20.3k | 2.4 mo | 5.0x | 83% | no |
| **Average** | $29.6k | $1.1k / $5.9k / $21.2k | 2.4 mo | 5.0x | 85% | no |

Stress: list at the base price ($5.9k) and only low-case savings show up ($5.3k/yr): payback 13.5 months.

## One-time spares release (cash freed once, not priced)

| Plant | Low | Base | High |
|---|---|---|---|
| PA | $28.7k | $79.0k | $191.5k |
| PB | $23.5k | $64.7k | $156.8k |
| PC | $18.3k | $50.3k | $122.0k |
| PD | $17.0k | $46.7k | $113.2k |
| PF | $13.1k | $35.9k | $87.0k |

## What moves the price
- **Plant size.** The demo plants are 90–220 employees, all in the smallest Census band (100–249). Carrying cost and rush premiums scale with the plant's spares and rush spend, which Velocity #1 puts at ~2× for 250–499 employees and ~4× for 500+. So larger plants price higher than the demo average (estimate, not modeled).
- **Carrying cost on excess spares is the largest lever (39% of base)**, now on Velocity #1's ~$0.37M spares per 170 employees instead of the old $1.8–2.2M placeholder. That change roughly halved the price.
- **Planned vs emergency replacement is the widest lever (29%)**: aging parts, emergency multiplier 1.1–1.6×, migration costs from Velocity #16.
- **Sister-plant spares are 13%** of recurring savings and the most auditable lever (PO + transfer). Downtime avoided and the one-time spares release are shown, never priced.

## Recurring savings by lever (portfolio average, base)

| Lever | Low | Base | High | Share of base |
|---|---|---|---|---|
| carrying_cost_avoided | $2.4k | $11.6k | $40.2k | 39% |
| planned_vs_emergency | $0.8k | $8.6k | $42.6k | 29% |
| rush_premiums_avoided | $0.9k | $5.4k | $13.6k | 18% |
| sister_spare_purchases_avoided | $1.2k | $4.0k | $9.6k | 13% |

## For the slide
**$5–10k per plant per year for a 100–249-employee plant (portfolio base $5.9k, Toledo $9.5k); 20% value capture; 5× return, payback under 3 months.** Plus a one-time $36–79k spares release (base) the customer keeps. Larger plants scale up with their spares and rush spend.
- The base price sits below the $10–25k quick-yes zone, so it's an easy approval, not a stretch.
- Stress case: list at base and only low-case savings show up → payback 13.5 months. Lead with base, footnote the range.
- The 10% / low-savings cell has negative margin: don't quote 10% capture.
