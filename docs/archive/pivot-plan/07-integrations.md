# 7 · External software we're compatible with (assumptions)

[← index](index.md)

**Rule:** for the hackathon we **mirror each system's format in the synthetic data** but don't build connectors. On stage: "designed to plug into…". ⚠️ Check exact status names and API terms before quoting them on a slide.

| # | Assumption | Real systems | How the POC shows it | Phase |
|---|---|---|---|---|
| 1 | The equipment list arrives as a **CMMS/EAM export** | SAP PM, IBM Maximo, Fiix, Limble, UpKeep | Import a CSV with Maximo-like asset columns (asset no., description, location, manufacturer, model, install date) | 0 (CSV) → 2 (API) |
| 2 | Spares on hand come from **ERP / storeroom inventory** | SAP MM, Oracle, NetSuite | A `spare_stock` CSV per plant (qty, bin, last moved). Drives the cross-plant spare match and the idle-stock number | 0 (CSV) → 2 |
| 3 | Lifecycle status follows **OEM categories** | Rockwell PCDC (Active / Active Mature / End of Life / Discontinued ⚠️ verify), Siemens lifecycle data on SiePortal | KB uses the same status words + a source URL per entry | 0 curated → 1 partner feeds |
| 4 | Asset classes follow **standards** | ISO 14224 (equipment taxonomy), ISO 55000 (asset management), ECLASS / UNSPSC | `class_code` column in the KB | 0 |
| 5 | Sourcing comes through **official APIs and partners** | Nexar/Octopart, DigiKey, Mouser APIs; eBay Browse API; Radwell / EU Automation / surplus dealers through partnerships | Curated offers tagged `channel` + `authorized` + `trust_score` | 0 curated → 3 live |
| 6 | **Counterfeit-risk** signals | ERAI, GIDEP reports | A trust-score input for sellers that aren't authorized | 3 |
| 7 | Live discovery in plants the customer owns | OPC UA, Rockwell FactoryTalk AssetCentre, OT-security asset lists (Claroty, Nozomi) | Roadmap slide only. **Photos cover the pre-close case, where there's no network access.** | 5 |
| 8 | Output feeds the **adviser's report** | Appraisal reports, quality-of-earnings / ops-diligence reports | CSV/PDF findings export with an evidence column | 1 |
| 9 | Vision runs on a **hosted model** | Anthropic API (`claude-sonnet-5-5`) | Live + cached responses | 0 |

## Design rules (from AGENTS.md)
- Use official APIs and partner feeds only. Respect each site's terms of use (no unlicensed scraping).
- Show counterfeit risk for every seller that isn't authorized.
- A person approves purchases and anything that goes into an investment memo.
- Matching code doesn't hardcode manufacturer or part names. Abbreviations are data.

## Data we generate to match these formats
| File | Mirrors |
|---|---|
| `data/seed/assets_plant_a.csv`, `assets_plant_b.csv` | CMMS asset export |
| `data/seed/spares_plant_a.csv`, `spares_plant_b.csv` | ERP storeroom inventory |
| `data/seed/kb.csv` | OEM lifecycle data + ISO/ECLASS classes |
| `data/seed/offers.csv` | Distributor / marketplace API results |
| `data/seed/answer_key.json` | Planted truth for accuracy |
| `data/photos/` | Nameplate + cabinet photos (real + generated) |
