# Manufacturing Downtime Cost Benchmarks

*November 14, 2026*

## Planning defaults: unplanned downtime cost per hour

**For an expected-value model, use lost contribution margin—not lost revenue or a vendor’s all-in “downtime cost”—as the default hourly benefit of avoiding an outage.** The table is a set of **modeled U.S. mid-market plant defaults**, not survey estimates for each industry–size cell. The available surveys do not provide that cross-tabulation.

The low/base/high cases assume that **50% / 100% / 150% of the stated base hourly output is ultimately unrecoverable**. Thus, an hour stopped is not automatically an hour of lost sales: orders made up on a later shift should not count as lost contribution. Values are rounded to the nearest $0.1k.

| Industry | Plant annual revenue band | Base output at risk, $k/hour* | Lost contribution margin, low / base / high, $k/hour |
| --- | --- | --- | --- |
| Automotive suppliers | $25–75m | 12 | **1.8 / 3.6 / 5.4** |
| Automotive suppliers | $75–200m | 30 | **4.5 / 9.0 / 13.5** |
| Automotive suppliers | $200–500m | 75 | **11.3 / 22.5 / 33.8** |
| Food & beverage | $25–75m | 8 | **1.0 / 2.0 / 3.0** |
| Food & beverage | $75–200m | 20 | **2.5 / 5.0 / 7.5** |
| Food & beverage | $200–500m | 50 | **6.3 / 12.5 / 18.8** |
| Packaging | $25–75m | 8 | **1.2 / 2.4 / 3.6** |
| Packaging | $75–200m | 20 | **3.0 / 6.0 / 9.0** |
| Packaging | $200–500m | 50 | **7.5 / 15.0 / 22.5** |
| Metals fabrication/products | $25–75m | 8.8 | **1.3 / 2.6 / 4.0** |
| Metals fabrication/products | $75–200m | 22 | **3.3 / 6.6 / 9.9** |
| Metals fabrication/products | $200–500m | 55 | **8.3 / 16.5 / 24.8** |
| Plastics/rubber products | $25–75m | 8.8 | **1.3 / 2.6 / 4.0** |
| Plastics/rubber products | $75–200m | 22 | **3.3 / 6.6 / 9.9** |
| Plastics/rubber products | $200–500m | 55 | **8.3 / 16.5 / 24.8** |

\* **Revenue, separately:** the “base output at risk” column is the **gross revenue-equivalent production rate**, _not_ profit or necessarily lost sales. Its low/base/high cases are **0.5× / 1× / 1.5×** that column. For example, a $75–200m automotive supplier has **$15k / $30k / $45k per hour of revenue-equivalent output at risk**, versus **$4.5k / $9k / $13.5k of lost contribution**. These are constructed assumptions, not figures reported by the surveys.

**How the defaults were constructed.** Representative annual plant revenue is assumed to be $50m / $125m / $300m across the three bands. Assumed scheduled production hours are 4,000 / 5,000 / 6,000 per year, with 64% / 80% / 100% of plant output affected by the modeled stoppage. Those inputs give $8k / $20k / $50k per hour before _illustrative_ industry adjustments: 1.5× for automotive, 1.1× for metals and plastics, and 1× for food and packaging. Assumed contribution margins on unrecoverable sales are **30% automotive, 25% food, and 30% for the other three**. None of these factors or margins is a measured industry survey result. Replace them with each plant’s scheduled bottleneck throughput, selling price, avoidable variable costs, and ability to catch up.

### What the requested surveys actually support

- **ABB — vendor-commissioned; fielded by Sapio Research.** Its 2023 global survey of 3,215 maintenance decision-makers reports **median self-reported all-in outage costs**, including approximately **$84.7k/hour for food & beverage, $71.0k for metals, $178.9k for plastics/rubber, and $124.7k overall**. These are neither U.S.-mid-market plant medians nor contribution margins. [1](https://new.abb.com/docs/librariesprovider19/default-document-library/abb_survey-report-2023.pdf)
- **Siemens/Senseye — vendor-run.** The _actual_ 2024 report covers 181 interviews with professionals at **large organizations worldwide**. It reports **$2.3m/hour for automotive** and **$36k/hour for FMCG**. The automotive number concerns large, integrated operations—not a transferable hourly default for a mid-market parts supplier. Siemens’ cost definition includes lost sales, idle and repair wages, emergency parts, and penalties. **Source-version caution:** one Siemens PDF indexed under a “2024” filename is internally titled _The True Cost of Downtime 2022_; the 2024 figures cited here come from the distinct 2024 report. [2](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/tcod-2024.pdf) · [3](https://assets.new.siemens.com/siemens/assets/api/uuid:3d606495-dbe0-43e4-80b1-d04e27ada920/DICS-B10056-00-7600-The-True-Cost-of-Downtime-2024.pdf)
- **SimuTech — vendor-run.** Its survey of **200 U.S. engineering/operations professionals at companies below $500m revenue** is closer to the requested company scale: **52% said an hour of **_**engineering downtime**_** cost their facility at least $50k on average**. It does not supply the requested plant-size-by-industry contribution-margin table, and engineering downtime need not equal a production-line stoppage. [4](https://simutechgroup.com/cost-of-engineering-downtime/)
- **L2L — vendor-sponsored, conducted with a third-party research firm.** Its survey of **607 U.S. manufacturing leaders** reports an average **17 unplanned downtime hours per facility per month** and that **six in ten** report **more than $250k annually from downtime**. Its illustrative roughly **$12/minute** calculation uses an annual-loss threshold and **30 monthly hours of **_**all**_** downtime**; it is **not an observed median hourly unplanned-outage cost**. L2L includes the five relevant sectors in its sample but does not publish a defensible cost/hour cross-tab for them. [5](https://www.l2l.com/hubfs/Beyond%20Breakdowns%20The%20Real%20Impact%20of%20Manufacturing%20Downtime.pdf)

**EV implementation:** use avoided unplanned hours × probability output cannot be recovered × hourly contribution from affected output, then add **incremental** scrap, restart costs, overtime, and contract penalties where evidenced. Do not add gross lost revenue to contribution margin, or add vendor all-in benchmarks on top: both would double-count. For food processing or continuous metals operations, validate that the modeled outage affects the whole line or plant before using these defaults; “discrete manufacturer” does not describe every facility in those categories.

## Sources

1. [ABB report](https://new.abb.com/docs/librariesprovider19/default-document-library/abb_survey-report-2023.pdf)
2. [Siemens 2024 report](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/tcod-2024.pdf)
3. [Siemens 2022 report](https://assets.new.siemens.com/siemens/assets/api/uuid:3d606495-dbe0-43e4-80b1-d04e27ada920/DICS-B10056-00-7600-The-True-Cost-of-Downtime-2024.pdf)
4. [SimuTech survey](https://simutechgroup.com/cost-of-engineering-downtime/)
5. [L2L report](https://www.l2l.com/hubfs/Beyond%20Breakdowns%20The%20Real%20Impact%20of%20Manufacturing%20Downtime.pdf)

## Sources

1. [The True Cost of an Hour’s Downtime: An Industry Analysis](https://www.siemens.com/global/en/products/services/industrial-services/true-cost-of-downtime.html)
2. [The True Cost of an Hour’s Downtime: An Industry Analysis by Emily Johnson on Siemens Blog](https://blog.siemens.com/2024/07/the-true-cost-of-an-hours-downtime-an-industry-analysis/)
3. [Siemens · Brochure template · A4 portrait](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/tcod-2024.pdf)
4. [Siemens · Data sheet · A4 portrait](https://assets.new.siemens.com/siemens/assets/api/uuid:3d606495-dbe0-43e4-80b1-d04e27ada920/DICS-B10056-00-7600-The-True-Cost-of-Downtime-2024.pdf)
5. [Siemens · Data sheet · A4 portrait](https://assets.new.siemens.com/siemens/assets/api/uuid:3d606495-dbe0-43e4-80b1-d04e27ada920/dics-b10153-00-7600truecostofdowntime2022-144.pdf)
6. [Siemens · Brochure template · A4 portrait](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/tcod-2024_original.pdf)
7. [The true cost of downtime | Siemens](https://www.assetmanagement.siemens.com/resource/the-true-cost-of-downtime)
8. [Die wahren Kosten einer Stunde Ausfallzeit: Eine Branchenanalyse by  on Siemens Blog](https://blog.siemens.com/de/2024/07/die-wahren-kosten-einer-stunde-ausfallzeit-eine-branchenanalyse/)
9. [The True Cost of Downtime](https://www.assetmanagement.siemens.com/sites/default/files/file/2026-08/True-cost-downtime-IG-Siemens-2026.pdf)
10. [Siemens · Brochure template · A4 portrait](https://assets.new.siemens.com/siemens/assets/api/uuid:1b43afb5-2d07-47f7-9eb7-893fe7d0bc59/TCOD-2024%5Foriginal.pdf)
11. [Share in our success – ABB ESAP 2022](https://new.abb.com/docs/librariesprovider19/default-document-library/abb_survey-report-2023.pdf)
12. [Manufacturing Downtime Statistics: Cost per Hour, Causes ...](https://rapideyeinspections.com/research/manufacturing-downtime-statistics/)
13. [Plastics & rubber sector is 'hardest hit' by unplanned downtime costs | European Rubber Journal](https://www.european-rubber-journal.com/article/2094440/rubber-manufacturers-among-hardest-hit-by-downtime-costs)
14. [ABB survey reveals unplanned downtime costs ...](https://new.abb.com/news/detail/107660/abb-survey-reveals-unplanned-downtime-costs-125-000-per-hour)
15. [The True Cost of Unplanned Downtime by Industry - SeQent](https://seqent.com/blog/the-true-cost-of-unplanned-downtime-by-industry/)
16. [AI-BASED SENSOR-LESS](https://library.e.abb.com/public/517f4be8be594ec6b55a3e6863316c4f/CogniEN%20Fault_prediction_broch_2GNA002425_ENa.pdf?x-sign=S60fAZ4QtN6X0NePdnrPRMT9UdasTHI3OrsltllPRayf8cs0XhWOJqJu7O5gpLh6)
17. [Cost of Unplanned Downtime in Manufacturing 2026](https://oxmaint.com/industries/manufacturing-plant/cost-of-unplanned-downtime-in-manufacturing-2026)
18. [ABB survey reveals unplanned downtime costs ...](https://new.abb.com/news/detail/108403/abb-survey-reveals-unplanned-downtime-costs-242-000-cad-per-hour)
19. [ABB survey reveals unplanned downtime costs INR 7 million per hour | News center](https://new.abb.com/news/detail/108271/abb-survey-reveals-unplanned-downtime-costs-inr-7-million-per-hour)
20. [Value of Reliability: ABB Survey Report 2023 | ABB Motion](https://www.linkedin.com/posts/abb-motion_value-of-reliability-abb-survey-report-2023-activity-7117751732754898944-zCzK)
21. [The True Costs of Downtime 2024](https://www.automation.com/article/white-paper-true-costs-downtime-2024)
22. [Cost of Unplanned Downtime per Hour (2024 Data) | VSight](https://vsight.io/blog/cost-of-unplanned-downtime-manufacturing/)
23. [The Cost Of Unplanned Downtime: Published Benchmarks By Sector | Industry Digits](https://industrydigits.com/resources/downtime-benchmarks/)
24. [Report zeigt wahre Kosten von Ausfallzeiten - Wartung & Instandhaltung](https://service-and-maintenance.com/pma/report-zeigt-wahre-kosten-von-ausfallzeiten/)
25. [The True Cost of Downtime 2024 - Siemens](https://manuals.plus/m/55849624d8f93a5fd9baa780e517e6e8f2702c3b322d52f0c986c94a6108c8ac)
26. [Maintenance Mindset: Inflation-driven trends are causing unplanned downtime costs to surge 300% in heavy industry | Plant Services](https://www.plantservices.com/predictive-maintenance/article/55308021/maintenance-mindset-inflation-driven-trends-are-causing-unplanned-downtime-costs-to-surge-300-in-heavy-industry)
27. [The Real Cost of Unplanned Downtime](https://s3.fabrico.io/uploads/The_real_cost_of_downtime.pdf)
28. [Beyond Breakdowns: The Real Impact of Manufacturing Downtime](https://www.l2l.com/hubfs/Beyond%20Breakdowns%20The%20Real%20Impact%20of%20Manufacturing%20Downtime.pdf)
29. [New Study: Only Half of Manufacturers Successfully Reduce Downtime](https://www.l2l.com/news/l2l-report-reveals-impact-of-manufacturing-downtime)
30. [The Impact of Manufacturing Downtime: The Real Costs](https://www.l2l.com/blog/2025-report-manufacturing-downtime)
31. [Research Report: The Real Impact of Manufacturing Downtime](https://www.l2l.com/2025-manufacturing-downtime-report)
32. [Manufacturing Downtime Cost: How to Calculate It and Cut I](https://www.collettsystems.com/blog/manufacturing-downtime-cost)
33. [Downtime Cost Calculator: Calculate the Cost of Downtime](https://www.l2l.com/downtime-cost-calculator)
34. [L2L White Paper - Final R1](https://www.l2l.com/hubfs/Hobson%20ROI%20Whitepaper_compressed.pdf)
35. [Unplanned downtime costs US manufacturers up to $207 Weekly](https://pressroom.fluke.com/unplanned-downtime-costs-united-states-manufacturers-up-to-207m-weekly-exposing-critical-vulnerabilities-in-industrial-resilience/)
36. [Engineering Downtime is Costing You Money | SimuTech Group](https://simutechgroup.com/cost-of-engineering-downtime/)
37. [Manufacturing Downtime: Costs, Causes & Solutions | SimuTech - Manufacturing Management](https://www.manufacturingmanagement.co.uk/content/news/engineering-downtime-the-hidden-cost-for-manufacturers)
38. [1 in 5 Manufacturers Lost $250K to Engineering Downtime: Study | Supply & Demand Chain Executive](https://www.sdcexec.com/sourcing-procurement/manufacturing/news/22953788/simutech-group-1-in-5-manufacturers-lost-250k-to-engineering-downtime-study)
39. [downtime cost](https://assets.sumitomodrive.com/sites/default/files/2025-04/cost-of-downtime.pdf)
40. [Share in our success – ABB ESAP 2022](https://library.e.abb.com/public/45afcf54780c489095517e653422d157/ABB_Survey%20Report%202023_1920x1080_20231010_JL_final_edits.pdf?x-sign=4o88yeLVtCpbUtRLMXP7Qsu7NiYukEhoA8uURcfMOVphJlQmfB0BCFNsGbLangwR)
41. [State of Industrial DevOps Report](https://8084760.fs1.hubspotusercontent-na1.net/hubfs/8084760/Marketing%20assets/Copia_Report_1stAnnual_r12.pdf)
42. [Unplanned downtime incidents have dropped, but costs continue to rise: MaintainX | Facilities Dive](https://www.facilitiesdive.com/news/maintainx-preventive-maintenance-industrial-facilities-management-2024-downtime-costs/724230/)
43. [Downtime Cost Survey Results](https://bin95.com/download/septdtsurvey.pdf)
44. [Unscheduled downtime costs US$125,000 per hour - ABB survey | Manufacturing Digital](https://manufacturingdigital.com/procurement-and-supply-chain/unscheduled-downtime-costs-us-125-000-per-hour-abb-survey)
45. [The Monthly Metric: Unscheduled Downtime](https://www.ismworld.org/supply-management-news-and-reports/news-publications/inside-supply-management-magazine/blog/2024/2024-08/the-monthly-metric-unscheduled-downtime/)
46. [Electric motors cost most when they run, not when bought](https://www.themanufacturer.com/articles/maintenance-strategies-reliability-is-not-just-key-its-king/)
47. [Survey Reveals Unplanned Downtime Costs $103,000 per Hour](https://www.fabricatingandmetalworking.com/2023/11/survey-reveals-unplanned-downtime-costs-103000-per-hour/)
48. [ABB survey reveals unplanned downtime costs the typical ...](https://new.abb.com/news/detail/108529/abb-survey-reveals-unplanned-downtime-costs-the-typical-australian-industrial-business-349-000-per-hour)
49. [Studie: Value of Reliability in deutschen Industriebetrieben](https://www.elektrotechnik.vogel.de/value-of-reliability-deutschen-industriebetrieben-a-231968a402621eeec975b6409c484562/)
50. [Industrial AI ROI Calculator: Payback & ROI by Industry](https://aigreentools.com/resource/industrial-ai-roi-calculator/)
51. [The Real Cost of Unplanned Downtime in Manufacturing ...](https://reliamag.com/topics/articles/cost-unplanned-downtime-manufacturing)


---

[View in Growth Signals](https://kearney-perlab.growthsignals.com/research/id-1794699700028-0.7e1375e5ddef48)