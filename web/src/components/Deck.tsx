"use client";

import { Fragment, useCallback, useEffect, useRef, useState } from "react";
import { CartesianGrid, Line, LineChart, ReferenceArea, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type SeriesPoint = { day: number; residual_c: number; ewma_c: number | null; limit_c: number; baseline: boolean };
export type DeckData = {
  companies: {
    name: string;
    owned: boolean;
    since: string;
    deal: string;
    plants: { name: string; state: string; employees: number; lines: number; machines: number }[];
  }[];
  series: SeriesPoint[];
};

// One idea per slide: a headline, at most one visual or 3 short lines. Details live in the live demo, not on slides.
function Slide({ kicker, title, children, owner }: { kicker?: string; title: string; children?: React.ReactNode; owner?: string }) {
  return (
    <div className="flex h-full flex-col">
      {kicker && <div className="text-sm font-semibold uppercase tracking-wider text-accent">{kicker}</div>}
      <h2 className="mt-2 text-balance text-4xl font-semibold leading-tight tracking-tight">{title}</h2>
      <div className="mt-6 min-h-0 flex-1">{children}</div>
      {owner && <div className="text-right text-xs text-muted">{owner}</div>}
    </div>
  );
}

function Big({ n, label }: { n: string; label: string }) {
  return (
    <div>
      <div className="tabular text-6xl font-semibold tracking-tight">{n}</div>
      <div className="mt-2 max-w-xs text-lg text-muted">{label}</div>
    </div>
  );
}

function Ladder() {
  const steps = [
    { n: "1", t: "The plant's own records", d: "maintenance system, purchase orders", c: "best, but usually machine-level only" },
    { n: "2", t: "Label photo", d: "identifies every part in a cabinet", c: "what it is, not how healthy" },
    { n: "3", t: "X-Ray Monitor", d: "heat, motor current, built-in diagnostics", c: "how healthy, continuously" },
    { n: "4", t: "Inspection service", d: "only where the risk justifies it", c: "the expert still signs off" },
  ];
  return (
    <div className="grid h-full grid-cols-4 gap-4">
      {steps.map((s) => (
        <div key={s.n} className="flex flex-col rounded-xl border border-line bg-bg p-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-lg font-semibold text-surface">{s.n}</div>
          <div className="mt-4 text-xl font-semibold">{s.t}</div>
          <div className="mt-2 text-base">{s.d}</div>
          <div className="mt-auto pt-4 text-sm text-muted">{s.c}</div>
        </div>
      ))}
    </div>
  );
}

function HealthFlow() {
  const box = "rounded-xl border border-line bg-bg px-5 py-4 text-center";
  return (
    <div className="flex h-full items-center justify-between gap-3 text-lg">
      <div className={box}><div className="font-semibold">Age & wear</div><div className="text-sm text-muted">records, label date,<br />self-reported life</div></div>
      <span className="text-3xl text-muted">+</span>
      <div className={box}><div className="font-semibold">Heat</div><div className="text-sm text-muted">ages 2× faster<br />per +10 °C</div></div>
      <span className="text-3xl text-muted">−</span>
      <div className={box}><div className="font-semibold">Anomalies</div><div className="text-sm text-muted">statistics on<br />temp + current</div></div>
      <span className="text-3xl text-muted">=</span>
      <div className="rounded-xl bg-accent px-6 py-5 text-center text-surface"><div className="text-3xl font-semibold">0–100</div><div className="text-sm">health + years left<br />+ confidence</div></div>
    </div>
  );
}

function AnomalyChart({ data }: { data: SeriesPoint[] }) {
  if (!data.length) return <div className="text-muted">Series unavailable (start the API).</div>;
  const limit = data[0].limit_c;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <ReferenceArea x1={0} x2={29} fill="var(--bg)" fillOpacity={1} label={{ value: "learns normal (30 days)", position: "insideTop", fill: "var(--muted)", fontSize: 13 }} />
        <XAxis dataKey="day" tick={{ fontSize: 13, fill: "var(--muted)" }} label={{ value: "day", position: "insideBottom", offset: -10, fill: "var(--muted)" }} />
        <YAxis tick={{ fontSize: 13, fill: "var(--muted)" }} unit=" °C" width={60} />
        <Tooltip formatter={(v: number) => `${v} °C`} labelFormatter={(d) => `day ${d}`} />
        <ReferenceLine y={limit} stroke="var(--alert)" strokeDasharray="6 4" label={{ value: "alarm limit", position: "insideTopRight", fill: "var(--alert)", fontSize: 13 }} />
        <Line dataKey="residual_c" name="vs. expected" stroke="var(--muted)" strokeWidth={1.2} dot={false} isAnimationActive={false} />
        <Line dataKey="ewma_c" name="smoothed (EWMA)" stroke="var(--accent)" strokeWidth={3} dot={false} connectNulls={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function ClientSlide({ companies }: { companies: DeckData["companies"] }) {
  const owned = companies.filter((c) => c.owned);
  const ps = owned.flatMap((c) => c.plants);
  const sum = (f: (p: (typeof ps)[number]) => number) => ps.reduce((t, p) => t + f(p), 0);
  const kpis = [
    [String(owned.length), "portfolio companies"],
    [String(ps.length), `plants in ${new Set(ps.map((p) => p.state)).size} states`],
    [sum((p) => p.employees).toLocaleString(), "employees"],
    [String(sum((p) => p.lines)), "production lines"],
  ];
  return (
    <div className="flex h-full flex-col">
      <p className="-mt-3 text-xl text-muted">Midwest private equity firm that buys and grows industrial manufacturers.</p>
      <div className="mt-4 grid grid-cols-4 gap-8 border-y border-line py-3">
        {kpis.map(([n, l]) => (
          <div key={l}>
            <div className="tabular text-5xl font-semibold tracking-tight">{n}</div>
            <div className="mt-1 text-base text-muted">{l}</div>
          </div>
        ))}
      </div>
      <div className="mb-2 mt-5 grid min-h-0 flex-1 grid-cols-3 gap-6">
        {companies.map((c) => (
          <div key={c.name} className={`flex flex-col rounded-2xl p-5 ${c.owned ? "bg-bg" : "border-2 border-dashed border-line"}`}>
            <div className="flex items-baseline justify-between gap-2">
              <span className={`text-xs font-semibold uppercase tracking-wider ${c.owned ? "text-accent" : "text-muted"}`}>
                {c.owned ? `Owned since ${c.since}` : "Acquisition target"}
              </span>
              {c.deal && <span className="tabular text-xs font-semibold text-muted">deal value {c.deal}</span>}
            </div>
            <div className="mt-1 text-2xl font-semibold leading-tight">{c.name}</div>
            <div className="mt-3 flex flex-1 flex-col">
              {c.plants.map((p) => (
                <div key={p.name} className="flex items-baseline justify-between border-t border-line py-2.5">
                  <span className="text-lg font-medium">{p.name}, {p.state}</span>
                  <span className="tabular text-sm text-muted">{p.employees} people · {p.lines} lines</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const ASSUMPTIONS: { what: string; value: string; why: string }[] = [
  { what: "Parts with an install record", value: "~28%", why: "60% CMMS × (15% part-level × 70% complete + 85% machine-level × 60% original × 70%); Velocity research, Plant Engineering surveys" },
  { what: "Record completeness", value: "70%", why: "assumption; a measured CMMS study saw record fields go from 20% to 90% filled (Lukens 2019)" },
  { what: "Part still original to its machine", value: "60%", why: "assumption, so a machine install year can date its parts; validate in the pilot" },
  { what: "Heat aging", value: "life halves per +10 °C", why: "Arrhenius rule of thumb in capacitor and fan datasheets" },
  { what: "Design-point temperature", value: "drives 55 °C, PLCs 45 °C", why: "typical rating points for industrial electronics; verify per manual" },
  { what: "Past heat history", value: "half of today's extra heat", why: "we only see today's temperature, not the part's past" },
  { what: "Health score", value: "100 × P(survives next 12 months)", why: "Weibull survival model (reliability-engineering standard); shape 3 = wear-out; scale 1.1 × rated life from the manual" },
  { what: "Anomaly alarms", value: "EWMA 3σ, CUSUM h = 5, z > 3, Mahalanobis > 3", why: "standard statistical process control defaults; measured ~1 false alarm per 40 monitored parts" },
  { what: "Anomaly effect", value: "failure rate × up to 20", why: "proportional hazards: severity 0–1 scales the hazard; assumption, calibrate against real failures in the pilot" },
  { what: "Fault effect", value: "+30% failure rate per fault (max 5)", why: "assumption; faults logged by the drive in the last 12 months" },
  { what: "Remaining life", value: "conditional median", why: "years until P(survive | survived so far) = 50%, from the same Weibull model" },
  { what: "Remaining-life range", value: "±15% / 30% / 50%", why: "by confidence (high / medium / low), set by which evidence exists" },
  { what: "Device hardware cost", value: "$185 ($127–285) at 1,000 units", why: "Velocity research: MLX90640 ~$31 (Octopart), ESP32-S3 $3.73 (DigiKey), SHT40 $1.33, 24→5 V supply ~$20; current clamps are the big unknown" },
  { what: "Install per cabinet", value: "2.5 h × $100 = $250 ($120–520)", why: "Velocity research; loaded electrician rates (PILARS 2026); done in a planned stop" },
  { what: "Data + cloud", value: "$30 / device / yr ($10–90)", why: "Velocity research; 1NCE $14 for 10 yrs / 500 MB, Hologram $1/SIM/month, AWS IoT Core" },
  { what: "Certification, one time", value: "$55k ($25–100k)", why: "Velocity research; safety listing + FCC (pre-certified module, $4.9–10k quotes) + cellular; spread over the rollout" },
  { what: "Line-stopper cabinets per plant", value: "60 (20–150)", why: "Velocity research estimate; no published cabinets-per-plant benchmark, so a planning assumption" },
  { what: "Comparable monitoring price", value: "~$900 / machine / yr ($300–2,400)", why: "Velocity research; e.g. Erbessd $22/device/month + $400 hardware; Augury doesn't publish prices" },
  { what: "Sensor data in the demo", value: "simulated", why: "no hardware built; data is in the exact format the device would send" },
];

const W = 1120;
const H = 630;

export function Deck({ data }: { data: DeckData }) {
  const slides: React.ReactNode[] = [
    <div key="title" className="flex h-full flex-col justify-center">
      <div className="text-sm font-semibold uppercase tracking-wider text-accent">Kearney × PERLab</div>
      <h1 className="mt-3 text-6xl font-semibold tracking-tight">Equipment X-Ray</h1>
      <p className="mt-6 max-w-2xl text-balance text-2xl text-muted">Know the health of every part in every plant, before one stops a line.</p>
    </div>,

    <Slide key="client" kicker="Our client" title="Granite Ridge Capital">
      <ClientSlide companies={data.companies} />
    </Slide>,

    <Slide key="problem" kicker="Problem" title="Owners do not know the health of the equipment their plants run on">
      <div className="flex h-full flex-col">
        <div className="grid min-h-0 flex-1 grid-cols-[1fr_1.15fr] content-center gap-12">
          <div className="self-start border-l-2 border-accent pl-6 text-lg leading-relaxed">
            <div className="text-xs font-semibold uppercase tracking-wider text-muted">A typical situation</div>
            <p className="mt-2">The plant follows its maintenance schedule: bearings greased, belts changed, oil sampled.</p>
            <p className="mt-3 text-muted">Nobody is watching the 20-year-old drive in the cabinet. The manufacturer stopped making it years ago, and there is no spare.</p>
            <p className="mt-3 text-xl font-semibold">It fails. The line stops.</p>
          </div>
          <div className="grid grid-cols-2 content-start gap-x-8 gap-y-5">
            {[
              ["83%", "of automation parts in one real plant audit were discontinued or end-of-life"],
              ["55%", "of plants have a plan for obsolete parts. The rest do not."],
              ["44%", "of plants have an equipment interruption every month"],
              ["10–24 wks", "to get a new controller; a discontinued one is resale-only"],
            ].map(([n, d]) => (
              <div key={n}>
                <div className="tabular text-4xl font-semibold tracking-tight text-accent">{n}</div>
                <div className="mt-1 text-[15px] leading-snug text-muted">{d}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between border-t border-line pt-3">
          {[
            ["Unknown health", "no list of what is in the cabinets"],
            ["Surprise failure", "no warning, no spare"],
            ["Lost output", "days, sometimes weeks"],
            ["Lost revenue", "and spending nobody budgeted"],
          ].map(([t, d], i, arr) => (
            <Fragment key={t}>
              <div>
                <div className={`text-lg font-semibold ${i === arr.length - 1 ? "text-accent" : ""}`}>{t}</div>
                <div className="text-sm text-muted">{d}</div>
              </div>
              {i < arr.length - 1 && <span className="text-xl text-muted">→</span>}
            </Fragment>
          ))}
        </div>
      </div>
    </Slide>,

    <Slide key="collect" kicker="How we collect data" title="Use what the plant has, fill the gaps cheaply">
      <Ladder />
    </Slide>,

    <Slide key="device" kicker="The hardware" title="X-Ray Monitor: one small box per critical cabinet">
      <div className="grid h-full grid-cols-[1.5fr_1fr] gap-8">
        <figure className="flex min-h-0 flex-col">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/xray-monitor.png" alt="Concept image of the X-Ray Monitor clipped to a DIN rail in a control cabinet" className="min-h-0 flex-1 rounded-xl object-cover" />
          <figcaption className="mt-2 text-xs text-muted">AI-generated concept image · no hardware built yet</figcaption>
        </figure>
        <div className="flex flex-col justify-center gap-5">
          {[
            ["Sees heat", "thermal camera watches every drive in the cabinet"],
            ["Feels current", "clamp-on sensors on the motor leads, no rewiring"],
            ["Never touches controls", "read-only; its own cellular link, not the plant network"],
            ["~$185 to build", "clips on a DIN rail in a planned stop, ~2.5 h install"],
          ].map(([t, d]) => (
            <div key={t} className="border-l-2 border-accent pl-4">
              <div className="text-xl font-semibold">{t}</div>
              <div className="text-base text-muted">{d}</div>
            </div>
          ))}
        </div>
      </div>
    </Slide>,

    <Slide key="diagram" kicker="The hardware" title="How the X-Ray Monitor works">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/xray-monitor-diagram.png" alt="System block diagram of the X-Ray Monitor" className="h-full w-full object-contain object-top" />
    </Slide>,

    <Slide key="econ" kicker="The hardware" title="What it costs to build and install">
      <div className="grid h-full grid-cols-[1fr_1.3fr] items-center gap-12">
        <Big n="~$470" label="per cabinet, first year, all in (range $270–900)" />
        <div className="space-y-5 text-xl">
          <div className="flex justify-between border-b border-line pb-2"><span>Hardware, at 1,000 units</span><b className="tabular">$185</b></div>
          <div className="flex justify-between border-b border-line pb-2"><span>Electrician install, ~2.5 h</span><b className="tabular">$250</b></div>
          <div className="flex justify-between border-b border-line pb-2"><span>Data + cloud, per year</span><b className="tabular">$30</b></div>
          <div className="flex justify-between text-muted"><span>Comparable monitoring, per machine per year</span><span className="tabular">~$900</span></div>
        </div>
      </div>
      <div className="text-sm text-muted">Only on line-stopper cabinets: ~60 per plant. Velocity-powered estimates; full ranges in the appendix.</div>
    </Slide>,

    <div key="demo" className="flex h-full flex-col">
      <div className="flex items-baseline justify-between px-1 pb-2">
        <span className="text-sm font-semibold uppercase tracking-wider text-accent">Live demo · Granite Ridge Capital</span>
        <span className="text-xs text-muted">click inside to drive the app · click outside, then arrows to leave</span>
      </div>
      <iframe src="/" className="min-h-0 w-full flex-1 rounded-xl border border-line bg-bg" title="Equipment X-Ray live demo" />
    </div>,

    <Slide key="ask" kicker="Recommendation" title="3 paid plant pilots + 1 portfolio">
      <div className="grid grid-cols-3 gap-10 pt-6">
        <Big n="90 days" label="per pilot: registry + X-Ray Monitors on line stoppers" />
        <Big n="10" label="cabinets monitored per plant to calibrate the score" />
        <Big n="1" label="Granite Ridge portfolio to prove sharing spares across plants" />
      </div>
    </Slide>,

    <div key="end" className="flex h-full flex-col justify-center">
      <h2 className="text-5xl font-semibold tracking-tight">Know before it stops.</h2>
      <p className="mt-6 text-2xl text-muted">Records first. A small box where it matters. Statistics that say why.</p>
    </div>,

    <div key="appendix" className="flex h-full flex-col justify-center">
      <div className="text-sm font-semibold uppercase tracking-wider text-accent">Appendix</div>
      <h2 className="mt-3 text-5xl font-semibold tracking-tight">For questions</h2>
      <p className="mt-6 text-2xl text-muted">Downtime, the model, proof, market, competition, pricing, risks, every assumption.</p>
    </div>,

    <Slide key="downtime" kicker="Why it matters" title="One failure, one line, one week of lost output" owner="Financial slides: Brandon">
      <div className="grid grid-cols-3 gap-10 pt-6">
        <Big n="176 h" label="Toledo Line 2 down if its drive fails today (worst case)" />
        <Big n="40 h" label="with the spare already sitting at Fort Wayne" />
        <Big n="~$84k" label="lost output at stake in that one event" />
      </div>
      <p className="mt-10 text-xl text-muted">Lost revenue is what plants feel. We count only rescues we actually found.</p>
    </Slide>,

    <Slide key="solution" kicker="The solution" title="One registry of every part, its health, and what to do">
      <div className="flex h-full items-center justify-between gap-4 text-xl">
        {["Plant records + label photos", "Registry: every part identified", "Health score per part", "Order by / where to buy"].map((t, i, a) => (
          <div key={t} className="flex items-center gap-4"><div className="rounded-xl border border-line bg-bg px-5 py-6 text-center font-semibold">{t}</div>{i < a.length - 1 && <span className="text-3xl text-muted">→</span>}</div>
        ))}
      </div>
    </Slide>,

    <Slide key="health" kicker="The model" title="Every piece of evidence becomes one probability: will it survive the year?">
      <HealthFlow />
    </Slide>,

    <Slide key="anomaly" kicker="The model" title="Statistics flag a failing fan the week it starts running hot">
      <div className="h-[85%]"><AnomalyChart data={data.series} /></div>
      <div className="text-sm text-muted">Toledo line-stopper drive · temperature vs. what&apos;s expected for its load and room temperature · simulated sensor data</div>
    </Slide>,

    <Slide key="proof" kicker="Proof" title="We built it this weekend, and measured it">
      <div className="grid grid-cols-3 gap-10 pt-6">
        <Big n="127 / 129" label="part numbers read exactly from label photos (the 2 misses were flagged, not guessed)" />
        <Big n="100%" label="precision matching parts to the catalog (98% recall)" />
        <Big n="4 / 4" label="planted failures caught by the health model, 1 false alarm in ~40" />
      </div>
    </Slide>,

    <Slide key="market" kicker="Customer" title="Multi-plant manufacturers and PE portfolios">
      <div className="grid grid-cols-3 gap-10 pt-6">
        <Big n="8–18k" label="US multi-plant manufacturers (recurring accounts)" />
        <Big n="2–4k" label="PE-owned manufacturers in hold" />
        <Big n="~1k / yr" label="acquisitions that need an equipment review: one way in" />
      </div>
    </Slide>,

    <Slide key="competition" kicker="Competition" title="Everyone values the machine. No one keeps the part record.">
      <div className="grid grid-cols-4 gap-4 pt-4 text-lg">
        {[["Appraisers", "value machines, not parts"], ["Operations diligence", "one-time, not kept up"], ["Controls audits", "one brand at a time"], ["Monitoring vendors", "~$900 per machine per year"]].map(([t, d]) => (
          <div key={t} className="rounded-xl border border-line bg-bg p-5"><div className="font-semibold">{t}</div><div className="mt-2 text-base text-muted">{d}</div></div>
        ))}
      </div>
      <p className="mt-8 text-xl">We don&apos;t replace appraisers or engineers. They keep the sign-off; we give them the record.</p>
    </Slide>,

    <Slide key="pricing" kicker="The business" title="How we charge" owner="Financial slides: Brandon">
      <div className="grid grid-cols-2 gap-10 pt-4 text-xl">
        <div className="rounded-xl border border-line bg-bg p-6"><div className="text-3xl font-semibold">Per plant / year</div><div className="mt-2 text-muted">registry, health scores, sourcing</div><div className="mt-4 text-muted">[Brandon: fixed fee]</div></div>
        <div className="rounded-xl border border-line bg-bg p-6"><div className="text-3xl font-semibold">Per device / year</div><div className="mt-2 text-muted">X-Ray Monitor, only on line stoppers</div><div className="mt-4 text-muted">[Brandon: fixed fee]</div></div>
      </div>
      <p className="mt-8 text-xl">No share of &quot;savings&quot;: savings can&apos;t be audited, so a share of them is a conflict of interest.</p>
    </Slide>,

    <Slide key="objections" kicker="Risks" title="What could go wrong, and how we would know">
      <div className="space-y-5 pt-2 text-xl">
        <div><b>&quot;Plants have terrible data.&quot;</b> <span className="text-muted">We start from what exists; the device fills gaps. Test: pilot plant coverage.</span></div>
        <div><b>&quot;The health score is unproven.&quot;</b> <span className="text-muted">True. Calibrate on 10 cabinets for 90 days against real failures.</span></div>
        <div><b>&quot;Plants won&apos;t install hardware.&quot;</b> <span className="text-muted">Read-only, clamp-on, planned stop. Test: install time in the pilot.</span></div>
      </div>
    </Slide>,

    <Slide key="assumptions" kicker="Appendix" title="Every assumption, and why">
      <div className="h-[88%] overflow-auto pr-2">
      <table className="w-full text-[13px]">
        <thead><tr className="text-left text-muted"><th className="pb-1 pr-3 font-medium">Assumption</th><th className="pb-1 pr-3 font-medium">Value</th><th className="pb-1 font-medium">Justification</th></tr></thead>
        <tbody>
          {ASSUMPTIONS.map((a) => (
            <tr key={a.what} className="border-t border-line align-top">
              <td className="py-1 pr-3 font-medium">{a.what}</td>
              <td className="tabular py-1 pr-3 whitespace-nowrap">{a.value}</td>
              <td className="py-1 text-muted">{a.why}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
      <div className="mt-2 text-xs text-muted">Financial assumptions: Brandon · every market number and its source: Sources tab</div>
    </Slide>,
  ];

  const [i, setI] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const full = (slides[i] as React.ReactElement).key === "demo";
  const go = useCallback((d: number) => setI((x) => Math.min(slides.length - 1, Math.max(0, x + d))), [slides.length]);
  // Slides are laid out on a fixed 16:9 canvas and scaled to fit, so full screen enlarges everything (like PowerPoint).
  const [box, setBox] = useState({ k: 1, x: 0, y: 0 });
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const fit = () => {
      const { width, height } = el.getBoundingClientRect();
      const k = Math.min(width / W, height / H);
      setBox({ k, x: (width - W * k) / 2, y: (height - H * k) / 2 });
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el);
    return () => ro.disconnect();
  }, [full]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (["ArrowRight", "PageDown", " "].includes(e.key)) { e.preventDefault(); go(1); }
      if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); go(-1); }
      if (e.key === "f") ref.current?.requestFullscreen?.().catch(() => {});
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go]);

  return (
    <div className="relative left-1/2 w-[calc(100vw-2rem)] -translate-x-1/2">
      <div ref={ref} className={`relative mx-auto overflow-hidden rounded-2xl border border-line bg-surface shadow-sm [&:fullscreen]:rounded-none ${full ? "h-[calc(100vh-130px)] w-full p-3 [&:fullscreen]:p-4" : "aspect-video w-full max-w-[calc((100vh-170px)*16/9)] "}`}>
        {full ? slides[i] : (
          <div className="absolute left-0 top-0 p-12" style={{ width: W, height: H, transform: `translate(${box.x}px, ${box.y}px) scale(${box.k})`, transformOrigin: "top left" }}>
            {slides[i]}
          </div>
        )}
        <div className="absolute bottom-0 left-0 h-1 bg-accent transition-all" style={{ width: `${((i + 1) / slides.length) * 100}%` }} />
      </div>
      <div className={`mx-auto mt-3 flex items-center ${full ? "" : "max-w-[calc((100vh-170px)*16/9)]"} justify-between text-sm text-muted`}>
        <button onClick={() => go(-1)} className="rounded px-3 py-1.5 hover:text-ink" disabled={i === 0}>← Back</button>
        <span className="tabular">{i + 1} / {slides.length} · arrow keys to move · F for full screen</span>
        <button onClick={() => go(1)} className="rounded px-3 py-1.5 hover:text-ink" disabled={i === slides.length - 1}>Next →</button>
      </div>
    </div>
  );
}
