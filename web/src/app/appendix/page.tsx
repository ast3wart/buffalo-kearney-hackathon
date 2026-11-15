import Link from "next/link";
import { AnomalyChart, type SeriesPoint } from "@/components/AnomalyChart";
import { AppendixIndex, type IndexItem } from "@/components/AppendixIndex";
import { ASSUMPTIONS } from "@/lib/assumptions";
import { tryJSON } from "@/lib/api";

// Everything behind the numbers that is not a slide: how we got the data, every formula, every assumption, and the
// backup material for Q&A. Searchable (sticky index on the left). Velocity = kearney-perlab.growthsignals.com.

function V({ chat }: { chat: string }) {
  return (
    <span className="ml-1 inline-flex items-center gap-1 rounded bg-accent-soft px-1.5 py-0.5 align-middle text-[11px] font-semibold uppercase tracking-wider text-accent" title={`Velocity research chat: ${chat}`}>
      From Velocity <span className="font-normal normal-case tracking-normal">· {chat}</span>
    </span>
  );
}

function Section({ id, n, title, children }: { id: string; n: number; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-4 rounded border border-line bg-surface p-6 transition-shadow">
      <div className="text-xs font-semibold uppercase tracking-wider text-muted">{String(n).padStart(2, "0")}</div>
      <h2 className="mt-1 text-xl font-semibold tracking-tight">{title}</h2>
      <div className="mt-4 space-y-4 text-[15px] leading-relaxed">{children}</div>
    </section>
  );
}

function F({ children }: { children: React.ReactNode }) {
  return <pre className="overflow-x-auto rounded bg-bg px-4 py-3 font-mono text-[13px] leading-relaxed">{children}</pre>;
}

function T({ head, rows, id }: { head: string[]; rows: React.ReactNode[][]; id?: string }) {
  return (
    <table id={id} className="w-full text-sm">
      <thead><tr className="border-b border-line text-left text-xs uppercase tracking-wider text-muted">{head.map((h) => <th key={h} className="py-1.5 pr-4 font-semibold">{h}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i} className="border-b border-line align-top last:border-0">{r.map((c, j) => <td key={j} className="py-1.5 pr-4">{c}</td>)}</tr>)}</tbody>
    </table>
  );
}

const SECTIONS = [
  { id: "velocity", title: "How we used Velocity", keywords: "velocity growth signals research chats sources method" },
  { id: "workflow", title: "Data collection workflow", keywords: "photos records cabinet monitor sources evidence order day 1 week 1 continuous" },
  { id: "records", title: "Install records: the ~28% formula", keywords: "28% cmms part-level machine-level completeness original install date records formula" },
  { id: "vision", title: "Reading labels with Claude vision", keywords: "photo ocr part number accuracy 127 129 unclear cut-off uspap appraiser" },
  { id: "health", title: "Health score formula", keywords: "weibull survival health 0-100 hazard beta eta remaining life confidence asap arrhenius heat" },
  { id: "anomaly", title: "Anomaly detection statistics", keywords: "ewma cusum trend t-test robust z peers mahalanobis severity false alarm" },
  { id: "downtime", title: "Downtime avoided and output protected", keywords: "downtime avoided output protected at stake hours rescue spare sister plant exposure cap unrecovered" },
  { id: "capex", title: "CapEx cliff and order-by dates", keywords: "capex cliff replacement migration order by lead time buffer" },
  { id: "sourcing", title: "Sourcing and where to buy", keywords: "listings shelf successor distributor authorized counterfeit trust" },
  { id: "hardware", title: "Cabinet Monitor: design and economics", keywords: "hardware device cabinet monitor bom cost install certification cellular mlx90640 esp32 diagram" },
  { id: "pricing", title: "How we charge", keywords: "pricing fixed fee per plant per device revenue share conflict of interest" },
  { id: "proof", title: "Proof: what we measured", keywords: "accuracy precision recall planted failures false alarms test factory" },
  { id: "eol83", title: "The 83%* on the problem slide", keywords: "83% asterisk discontinued end-of-life audit siemens 699 843 obsolete representative" },
  { id: "market", title: "Market, competition, risks", keywords: "market size deals pe competition appraisers risks objections" },
  { id: "assumptions", title: "Every assumption", keywords: "assumptions table values justification" },
];

export default async function AppendixPage() {
  const s = await tryJSON<{ points: SeriesPoint[] }>("/components/PA-L2-M01-C1/series");
  const sec = Object.fromEntries(SECTIONS.map((x, i) => [x.id, i + 1]));
  const items: IndexItem[] = [
    ...SECTIONS.map((x) => ({ id: x.id, title: x.title, section: "Section", keywords: x.keywords })),
    ...ASSUMPTIONS.map((a, i) => ({ id: `a-${i}`, title: a.what, section: "Every assumption", keywords: `${a.value} ${a.why}` })),
  ];
  return (
    <div className="grid gap-8 md:grid-cols-[220px_1fr]">
      <aside className="hidden md:block"><AppendixIndex items={items} sections={SECTIONS} /></aside>
      <div className="min-w-0 space-y-6">
        <header>
          <h1 className="text-3xl font-semibold tracking-tight">Appendix</h1>
          <p className="mt-2 max-w-3xl text-muted">
            Every formula, assumption and data source behind the Equipment Health Index, for Q&amp;A. Search on the left. Items tagged
            <V chat="chat name" /> came from research we ran on Velocity, the Kearney × PERLab research platform; the market numbers and their sources are on the{" "}
            <Link href="/sources" className="text-accent underline">Sources</Link> tab.
          </p>
        </header>

        <Section id="velocity" n={sec.velocity} title="How we used Velocity">
          <p>Velocity was our research engine for every number we could not measure ourselves. We ran <b>20+ Velocity research prompts across a dozen chats</b> and logged each one (prompt, answer, what we used, what we pushed back on) in <code>docs/research/velocity.md</code>.</p>
          <T head={["Velocity research chat", "What it gave us", "Where it is used"]} rows={[
            ["Manufacturing Maintenance Data Adoption", "CMMS use 45/60/75%, part-level records 5/15/30%, drive/PLC diagnostics availability and use", <a key="r" href="#records" className="text-accent">Install records (~28%)</a>],
            ["Cabinet Monitor unit economics", "Hardware $127/$185/$285, certification, install, data plans, cabinets per plant, comparable monitoring prices", <a key="h" href="#hardware" className="text-accent">Cabinet Monitor economics</a>],
            ["Vision feasibility (narrowed rerun)", "Label-reading accuracy benchmarks (85%, 94%, >97% OCR), failure modes, design rules, USPAP reliance", <a key="v" href="#vision" className="text-accent">Reading labels</a>],
            ["Common PLC/drive/HMI families + lifecycle", "Lifecycle dates checked for the knowledge base (e.g. 1769-L32E discontinued Dec 16, 2020)", <a key="s" href="#sourcing" className="text-accent">Knowledge base</a>],
            ["Money-thread prompts #1–6, #15–20", "Plant baselines, carrying cost, rush premiums, failure rates by age (#4), emergency vs planned (#5), discount rates (#15), migration labor (#16), sister-plant transfer (#20)", <a key="d" href="#downtime" className="text-accent">Downtime and CapEx</a>],
            ["Market validation (3 chats) + 7 deep dives", "83% of automation parts end-of-life in one audit, PLC lead times 10–24 wks, ~1,667 US manufacturing deals, appraisal cost structure", <a key="m" href="#market" className="text-accent">Market</a>],
          ]} />
          <p className="text-sm text-muted">Where Velocity could not answer (e.g. a national rate of surprise failures, cabinets per plant), we say so and label the number an assumption.</p>
        </Section>

        <Section id="workflow" n={sec.workflow} title="Data collection workflow">
          <T head={["Source", "When", "What we collect", "What it changes in the health score"]} rows={[
            [<b key="1">1. Label photos</b>, "day 1, every cabinet", "part number, maker, date code", "identity → rated life from the manual, lifecycle status; date code = minimum age"],
            [<b key="2">2. Plant records</b>, "week 1, where they exist (~28% of parts)", "install dates from the CMMS and purchase orders", "true age → position on the wear-out curve"],
            [<b key="3">3. Cabinet Monitor</b>, "continuous, line-stopper cabinets", "temperature, motor current, drive fault logs, fan + capacitor life", "heat aging; anomalies raise failure risk up to 20×; +30% per fault"],
          ]} />
          <p>A part uses whatever evidence it has. More sources → tighter remaining-life range and higher confidence (high ±15%, medium ±30%, low ±50%).</p>
        </Section>

        <Section id="records" n={sec.records} title="Install records: the ~28% formula">
          <p>How many parts come with a known install date? No survey measures it directly, so we combined the Velocity estimates: <V chat="Manufacturing Maintenance Data Adoption" /></p>
          <F>{`P(install record) = P(CMMS) × [ P(part level) × completeness  +  P(machine level) × P(part is original) × completeness ]
                  = 0.60     × [ 0.15 × 0.7                +  0.85 × 0.6 × 0.7 ]
                  ≈ 28%   (6% part-level records + 21% machine-level records)`}</F>
          <T head={["Input", "Value (low / base / high)", "Basis"]} rows={[
            ["Plant uses a CMMS", "45 / 60 / 75%", <>Velocity; anchors Plant Engineering surveys 2018 (53%), 2019 (61%) <V chat="Maintenance Data" /></>],
            ["Of those, part-level records", "5 / 15 / 30%", <>Velocity, low confidence <V chat="Maintenance Data" /></>],
            ["Record completeness", "70%", "assumption; Lukens et al. 2019 saw cost fields go 20% → 90% after process fixes (via Velocity)"],
            ["Part still original to its machine", "60%", "assumption, so a machine install year can date its parts; validate in the pilot"],
          ]} />
          <p className="text-sm text-muted">Also from the same chat: drives exposing fan/capacitor life 10/25/45%; PLCs networked with diagnostics 50/70/85%; plants that routinely use those diagnostics 5/12/25%. That gap (data inside the hardware, unread) is why the Cabinet Monitor reads it.</p>
        </Section>

        <Section id="vision" n={sec.vision} title="Reading labels with Claude vision">
          <p>Each photo is read by Claude (<code>claude-sonnet-5-5</code>) into manufacturer, part number, serial, date code, plus an explicit list of anything unclear. Readings are cached so the demo runs offline.</p>
          <T head={["Benchmark", "Result", "Source"]} rows={[
            ["Our test factory: rendered labels incl. glare, blur, worn, cut-off", "127 / 129 exact; the 2 misses flagged unclear, not guessed", "measured"],
            ["Building nameplates (Park et al. 2022)", "65.8% → 85.0% character accuracy after post-processing", <V key="v1" chat="Vision feasibility" />],
            ["Auto-parts part numbers (Schlüter et al.)", "94%", <V key="v2" chat="Vision feasibility" />],
            ["Control-cabinet detection (Scheck et al. 2026)", "> 95% mAP, > 97% OCR", <V key="v3" chat="Vision feasibility" />],
          ]} />
          <p>Design rules from that research: an identifier with any ambiguous character is unverified; never silently correct a serial or series letter; low-confidence reads go to a person. Appraisers may rely on AI-collected data but keep responsibility (USPAP Advisory Opinion 41, April 2026). <V chat="Vision feasibility" /></p>
        </Section>

        <Section id="health" n={sec.health} title="Health score formula">
          <p><b>Health = 100 × the chance the part survives the next 12 months</b>, from a Weibull proportional-hazards survival model (the reliability-engineering standard).</p>
          <F>{`effective age  a = life_used × rated_life
life_used      = self-reported (fan/capacitor life from the drive)            if available
               = age × heat_factor / rated_life                               otherwise
heat_factor    = 2 ^ ((T − T_ref) / 10)      (life halves per +10 °C; half of today's excess counted for the past)
hazard mult. m = exp( ln(20) × anomaly_severity ) × (1 + 0.3 × faults_12m)     (faults capped at 5)
η = 1.1 × rated_life,  β = 3

health        = 100 × exp( −m × ((a + 1)^β − a^β) / η^β )          floored at 1
remaining life = (a^β + η^β × ln 2 / m)^(1/β) − a                    (conditional median)
range          = ± 15% / 30% / 50%  for high / medium / low confidence`}</F>
          <T head={["Status", "Rule"]} rows={[
            ["Replace ASAP", "health ≤ 10, or getting a replacement takes longer than the life left"],
            ["Replace soon", "≥ 75% of life used, but there is still time to get one"],
            ["Working", "otherwise"],
          ]} />
          <p className="text-sm text-muted">Rated life comes from the manufacturer manual / knowledge base. T_ref: drives 55 °C, PLCs/HMIs 45 °C, power supplies 50 °C. Order-by dates use the health model&apos;s conservative remaining life (below).</p>
        </Section>

        <Section id="anomaly" n={sec.anomaly} title="Anomaly detection statistics">
          <p>Each monitored part learns its own normal over 30 days, then every daily summary is checked by standard statistical process control:</p>
          <F>{`expected temp:  (T − ambient) = a + c × load        (least squares on the 30-day baseline)
residual r      = actual − expected
EWMA            z_t = 0.2 r_t + 0.8 z_{t−1};  alarm beyond 3σ limits        → sudden shifts (failing fan)
CUSUM           S_t = max(0, S_{t−1} + r_t/σ − 0.5);  alarm at S > 5        → slow drift (aging capacitors)
trend           slope of r over time, t-test;  alarm at > 1 °C/month, t > 3 → warming
peers           robust z vs same-model parts (median / MAD);  alarm at |z| > 3
motor current   Mahalanobis distance on RMS/load + sideband energy;  alarm at > 3
severity        1 − exp(−(stat − alarm)/alarm) per detector;  anomaly_severity = max (0–1)
judged on the last 7 days`}</F>
          <div className="h-64 rounded border border-line p-2"><AnomalyChart data={s.data?.points ?? []} /></div>
          <p className="text-sm text-muted">Toledo line-stopper drive with a failing fan (planted, simulated sensor data): EWMA crosses its limit the week the step starts. Measured false-alarm rate: ~1 in 40 monitored parts.</p>
        </Section>

        <Section id="downtime" n={sec.downtime} title="Downtime avoided and output protected">
          <p>Downtime is the number plants feel. We count it two ways, and only for <b>spare rescues we actually found</b> (a line-stopping part whose spare sits at a sister plant). Never scaled up to the whole plant, never in the fee.</p>
          <F>{`hours down without spare = min(lead time to buy one, outage cap 10–25 operating days) × operating hours/day
hours down with spare    = transfer (1–2 days) + swap (2–8 h)
at stake (one failure)   = (hours without − hours with) × line $/hour × share of output never made up (40–80%)

OUTPUT PROTECTED   = Σ at stake                                  (Toledo: $622k, 668 h of stoppage)
DOWNTIME AVOIDED   = Σ P(fails within 3 yrs) × at stake, discounted at 10%, per year   (Toledo: ~$77k/yr, $12–205k)
EXPOSURE / YEAR    = P(fail this year) × hours down × $/hour × unrecovered share        (line-stopper table)

P(fail this year)  = 1 − health/100     (the part's own health score: age, heat, sensor anomalies, faults)
                   = age table below     (only for parts with no health evidence)`}</F>
          <p>Fallback failure odds by age, for parts with no health score: 0–10 yrs 2–5%/yr, 10–20 yrs 4–8%, 20+ yrs 6–10% <V chat="money thread #4" />. Transfer time and cost <V chat="#20 sister-plant transfer" />. Line $/hour from plant revenue and operating hours <V chat="#1 plant baseline" />.</p>
        </Section>

        <Section id="capex" n={sec.capex} title="CapEx cliff and order-by dates">
          <F>{`CapEx in year Y   = Σ replacement cost of control parts expected to reach end of life in Y  (+ migration engineering if discontinued)
replacement cost  = market price from trusted listings, else type fallback;  migration = engineering hours × integrator rate
failure date      = today + health model's conservative remaining life   (else install year + typical life)
order-by          = failure date − lead time − 14-day buffer`}</F>
          <p>Component prices and migration labor <V chat="#16 prices + migration labor" />; emergency vs planned cost <V chat="#5" />; lead times for new PLCs 10–24 wks <V chat="market validation" />.</p>
        </Section>

        <Section id="sourcing" n={sec.sourcing} title="Sourcing and where to buy">
          <p>Recommended order: a spare already on a shelf in the portfolio (reserve it, ~7 days) → the manufacturer or an authorized distributor (for discontinued parts: the official successor) → refurbishers and marketplaces, flagged as counterfeit risk.</p>
          <p>Marketplace prices: 42 real listings hand-collected for the demo parts, plus real distributor offers. Lifecycle status comes from manufacturer pages and distributor records (source URL + date on every knowledge-base row). <V chat="PLC/drive/HMI lifecycle check" /></p>
        </Section>

        <Section id="hardware" n={sec.hardware} title="Cabinet Monitor: design and economics">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/cabinet-monitor-diagram.png" alt="Cabinet Monitor system block diagram" className="w-full rounded border border-line" />
          <T head={["Item", "Low / base / high", "Basis"]} rows={[
            ["Hardware at 1,000 units", "$127 / $185 / $285", <>MLX90640 ~$31 (Octopart), ESP32-S3 $3.73, SHT40 $1.33 (DigiKey), 24→5 V ~$20 <V chat="Cabinet Monitor unit economics" /></>],
            ["Certification (one time)", "$25k / $55k / $100k", <>safety listing + FCC (pre-certified module $4.9–10k) + cellular <V chat="unit economics" /></>],
            ["Install per cabinet", "$120 / $250 / $520", <>1.5–4 h × loaded electrician rate (PILARS 2026) <V chat="unit economics" /></>],
            ["Data + cloud per year", "$10 / $30 / $90", <>1NCE, Hologram, AWS IoT Core <V chat="unit economics" /></>],
            ["All-in first year per cabinet", <b key="b">~$270 / ~$474 / ~$902</b>, <V key="v" chat="unit economics" />],
            ["Line-stopper cabinets per plant", "20 / 60 / 150", <>planning assumption, no published benchmark <V chat="unit economics" /></>],
            ["Comparable monitoring", "$300 / $900 / $2,400 per asset-year", <>Erbessd $22/device/month + $400; Augury unpublished <V chat="unit economics" /></>],
          ]} />
          <p className="text-sm text-muted">Read-only to plant equipment, own cellular link (not on the plant network), no inbound ports. Before quoting: qualify the clamps, confirm camera field of view in a real cabinet, test LTE-M inside a closed steel cabinet. Diagram source: <code>docs/plan/hardware/cabinet-monitor-diagram.tex</code> (TikZ).</p>
        </Section>

        <Section id="pricing" n={sec.pricing} title="How we charge">
          <p><b>We charge for what the customer can count, not for what we say they saved.</b> Never a share of savings: savings can&apos;t be audited, so a share of them would make us the judge of our own fee (mentor feedback).</p>
          <T head={["Step", "Price", "What it covers"]} rows={[
            ["1 · One-time: onboard a plant", "$1–2k flat, per plant", "first scan: registry, line stoppers, spending by year"],
            ["2 · Yearly: registry subscription", "$4–10k per plant, tiered by the number of critical parts", "kept current: lifecycle alerts, rescans, spares on every plant's shelf"],
            ["3 · Monthly: sensors", "$ per monitored point (price to set)", "clip-on Cabinet Monitors on the riskiest parts, hardware included"],
          ]} />
          <p>Toledo pays ~$9.5k a year against ~$48k of auditable savings: paid back in ~2.4 months. Cost to serve a plant: $0.3–1.8k a year. Tier amounts come from Brandon&apos;s money model (<code>xray/pricing.py</code>); pilots test willingness to pay.</p>
          <p className="text-sm text-muted">The savings model stays as the customer&apos;s business case (payback), not as the price formula. Comparable monitoring sells for ~$900 per machine per year <V chat="unit economics" />.</p>
        </Section>

        <Section id="proof" n={sec.proof} title="Proof: what we measured">
          <T head={["What", "Result", "How"]} rows={[
            ["Part numbers read from label photos", "127 / 129 exact; 2 misses flagged", "synthetic test factory with planted answers"],
            ["Matching parts to the catalog", "100% precision, 98% recall", "against the answer key"],
            ["Planted failures caught by the health model", "5 / 5 score ≤ 40", "failing fan, worn capacitors, current anomaly, hot connection, overheating relay"],
            ["False alarms (anomaly detectors)", "~1 in 40 monitored parts", "parts with no planted problem"],
          ]} />
          <p className="text-sm text-muted">Sensor data in the demo is simulated in the exact format the device would send; plants are fictional; part numbers, lifecycle data and listings are real.</p>
        </Section>

        <Section id="eol83" n={sec.eol83} title="The 83%* on the problem slide">
          <p><b>What it is:</b> one real plant audit published by Siemens (2025): <b>699 of 843</b> automation assets, from 17 manufacturers, were discontinued or end-of-life. <V chat="Manufacturing Equipment Risk Costs" /></p>
          <p><b>Why the asterisk:</b> it is one plant, from a vendor that sells upgrades, not a national rate. Siemens&apos; other published audits found <b>35%</b> (3,686 filling/packaging assets), <b>59%</b> (914 process assets) and <b>60%</b> (388 utility assets). <V chat="Manufacturing Equipment Risk Costs" /></p>
          <p><b>What we claim:</b> a large share of the automation in older plants is past its supported life, often a third to most of it. Our own demo portfolio, built on real part numbers and lifecycle data, has <b>32%</b> of critical parts discontinued or end-of-life. No survey measures a national rate, so we never quote one.</p>
        </Section>

        <Section id="market" n={sec.market} title="Market, competition, risks">
          <T head={["Market", "Number", "Source"]} rows={[
            ["US multi-plant manufacturers (recurring accounts)", "8–18k", <Link key="s" href="/sources" className="text-accent">Sources tab</Link>],
            ["PE-owned manufacturers in hold", "2–4k", <Link key="s2" href="/sources" className="text-accent">Sources tab</Link>],
            ["US manufacturing deals (2024)", "1,667; ~670 with an equipment review", <V key="v" chat="deal volume deep dive" />],
            ["Automation parts end-of-life in one plant audit", "83%", <V key="v2" chat="Manufacturing Equipment Risk Costs" />],
            ["New controller lead time", "10–24 weeks", <V key="v3" chat="Installed-Base Audits Market" />],
          ]} />
          <T head={["Competitor", "Gap"]} rows={[
            ["Appraisers", "value machines, not parts"], ["Operations diligence", "one-time, not kept up"],
            ["Controls audits (e.g. OEM installed-base audits)", "one brand at a time"], ["Monitoring vendors", "~$900 per machine per year, no part registry"],
          ]} />
          <T head={["Risk", "How we would know"]} rows={[
            ["Plants have terrible data", "pilot plant coverage: share of parts with an identity, a date and a health score"],
            ["The health score is unproven", "calibrate on 10 cabinets for 90 days against real failures"],
            ["Plants won't install hardware", "install time and approvals in the pilot (read-only, clamp-on, planned stop)"],
          ]} />
        </Section>

        <Section id="assumptions" n={sec.assumptions} title="Every assumption">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-line text-left text-xs uppercase tracking-wider text-muted"><th className="py-1.5 pr-4 font-semibold">Assumption</th><th className="py-1.5 pr-4 font-semibold">Value</th><th className="py-1.5 font-semibold">Justification</th></tr></thead>
            <tbody>
              {ASSUMPTIONS.map((a, i) => (
                <tr key={a.what} id={`a-${i}`} className="scroll-mt-4 border-b border-line align-top last:border-0">
                  <td className="py-1.5 pr-4 font-medium">{a.what}</td>
                  <td className="tabular py-1.5 pr-4">{a.value}</td>
                  <td className="py-1.5 text-muted">{a.why}{/velocity/i.test(a.why) && <V chat="see section 01" />}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      </div>
    </div>
  );
}
