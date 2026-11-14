# Roles and checkpoints (Equipment X-Ray)

**Agreed Sat Nov 14, ~4 PM.** Submission is due **Sun 8:30 AM**.

The work is split by strength. Both threads build part of the live demo, and both run in parallel.

## 🛠 Asher (CS + stats): "the machine" thread: photo → parts → registry → app
| Task | Output |
|---|---|
| Fake target factory + answer key: ~3 lines, ~15 machines, ~40 components, with end-of-life single points of failure planted | `data/factory/` + `truth_components.csv` |
| Knowledge base: ~30 component types (lifecycle status, lifespan, successor). Brandon fills the cost columns. | `data/kb/kb.csv` |
| Vision extraction: Claude reads nameplate and cabinet photos → `xray/matching.py` → knowledge base | `xray/extract.py` |
| Accuracy: precision/recall with confidence intervals against the answer key | `xray/evaluate.py` |
| App: registry screen, CapEx cliff chart, sourcing panel, API | `api/`, `web/` |
| Live photo demo of a real machine | rehearsed |

## 💲 Brandon (finance + accounting): "the money" thread: the numbers in the demo and the pitch
| Task | Output |
|---|---|
| Valuation: CapEx cliff by year, "pay $X less" / holdback, deferred CapEx as a hidden liability, discounting | `xray/valuation.py` |
| Cost columns in the knowledge base (replacement and migration cost) and lines (revenue per day, downtime $/hour) | `data/kb/kb.csv`, `lines.csv` |
| Sourcing: 2–3 discontinued parts with offers from OEM, refurbisher and eBay (price, lead time, condition, trust) + the buy / migrate / monitor rule | `data/sourcing/offers.csv` + `xray/sourcing.py` |
| Refine the estimates with Velocity: willingness to pay, downtime value, sourcing take-rate, PE portfolio size | `docs/research/deep-dive-numbers.md`, `scripts/market_model.py` |
| Pitch numbers + judge Q&A: problem, market, business model, consulting-firm breakeven | `docs/pitch/` |

## Shared
- **The registry data format** ([docs/build/registry-format.md](../build/registry-format.md)): agree it at CP0. Asher fills in *what's installed*, Brandon fills in *what it costs*.
- **The deck:** Brandon owns the problem, market and business-model slides. Asher owns the how-it-works, demo and accuracy slides.
- **Staying unblocked:**
  - Brandon builds against `data/factory/sample/`, a hand-made registry in the agreed format.
  - Asher's app shows placeholder numbers until `valuation.py` lands.

## Checkpoints
| When | Checkpoint | Done means |
|---|---|---|
| **~4:30 PM** | **CP0: format** | `registry-format.md` signed off by both, and a sample registry committed |
| **~7:30 PM** | **CP1: slices work alone** | Asher: photos → registry for the fake factory. Brandon: `valuation.py` + `sourcing.py` run on the sample. Both merged to `main`. |
| **~10:30 PM** | **CP2: end to end** | One command runs the fake factory → registry → CapEx cliff → sourcing → app. First accuracy number. Deck outline. |
| **~1 AM** | **CP3: feature freeze** | After this, only fixes, polish, numbers and the deck. Sleep. |
| **~7 AM** | **CP4: rehearse** | Full pitch once, including the live photo, then submit by 8:30. |

At each checkpoint: merge through a PR, run `./scripts/checkpoint.sh` on `main`, and check your inbox.
