# 2 · Long-term market validity

[← index](index.md)

## Why the problem keeps coming back (and grows)
| Driver | Why the record goes stale without us |
|---|---|
| **Equipment keeps aging** | US equipment is the oldest since 2011. Every year, more controllers reach end-of-life. |
| **OEMs keep discontinuing parts** | Lifecycle status changes constantly. A plant that was fine last year may not be fine this year. |
| **PE buy-and-build** | Add-ons are ~76% of buyout deals. **Each add-on brings a new, messy equipment register, its own part names and its own storeroom.** |
| **Supply shocks** | Lead times of 10–30 wks, plus tariffs held in reserve, make "do we have a spare?" a live question every quarter. |
| **Reindustrialization / reshoring** | More plants being bought, expanded and re-tooled in the US (⚠️ size it in the deep-research run, doc 8). |

**What this means for the business:** a one-time scan decays, and keeping the record current is the recurring job. That job justifies a subscription.

## Threats, and how we answer them
| Threat | Why it's real | Our answer |
|---|---|---|
| **OT security vendors** (Claroty, Nozomi, Armis, Dragos) | They already discover PLCs and drives passively on plant networks | They need network access to a plant **you already own**, which doesn't help pre-close. They build security tools, not CapEx or sourcing tools. **Treat them as a future data source** (import their asset lists). ⚠️ Not covered in PR #11 research. Run Velocity on it. |
| **OEMs** (Rockwell, Siemens) expand their installed-base audits | They have the lifecycle data | They'll never be vendor-neutral or recommend a competitor's successor part. Mixed-brand plants are the norm in roll-ups. |
| **SPARETECH / Verusen** move from storeroom to installed base | Adjacent data and customers | We start from what is **installed in each machine** + line criticality. They start from what's on the shelf. Possible partner. |
| **Appraisers build it themselves** | They own the deal relationship | We sell **through** them. We make them faster, and they keep sign-off. |
| **"Just ask ChatGPT"** | Anyone can send a photo to a vision model | The model isn't the product. The **KB, the line-criticality roll-up, the evidence trail and the outcome data** are. |

## Moat (in order of how hard it is to copy)
1. **Outcome data:** "this part failed X months after the scan"; "this part sold for $Y with Z wks lead time from seller S". No one collects this across brands.
2. **Cross-brand lifecycle KB:** grows with every scan and covers the long tail of old equipment.
3. **Portfolio network:** the more plants in a PE portfolio, the more spare-sharing matches. A switching cost at the fund level.
4. **Labeled photo library:** later trains our own cabinet-component detector.
5. **Channel relationships** with appraisers and ops-diligence firms.

## Risks that could sink it
- **Willingness to pay** for the recurring product is unproven. **Test:** paid pilots, and track whether a buyer pays separately.
- **KB coverage** of the long tail is slow to build.
- **Data ownership** across a portfolio (each company vs. the fund) could block spare sharing.
- **Accuracy on worn, dirty nameplates:** measure it, don't assume it.

## Verdict
The market is valid **only as a recurring product**. Diligence-only tops out around $3M/yr. The recurring pool (MRO $93B, automation spares ~$21.6B) is large enough. **The only part we need to win is the avoidable slice:** missing critical spares, rush buys, stranded stock and badly timed replacements.
