import { Card, PageHeader } from "@/components/ui";

// Every headline number in the demo and the pitch, where it comes from, and how strong the evidence is.
// Keep in sync with docs/research/market-validation.md, deep-dive-numbers.md, velocity.md and xray/params.py.
type Row = { n: string; what: string; source: string; kind: "measured" | "survey" | "vendor" | "estimate" | "model" | "real data" };

const KIND: Record<Row["kind"], string> = {
  measured: "bg-accent-soft text-accent",
  "real data": "bg-accent-soft text-accent",
  survey: "bg-warn-soft text-warn",
  vendor: "bg-warn-soft text-warn",
  estimate: "bg-bg text-muted",
  model: "bg-bg text-muted",
};

const SECTIONS: { title: string; note?: string; rows: Row[] }[] = [
  {
    title: "The problem: is it big?",
    rows: [
      { n: "~$1.4T / yr, 11% of revenue", what: "Unplanned downtime cost at the world's 500 largest companies", source: "Siemens, True Cost of Downtime 2024 (181 interviews, extrapolated)", kind: "vendor" },
      { n: "44% monthly, 14% weekly", what: "Plants with equipment-related interruptions at least that often", source: "ABB / Sapio Research 2025, n = 3,600", kind: "survey" },
      { n: "52%", what: "Smaller US manufacturers (< $500M) saying downtime costs ≥ $50k per hour", source: "SimuTech 2025, n = 200", kind: "survey" },
      { n: "83% (699 of 843)", what: "Automation assets discontinued or end-of-life in one real plant audit", source: "Siemens obsolescence audit case, 2025 (one plant, not a national rate)", kind: "vendor" },
      { n: "Only 55%", what: "Plants with a proactive plan to manage obsolete components", source: "ABB 2025", kind: "survey" },
      { n: "9.2 years", what: "Average age of equipment in US durable-goods factories, oldest since 2011", source: "Federal Reserve / BEA data via Silverado Policy Accelerator", kind: "measured" },
      { n: "PLCs 10–24 wks, drives 12–26 wks", what: "Lead times for new automation hardware", source: "Distributor planning ranges, Q1 2026", kind: "vendor" },
    ],
  },
  {
    title: "The market: how many customers?",
    rows: [
      { n: "25,799", what: "US manufacturing plants with 100+ employees (8,992 with 250+)", source: "US Census County Business Patterns 2022, NAICS 31-33", kind: "measured" },
      { n: "1,667", what: "US manufacturing acquisitions in 2024", source: "Travelers / PitchBook", kind: "measured" },
      { n: "~670 / yr (450–900)", what: "Of those, deals that get an equipment or controls review", source: "Velocity model on the deal count (no body publishes this)", kind: "estimate" },
      { n: "67.1%", what: "Share of US mid-market PE deals that are add-ons (each brings a new plant register)", source: "PitchBook, Q3 2026 US PE Middle Market Report", kind: "measured" },
      { n: "32,000 · $3.8T", what: "Unsold PE-backed companies worldwide (the liquidity squeeze)", source: "Bain, Global Private Equity Report 2026", kind: "measured" },
      { n: "~$93B", what: "US maintenance, repair and operations (MRO) spend, 2025: the pool savings come from", source: "Mordor Intelligence (market estimate; definitions vary)", kind: "estimate" },
      { n: "22%", what: "MRO inventory unused for 5+ years", source: "SPARETECH survey of 300 manufacturing executives", kind: "survey" },
    ],
  },
  {
    title: "Today's alternatives: what they cost",
    rows: [
      { n: "~64 h, ~$12.8k", what: "On-site machinery appraisal, mid-market plant; photo capture saves only 2–5 h", source: "Velocity model from published appraisal fees and practitioner examples", kind: "estimate" },
      { n: "~104 h, ~$20k", what: "Controls / obsolescence assessment; photo ID + lifecycle lookup saves 9–34 h", source: "Velocity model; anchors: distributor IBE $5–15k, Avanceon $15k fixed fee, Siemens $290–341/h", kind: "estimate" },
      { n: "~45 engagements / yr", what: "Consulting-firm breakeven for an expert-reviewed assessment tool ($15k fee uplift)", source: "Velocity model ($600k build, $250k/yr to run)", kind: "model" },
    ],
  },
  {
    title: "Plant economics (inputs to the price model)",
    note: "Values for a ~170-person plant (100–249 employee band), scaled by headcount in the demo.",
    rows: [
      { n: "$1.05M / yr", what: "Maintenance budget", source: "Velocity #1 (benchmarks: maintenance as % of replacement asset value)", kind: "estimate" },
      { n: "$0.37M", what: "Spare-parts inventory on the shelf", source: "Velocity #1", kind: "estimate" },
      { n: "12–30% / yr", what: "Carrying cost of spares (cash part only 3.5–8%)", source: "Velocity #2", kind: "estimate" },
      { n: "~$20k / yr", what: "Rush / expedite premiums", source: "Velocity #3 (one vendor case + survey anchors)", kind: "estimate" },
      { n: "$300–1,840 / plant / yr", what: "Our cost to serve (image recognition API + human review)", source: "Velocity #18 at claude-sonnet-5-5 prices", kind: "estimate" },
    ],
  },
  {
    title: "Our results on the demo",
    note: "Plants and companies are fictional. Part numbers, lifecycle statuses and marketplace listings are real.",
    rows: [
      { n: "127 / 129", what: "Part numbers read exactly by image recognition (the 2 misses were cut-off labels, flagged, not guessed)", source: "Measured on rendered test photos of real part labels", kind: "measured" },
      { n: "100% precision · 98% recall", what: "Parts matched to the right catalog entry; 112 / 112 auto-accepted parts correct", source: "Measured against the demo's planted answer key", kind: "measured" },
      { n: "30 parts", what: "Lifecycle status (active / end-of-life / discontinued) with date and successor", source: "Manufacturer lifecycle pages: Rockwell, Siemens, ABB, Mitsubishi (each part links its source)", kind: "real data" },
      { n: "42 listings", what: "Real marketplace prices for 6 parts (e.g. refurbished Kinetix 6000 $4.3–6.5k)", source: "Hand-collected Nov 14, 2026 from eBay (sold), Radwell, DO Supply; screenshots in the repo", kind: "real data" },
      { n: "~$9.5k / plant / yr", what: "Price: 20% of auditable recurring savings, extrapolated to a whole-plant scan (Toledo; range $1.8–33k; demo-plant average $5.9k)", source: "Our money model (xray/pricing.py); every input labeled in xray/params.py", kind: "model" },
      { n: "176 h → 40 h · ~$84k at stake", what: "One event: Toledo's Line 2 servo drive fails. Worst-case outage without and with the Fort Wayne shelf spare (at stake: $5–249k)", source: "Our model: outage capped at 10–25 operating days, 40–80% of lost output counted (both assumptions)", kind: "model" },
      { n: "~$19k / yr", what: "Downtime avoided at Toledo, expected (range $2–71k). Shown separately, never in the price, never scaled up to the whole plant", source: "Our model: only the spare rescues we found; chance of one failure per spare within 3 years, discounted at 10%", kind: "model" },
      { n: "$429k cut + ~$1.7M holdback", what: "Tillman deal view: overdue spending the buyer inherits ($79k control parts + $350k for 6 machines at end of life); holdback at a 10% discount rate", source: "Our model; discount rate per Damodaran Jan 2026, escrow norms per SRS Acquiom 2025", kind: "model" },
    ],
  },
];

export default function SourcesPage() {
  return (
    <>
      <PageHeader
        title="Where the numbers come from"
        subtitle="Every headline number, its source, and how strong the evidence is. We say what's measured and what's an estimate."
      />
      <div className="mb-4 flex flex-wrap gap-2 text-xs">
        {(["measured", "real data", "survey", "vendor", "estimate", "model"] as const).map((k) => (
          <span key={k} className={`rounded px-1.5 py-0.5 font-medium ${KIND[k]}`}>{k}</span>
        ))}
        <span className="text-muted">vendor = a company that sells a related product · model = our own calculation</span>
      </div>
      <div className="space-y-4">
        {SECTIONS.map((s) => (
          <Card key={s.title} title={s.title}>
            {s.note && <p className="mb-2 text-xs text-muted">{s.note}</p>}
            <table className="w-full text-sm">
              <tbody>
                {s.rows.map((r) => (
                  <tr key={r.n + r.what} className="border-t border-line align-top first:border-0">
                    <td className="tabular w-48 py-2 pr-3 font-semibold">{r.n}</td>
                    <td className="py-2 pr-3">{r.what}</td>
                    <td className="py-2 pr-3 text-xs text-muted">{r.source}</td>
                    <td className="py-2"><span className={`whitespace-nowrap rounded px-1.5 py-0.5 text-[11px] font-medium ${KIND[r.kind]}`}>{r.kind}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        ))}
      </div>
      <p className="mt-4 text-xs text-muted">
        Full research and citations: docs/research/market-validation.md, deep-dive-numbers.md and velocity.md in the repo.
      </p>
    </>
  );
}
