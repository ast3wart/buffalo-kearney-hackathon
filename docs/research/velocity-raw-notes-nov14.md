# Velocity session notes (Sat Nov 14 ~23:50)
## #1 plant baseline — chat id-1794700204664 (tab 777) DONE
Modeled (assumption) not measured. Calc: employees × shipments/emp ($200/300/400k, assumption) × maint/shipments (1/2/3%, anchored NIST 1.8% outlier-excl, survey) ; parts share 25/35/40% (assumption); turns 2/1/0.75.
Maint budget L/B/H: 100–249: $0.35/1.05/2.10M · 250–499: $0.70/2.10/4.20M · 500+: $1.5/4.5/9.0M
MRO purchases: $0.09/0.37/0.84M · $0.18/0.74/1.68M · $0.38/1.58/3.60M
Inventory: $0.04/0.37/1.12M · $0.09/0.74/2.24M · $0.19/1.58/4.80M
Sources: NIST Economics of Manufacturing Machinery Maintenance (Table 3.2/4.1; tiny band samples 17/6/3 plants) — survey; ScottMadden/Oniqua survey >170 asset-intensive respondents, only 9% ≥3 turns — survey; Emerson 2–5% RAV, 1.5–5% sales — vendor; SMRP metric 1.5 defines metric only; BCG 0.5–4.5% rev MRO services+spares — consultant estimate.
Pushback: "2–5% of revenue" too strong (NIST 1.8%); SMRP gives no target; NIST "inventory due to maintenance" is FG buffer not spares.
SURPRISE: base 250–499 plant = $2.1M maint / $0.74M spares << registry defaults $5M / $2M.

## #2 carrying cost — chat id-1794700262283 (tab 780) DONE
12% / 18% / 30% (constructed estimate). Components L/B/H: capital 7/9/12, storage 3/4/6, ins+tax 0.5/1/2, obsolescence/shrink 1.5/4/10.
Sources: ISM — no consensus benchmark; Reliable Media review — no authoritative MRO rate; UNITEC-D 18–25% (vendor); MRO Magazine 20–25% (practitioner); KPMG Inventory Handbook (Oct 2026) on write-downs.
Cash-only buckets 3.5/5/8%. Don't double-count write-offs with obsolescence allowance. 20–30% = FG rule of thumb.
SURPRISE: base 18% > our 15% fallback; but cash portion only ~5%.

## #3 rush premiums — chat id-1794700295097 DONE
No measured industry share/premium. Emergency share of POs 5/12/23%; combined premium 20/35/60%; overtime $50/100/150 per PO. Default plant $1.5M MRO purchases, 1,500 POs → $18,750 / $81,000 / $258,750 per plant per yr (estimate, excl downtime).
Sources: iFactory six-plant beverage case 23% POs emergency, 34% above contract, $642k/yr on $8.2M spend (vendor case, unverified; conflates PO share with spend share); SDI target 1 rush per 8–10 routine (~9–11%) (vendor target); SPARETECH 2026 survey n=362: 12% orders off-contract (survey, not emergency measure); PMMI Rush Premiums QS 2020 n=98 (survey, no average); Faes/Groningen €1,200 vs €150 urgent shipping (case); Plant Engineering ">40% unplanned" (practitioner, no sample); Oxmaint 35–50% steel (vendor, reject).
SURPRISE: base $81k/yr >> our $10k fallback — but it scales with $1.5M MRO purchases; per #1 a 250–499 plant buys ~$0.74M → ~$40k. Pushback: whole range rests on one vendor case.

## #6 value capture — chat id-1794700311766 DONE
Software: 10/15–20/25% of annualized attributable value (Emergence Capital 10–30% heuristic — investor opinion). Gain-share services: 20–25% verified first-yr savings, range 15–30% (Pearl Lemon Procurement — vendor). Verusen 3× guarantee in 12 mo → ceiling 33%; claims 10× avg → ~10% (vendor). Verusen case: $20.9M identified vs $10.5M verified, 29 plants (vendor). SPARETECH: no price published; Idahoan $3M unused / $500k obsolete (vendor). Airinmar 3–5× ROI gain-share, % undisclosed.
Payback: LNS Research 2015 APM survey: >70% expect ≤18 mo, 36% ≤12 mo (survey, old). MaintainX 6–12 mo ROI (vendor). FTMaintenance illustrative 7.2 mo.
Arithmetic: 3–5× gross → fee 20–33%; 3–5× net → 17–25%.
SURPRISE: no procurement-wide 3–5× rule exists; our 20/30/40% is too high for software — use 10/20/30 (40% only above Verusen ceiling).

## #5 planned vs emergency — chat id-1794700308077 DONE
Single obsolete PLC, one line: planned $45,600 vs emergency $126,600 = 2.8× (+$81k) — scenario estimate. Hardware $20k vs $26k (assumption); engineering 160h×$135 = $21.6k vs +40h×$175 = $28.6k (Knapp Engineering 2025 rate sheet — vendor; hours assumption); downtime 8h×$500 = $4k vs 24h×$3,000 = $72k (assumption).
Ex-downtime ratio: $41.6k vs $54.6k = 1.3×.  Sensitivity by unplanned hours: 8h 1.7× / 24h 2.8× / 48h 4.4×.
Sources: Joltek $10–75k small-I/O single-processor migration ex-downtime (vendor); EU Automation 315 kW Siemens drive 36h charter (vendor case, no prices); Liberty Automation S5 3 days down (vendor case); Neuron Industries CureWood S5 retrofit $2,950 + $3,000 I/O + $4,000 integration (vendor); Taggart Brown 2 VFD $62,195 → $67,573 (1.09×, public record, not counterfactual); ABB ~$125k/h median (vendor survey; don't use for one line).
SURPRISE: hardware/labor emergency premium only ~1.3×; the "3×" is all downtime → our 1.5/2/3× fallback (before downtime) is too high; use 1.1/1.3/1.6× before downtime and downtime separately.

## #15 discount rate — chat id-1794700384999 DONE
Owner: 8/10/12% (planning estimate around Damodaran). Damodaran Jan 2026 US cost of capital: Machinery 7.70% (105 firms), Diversified 7.30% (20), Electrical Equipment 8.99% — measured (public-company).
PE: 20/25/30% gross deal IRR. Gompers, Kaplan & Mukharlyamov survey: median 25%, mean 27% gross target IRR (survey); later survey median 24.8%, mean 22.6% (survey). Spire–Branford Castle Fund III 25% net fund target (marketing).
(c) Identified pre-close shortfall → dollar-for-dollar price cut / seller repair / escrow, NOT discounted at IRR (Holland & Knight; Akerman — law-firm practitioner). Years 3–5 spend → put in LBO cash flows and re-solve price. Don't double-count forecast + holdback. Mercer Capital: QoE separates maintenance vs growth.
SURPRISE: deal-lens fallback 15/20% is low vs 25% median; and practitioners don't discount identified shortfalls at all → our "price cut = PV(low)" should be "price cut = undiscounted near-term + PV of later".

## #4 components + failure — chat id-1794700302860 DONE
Counts per plant (assumption) L/B/H: PLC CPUs 20/60/150; drives 40/150/400; HMIs 15/50/120; other controllers 10/35/100; total 85/295/770.
Annual hardware failure prob (assumption) L/B/H: PLC 0.5/2/5%; drives 1/4/10%; HMI 1/4/10%; other 0.5/2/6%.
EOL/discontinued share 10/35/65% (scenario). Siemens audit examples: 699/843 = 83%; 35% of 3,686 filling/packaging; 59% of 914 process; 60% of 388 utilities (vendor audits, selected). E Tech Group food plant >5,000 line items (vendor). ABB Arkema case (vendor). Reponen 2019 LUT thesis >2,000 frequency converters Finnish mills (academic). ABB SPC700 MTBF 180,930 h → 4.7%/yr constant hazard (vendor calc). Siemens HMI display MTBF 30–50k h. ABB drive note: 20–50 yr MTBF assumes fan/capacitor maintenance; design life >10 yr. Kolehmainen, Aalto: slight age increase, work orders can't separate hard failures (academic).
Lifecycle status doesn't cause failure: age/duty/environment/maintenance → hazard; lifecycle → restoration time. CONFIRMS model-spec.
SURPRISE: our age-band fallback (10–20%/yr >20 yrs) is above anything Velocity supports; base per-device 2–4%. 

## #17 escrow — chat id-1794700448126 DONE  ★ slide-quality
SRS Acquiom, 2025 M&A Deal Terms Study (2024 closings, cross-industry): median general indemnity escrow 10.0% of transaction value with no RWI identified vs 0.35% with RWI (pp. 80, 83–84) — measured. Separate PPA escrow median 0.98% pooled (p.22); PPA escrow present in 91% (RWI) vs 66% (no RWI). Survival of general reps median 12 months (p.63).
SRS Acquiom, Lower Middle Market M&A Deals: What Makes Them Different? ($5–50M): median general escrow 12.5%, PPA escrow 1.23% (measured, year not stated in answer — CHECK).
ABA 2025 Private Target M&A Deal Points Study: 139 deals, 2024–Q1 2025, $25–900M, 63% referenced RWI (measured; no escrow split in public summary).
RWI excludes known issues (Horton Group 2026 — broker). Escrow durations 12–18 mo general = practitioner convention, not measured.
NO evidence that vendor diligence cuts escrow or time-to-close.
Treatment: known/quantified → price; uncertain → specific indemnity + special escrow sized to exposure; debt-like only if SPA defines it. Prospective CapEx ≠ debt.
SURPRISE: escrow-reduction scenarios must stay "not evidenced"; special escrow sized to exposure not to 10% norm.

## #16 component prices — chat id-1794700395859 DONE
Labor $160–200/h (Artisan Automation rate sheet: $160 PLC/HMI programming, $180 engineering, $200 emergency — vendor). Hours = estimates.
New (vendor listing) / Refurb (vendor listing) / Migration engineering (estimate):
- PLC small: $150–2,500 (AutomationDirect P1000 $139, P2000 $365) / $400–2,500 (DO Supply 1769-L33ER $2,029) / 24–80 h = $3.8–16k
- PLC large chassis: $550–8,000+ CPU (P3000 $550–750) / $2–5k+ (estimate) / 60–200 h = $9.6–40k
- I/O digital: $100–300, analog $200–1,100 / $90–200 (1756-IB16 $117, $164.61) / 4–16 h = $0.6–3.2k per module
- VFD <10 HP: $200–1,500 (GS20 5 HP $357) / $250–2,000 / 8–24 h = $1.3–4.8k
- VFD 10–100 HP: $650–8,000 (10 HP $659, 15 HP $1,449, 75 HP $5,078) / $1–6k / 16–40 h = $2.6–8k
- VFD >100 HP: $9–30k+ (GS4 125 HP $9,037.50; 300 HP $22,173) / $4–16k+ (PF753 150 HP $14,500) / 32–80 h = $5.1–16k
- HMI small: $340–3,000 (C-more 4" $340, 7" $499) / $750–2,000 (PanelView Plus 7 $1,836) / 12–40 h = $1.9–8k
- HMI large: $1,100–6,500 (CM5 15" $1,699; PV+7 15" surplus $6,088) / $3–5k (PV+7 15" $3,388) / 24–80 h = $3.8–16k
- Servo drive: $500–4,000+ / $1–3k+ (Servostar $2,091) / 24–80 h = $3.8–16k per axis
- Servo motor: $400–4,000+ / $400–4,000+ / 8–32 h
- 24 VDC PSU: $70–550 / $50–250 / 2–8 h
Caveat: low prices are AutomationDirect ecosystem; Rockwell/Siemens new much higher. Migration labor usually >> hardware.
SURPRISE: engineering dominates — PLC migration labor $3.8–40k vs CPU $150–8k; our fallback (20–80 h × $150–300) close, rate band should be $160–200.

## G1 QoE / deferred capex — chat id-1794700458052 DONE
Delayed capex does NOT inflate EBITDA (EBITDA excludes capex) — it inflates FCF. Deferred/capitalized repairs DO inflate EBITDA.
Routes: discrete overdue catch-up → dollar-for-dollar debt-like / price cut / seller cure / holdback (Underridge, Anders — practitioner); recurring opex omitted → EBITDA correction × multiple (Avant Advisory case: −$1.683M capitalized R&M, −$545k deferred truck maintenance — documented case); higher ongoing maintenance capex → normalized FCF or lower multiple (Mercer Capital — provider guidance); growth capex → forecast, not backlog.
Mercer: use depreciation as maintenance-capex proxy only absent better data. Bedrock: deferred replacement = hidden buyer cost, not add-back. Forvis Mazars: don't double-penalize via EBITDA + debt.
No measured frequency of debt-like vs multiple treatment.
SURPRISE/USE: our product's output maps cleanly: backlog list → debt-like $; run-rate gap → normalized capex. Fix pitch wording: "deferred capex inflates FCF, not EBITDA".

## G2 asset register vs floor — chat id-1794700492765 DONE
No defensible single match rate. Kroll 2025: studies put ghost assets at 10–30% of register entries; >15% of recorded assets at one manufacturing client no longer in service (advisory claim, not representative). Peeriosity poll: 14% of companies don't tag; 33% of those don't verify untagged assets (practitioner survey, company share not asset share). Novelis 10-K: keeps fully depreciated assets until removal (filing). Gibraltar Business Capital: full depreciation ≠ end of life (lender).
NBV = books; FMV-in-continued-use = appraiser/acquirer (ASA definitions); NOLV = asset-based lenders' collateral/borrowing base; RCN = cost approach input, insurance, capex planning. PPA uses ASC 820 fair value.
Gotham Consulting case: dry-ice maker, 150+ machines reconciled, $2M capex shortfall at one plant (consultant case).
USE: register ≠ floor is our wedge; "10–30% ghost" is advisory — label it.

## G3 capex vs opex — chat id-1794700589440 DONE
Routine spares: inventory/materials, expensed when consumed (ASC 330, IAS 2). Significant reusable/insurance spares: PP&E if multi-period use (ASC 360 limited guidance; IAS 16.7–8). IFRS: insurance spare depreciated from available-for-use (PwC FAQ 4.4.4.1). Migration = capex if it creates/replaces identifiable long-lived asset or betterment; troubleshooting/like-for-like = R&M. Split mixed projects; software separately. Sources: KPMG Handbook: Inventory; PwC US PP&E guide; Deloitte IAS 16 guide; EY US GAAP vs IFRS; IAS 7.16(a); ASC 230-10-45-13; IASB declined to define EBITDA in IFRS 18 (documented standards/Big Four).
EBITDA/FCF: capitalize → EBITDA up now, FCF hit (investing). Inventory buy → FCF hit via op cash, EBITDA hit on consumption. Expense → both.
PE pooling: no single accounting entity; each company per ownership/control; elimination only within a consolidated group; separate portfolio cos = related-party transactions.
USE: pooled spare transfers between portcos are intercompany sales — need part-level ownership register (a product feature).

## #18 cost to serve — chat id-1794702160649 DONE (rerun solo, Sun ~00:25)
Per plant (estimate): photos 400/500/800; API $0.0008/0.0020/0.0063 per photo (OpenAI GPT-5.4 mini list price — vendor; NOT our model, rerun with claude-sonnet-5-5 pricing); review 25h×$65 / 50h×$85 / 100h×$110 = $1,625/4,250/11,000 (assumption; BLS 2025 median $49.25/h industrial engineers, $48.97 mgmt analysts — measured); workflow $150/400/1,200.
Initial delivery $1,775 / $4,651 / $12,205. On-site capture +$1,300/3,400/8,800. Annual upkeep $620/2,000/5,751.
Year-one (customer photos) $2,395 / $6,651 / $17,956; with capture $3,695 / $10,051 / $26,756.
Gross margin yr1 (low/base/high cost): $10k 76/33/−80% · $25k 90/73/28% · $50k 95/87/64%. Later years: $10k 94/80/42 · $25k 98/92/77 · $50k 99/96/88.
With on-site capture, base yr1: $10k −1%, $25k 60%, $50k 80%.
SURPRISE: API is noise (~$1/plant); human review is the cost. $10k/plant only works if review ≤ ~25 h → Asher's real review hours at CP2 decide the price floor.

## #19 approval limits — chat id-1794702353363 DONE (solo)
Planning ranges, no measured survey medians. Plant manager $5–25k (Summit Polymers policy: plant ops mgr $10k, plant GM $25k incl. software/services — documented company policy; Tallyfy example dept mgr $5k/yr software — vendor example). VP Ops $50–250k opex / $50–150k software (Tallyfy $100k; Summit corporate VP $150k). CFO $100–500k (Tallyfy $100–500k; software cap ~$200k/yr in one example). Above → CEO/board (varies).
RFP: Armstrong competitive bids ≥$50k (company policy); Stanley Black & Decker ≥3 quotes >$50k (company policy). <$25k direct; $25–50k quotes; $50–100k formal competitive (RFQ/3 quotes); $100–250k+ formal RFP likely (inference). SIG 2022 benchmark behind login.
Total contract value counts (Summit) → a 3-yr $10k deal = $30k toward limit.
SURPRISE/USE: confirms fallback: $10–25k/plant/yr = quick-yes; >$50k triggers procurement + IT/security. Watch multi-year TCV.

## #20 sister-plant transfer — chat id-1794705589020 DONE (retry, solo)
Per transfer (estimate): $100 / $355 / $1,260. Freight $25/145/250 (FedEx 2026 list 5 lb Zone 4: Ground $17.06, Standard Overnight $107.46, Priority Overnight $120.37 — vendor list rates); packing $10/20/40; admin 1/2/5 h = $35/70/200 (assumption; BLS May 2025 means: clerks $22.50, EE techs $38.79, accountants $45.56 — measured); bench check $30/120/770 (high incl. $650 outside repair, NJT Automation "from $650" — vendor). Without outside work high = $610.
Separate portcos: +$40–200 finance/procurement per transaction; arm's-length pricing (IRS §1.482-3), sales/use tax. Same entity = location transfer only.
Compare (landed incl. $180 buy overhead): AB 1769-L33ER PLC refurb $2,209 / surplus-new $3,520 (DO Supply) → transfer saves $1,854–3,165. AB 25B-D4P0N104 drive refurb $670 / surplus $869 (Replace Industrial) → saves only $315–514.
Caveats: drive capacitor reforming after storage (Rockwell); safety apps need revalidation.
SURPRISE: fallback ($150–1,000 freight + $200 admin) is too high; base $355. Sharing wins big on PLCs, marginal on cheap drives → only route a transfer when part value > ~$1k.
