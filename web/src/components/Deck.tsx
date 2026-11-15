"use client";

import { Fragment, useCallback, useEffect, useRef, useState } from "react";

export type DeckData = {
  companies: {
    name: string;
    owned: boolean;
    since: string;
    deal: string;
    plants: { name: string; state: string; employees: number; lines: number; machines: number }[];
  }[];
  toledo: { levers: Record<string, number>; total: number; fee: number; payback: number; dtBase: number; dtLow: number; dtHigh: number } | null;
};

const k = (v: number) => (v >= 1000 ? `$${(v / 1000).toFixed(v >= 100000 ? 0 : 1).replace(/\.0$/, "")}k` : `$${Math.round(v)}`);

// One idea per slide: a headline, at most one visual or 3 short lines. Details live in the live demo, not on slides.
// "V" = found with Velocity research: say how Velocity helped when you reach it.
function V() {
  return <sup title="Found with Velocity research" className="ml-0.5 inline-flex h-3 w-3 items-center justify-center rounded-sm bg-accent-soft align-super text-[7px] font-bold leading-none tracking-normal text-accent">V</sup>;
}

function Slide({ kicker, title, children, owner, v }: { kicker?: string; title: string; children?: React.ReactNode; owner?: string; v?: boolean }) {
  return (
    <div className="flex h-full flex-col">
      {kicker && <div className="text-sm font-semibold uppercase tracking-wider text-accent">{kicker}</div>}
      <h2 className="mt-2 text-balance text-4xl font-semibold leading-tight tracking-tight">{title}{v && <V />}</h2>
      <div className="mt-6 min-h-0 flex-1">{children}</div>
      {owner && <div className="text-right text-xs text-muted">{owner}</div>}
    </div>
  );
}


// Data collection workflow (three sources): each source, when it happens, what we collect, and what it changes in the health score.
function Ladder() {
  const steps = [
    { n: "1", t: "Label photos", when: "day 1 · every cabinet", got: "part number, maker, date code", feeds: <>what the part is → <b>rated life</b> from its manual, discontinued or not; date code = <b>minimum age</b></> },
    { n: "2", t: "Plant records", v: true, when: "week 1 · where they exist (~28%)", got: "install dates from the maintenance system and purchase orders", feeds: <>true <b>age</b> → how far along its wear-out curve the part is</> },
    { n: "3", t: "Cabinet Monitor", when: "continuous · line-stopper cabinets", got: "temperature, motor current, drive fault logs, fan + capacitor life", feeds: <><b>heat</b> ages parts faster (2× per +10 °C); <b>anomalies</b> raise failure risk up to 20×; each <b>fault</b> +30%</> },
  ];
  return (
    <div className="grid h-full grid-cols-[1fr_220px] gap-6">
      <div className="flex flex-col">
        <div className="grid grid-cols-[220px_1fr_1.4fr] gap-5 pb-2 text-xs font-semibold uppercase tracking-wider text-muted">
          <span>Source · when</span><span>What we collect</span><span>What it changes in the score</span>
        </div>
        {steps.map((s) => (
          <div key={s.n} className="grid flex-1 grid-cols-[220px_1fr_1.4fr] items-center gap-5 border-t border-line">
            <div className="flex items-center gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent text-base font-semibold text-surface">{s.n}</span>
              <div>
                <div className="text-xl font-semibold leading-tight">{s.t}{"v" in s && s.v && <V />}</div>
                <div className="mt-0.5 text-sm leading-snug text-muted">{s.when}</div>
              </div>
            </div>
            <div className="text-base leading-snug text-muted">{s.got}</div>
            <div className="flex items-center gap-3 text-[17px] leading-snug">
              <span className="flex-1">{s.feeds}</span>
              <span className="text-xl text-accent">→</span>
            </div>
          </div>
        ))}
      </div>
      <div className="flex flex-col justify-center rounded-2xl bg-accent p-5 text-surface">
        <div className="text-xs font-semibold uppercase tracking-wider opacity-80">Health score</div>
        <div className="tabular mt-1 text-5xl font-semibold">0–100</div>
        <div className="mt-3 text-lg leading-snug">= the chance the part survives the next 12 months</div>
        <div className="mt-4 border-t border-surface/30 pt-3 text-[15px] leading-snug opacity-90">
          plus <b>years left</b>, and a <b>confidence</b>: the more sources a part has, the tighter its range
        </div>
      </div>
    </div>
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


const W = 1120;
const H = 630;

export function Deck({ data }: { data: DeckData }) {
  const slides: React.ReactNode[] = [
    <div key="title" className="flex h-full flex-col justify-center">
      <div className="text-sm font-semibold uppercase tracking-wider text-accent">Kearney × PERLab</div>
      <h1 className="mt-3 text-6xl font-semibold tracking-tight">Equipment Health Index</h1>
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
              ["$1.4T", "lost to unplanned downtime every year by the world's 500 largest companies (11% of revenue)"],
              ["55%", "of plants have a plan for obsolete parts. The rest do not."],
              ["44%", "of plants have an equipment interruption every month"],
              ["10–24 wks", "to get a new controller; a discontinued one is resale-only"],
            ].map(([n, d]) => (
              <div key={n}>
                <div className="tabular text-4xl font-semibold tracking-tight text-accent">{n}<V /></div>
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

    <Slide key="collect" kicker="The solution" title="Data Collection Workflow">
      <Ladder />
    </Slide>,

    <Slide key="device" kicker="The hardware" title="Cabinet Monitor: one small box per critical cabinet">
      <div className="grid h-full grid-cols-[1.5fr_1fr] gap-8">
        <figure className="flex min-h-0 flex-col">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/xray-monitor.png" alt="Concept image of the Cabinet Monitor clipped to a DIN rail in a control cabinet" className="min-h-0 flex-1 rounded-xl object-cover" />
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
              <div className="text-xl font-semibold">{t}{t.startsWith("~$185") && <V />}</div>
              <div className="text-base text-muted">{d}</div>
            </div>
          ))}
        </div>
      </div>
    </Slide>,

    <Slide key="diagram" kicker="The hardware" title="How the Cabinet Monitor works" v>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/cabinet-monitor-diagram.png" alt="System block diagram of the Cabinet Monitor" className="h-full w-full object-contain object-top" />
    </Slide>,

    <div key="demo" className="flex h-full flex-col">
      <div className="flex items-baseline justify-between px-1 pb-2">
        <span className="text-sm font-semibold uppercase tracking-wider text-accent">Live demo · Granite Ridge Capital</span>
        <span className="text-xs text-muted">click inside to drive the app · click outside, then arrows to leave</span>
      </div>
      <iframe src="/" className="min-h-0 w-full flex-1 rounded-xl border border-line bg-bg" title="Equipment Health Index live demo" />
    </div>,

    <Slide key="savings" kicker="Financials · Cost savings" title="What we count, and what we only show">
      {data.toledo ? (() => { const t = data.toledo; return (
      <div className="flex h-full flex-col gap-4">
        <div className="grid min-h-0 flex-1 grid-cols-2 gap-5">
          <div className="flex flex-col rounded-2xl border-t-4 border-accent bg-bg p-5">
            <div className="flex items-center gap-2 text-xl font-semibold">Direct savings <span className="rounded bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">auditable</span><V /></div>
            <div className="tabular mt-1 text-5xl font-semibold tracking-tight text-accent">{k(t.total)} / yr</div>
            <div className="text-sm text-muted">Toledo, each line traced to parts in the registry</div>
            <div className="mt-3 text-[15px]">
              {[["Spares carrying cost", t.levers.carrying_cost_avoided], ["Planned instead of emergency buys", t.levers.planned_vs_emergency], ["Purchases a sister plant's spare avoids", t.levers.sister_spare_purchases_avoided], ["Rush premiums", t.levers.rush_premiums_avoided]].map(([l, v]) => (
                <div key={l as string} className="flex justify-between border-b border-line py-1.5"><span>{l}</span><span className="tabular">{k(v as number)}</span></div>
              ))}
            </div>
            <div className="mt-2 text-[15px]">+ <b>{k(t.levers.spares_inventory_released)}</b> of idle spares cash freed once</div>
          </div>
          <div className="flex flex-col rounded-2xl border-2 border-dashed border-line p-5">
            <div className="flex items-center gap-2 text-xl font-semibold">Downtime avoided <span className="rounded bg-warn-soft px-2 py-0.5 text-xs font-semibold text-warn">estimate</span></div>
            <div className="tabular mt-1 text-5xl font-semibold tracking-tight text-muted">~${Math.round(t.dtBase / 1000)}k / yr</div>
            <div className="text-sm text-muted">Toledo, range ${Math.round(t.dtLow / 1000)}–{Math.round(t.dtHigh / 1000)}k</div>
            <pre className="mt-3 rounded bg-bg px-3 py-2 font-mono text-[13px] leading-relaxed">{`chance it fails × hours the spare saves
× lost margin per hour
× share of output never made up`}</pre>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-[15px]">
              <li>Only spare rescues the scan actually found</li>
              <li>One failure per spare, over 3 years, at 10%</li>
              <li>Outage capped at 10–25 days; 40–80% never made up</li>
            </ul>
          </div>
        </div>
        <div className="rounded-xl border-l-4 border-accent bg-accent-soft px-5 py-3 text-[17px]">
          <b>The business case uses only the left side.</b> Downtime depends on judgment calls, so we show it conservatively and never price it.
        </div>
      </div>); })() : <div className="text-muted">Start the API to load Toledo&apos;s numbers.</div>}
    </Slide>,

    <Slide key="model" kicker="Financials · Business model" title="We charge for what the customer can count, not for what we say they saved">
      <div className="flex h-full flex-col gap-3">
        <div className="grid grid-cols-[1fr_auto_1fr_auto_1fr] items-stretch gap-3">
          {[
            { n: "1 · One-time", t: "Onboard a plant", d: "First scan: registry, line stoppers, spending by year", p: "$1–2k", u: "flat, per plant" },
            { n: "2 · Yearly", t: "Registry subscription", d: "Kept current: lifecycle alerts, rescans, spares on every plant's shelf", p: "$4–10k", u: "per plant, tiered by the number of critical parts", hi: true },
            { n: "3 · Monthly", t: "Sensors", d: "Clip-on sensors on the riskiest parts, hardware included", p: "$ / point", u: "per monitored point", tag: "price to set" },
          ].map((c, i, arr) => (
            <Fragment key={c.t}>
              <div className={`flex flex-col rounded-2xl p-4 ${c.hi ? "bg-accent text-surface" : "bg-bg"}`}>
                <div className={`text-xs font-semibold uppercase tracking-wider ${c.hi ? "opacity-85" : "text-accent"}`}>{c.n}</div>
                <div className="mt-1 text-xl font-semibold">{c.t}</div>
                <div className={`mt-1 text-[15px] leading-snug ${c.hi ? "opacity-90" : "text-muted"}`}>{c.d}</div>
                <div className={`tabular mt-auto pt-2 text-4xl font-semibold tracking-tight ${c.hi ? "" : "text-accent"}`}>{c.p}</div>
                <div className={`text-sm ${c.hi ? "opacity-85" : "text-muted"}`}>{c.u}{c.tag && <span className="ml-2 rounded bg-warn-soft px-1.5 py-0.5 text-xs font-semibold text-warn">{c.tag}</span>}</div>
              </div>
              {i < arr.length - 1 && <span className="self-center text-2xl text-accent">→</span>}
            </Fragment>
          ))}
        </div>
        <div className="mb-2 grid flex-1 grid-cols-2 gap-4">
          <div className="flex flex-col justify-center rounded-2xl border-l-4 border-accent bg-accent-soft px-5 py-3 text-[17px] leading-snug">
            {data.toledo ? <><b>Toledo pays {k(data.toledo.fee)} a year and saves {k(data.toledo.total)}: paid back in {data.toledo.payback} months.</b> </> : null}
            The fee stays fixed whatever we report, so we never judge our own fee.
          </div>
          <div className="flex flex-col rounded-2xl bg-ink px-5 py-3 text-surface">
            <div className="text-xs font-semibold uppercase tracking-wider opacity-70">A typical mid-market PE portfolio</div>
            <div className="tabular mt-1 text-4xl font-semibold tracking-tight">$1–4M <span className="text-xl opacity-80">a year</span></div>
            <div className="mt-1 text-sm leading-snug opacity-85">10–20 portfolio companies · 30–100 plants · registry + sensors on ~60 line-stopper cabinets per plant</div>
            <div className="mt-auto border-t border-surface/25 pt-2 text-sm leading-snug">
              <b>25,800</b> US plants with 100+ employees · registry alone: <b>$7.6M</b> a year at 5% of them, <b>$152M</b> at all
            </div>
          </div>
        </div>
      </div>
    </Slide>,

    <div key="next" className="flex h-full flex-col justify-center">
      <div className="text-sm font-semibold uppercase tracking-wider text-accent">Next</div>
      <h2 className="mt-2 text-5xl font-semibold tracking-tight">Run 3 paid plant pilots and 1 portfolio</h2>
      <div className="mt-10 grid grid-cols-4 gap-6">
        {[
          { t: "Now", d: <>Photos → registry → health, sourcing, savings. <b>Built.</b></>, bar: "bg-ink" },
          { t: "Pilots", d: "Site walks at real plants; first sensors on the riskiest cabinets", bar: "bg-accent" },
          { t: "Then", d: "Live registry per plant, kept current by the hardware", bar: "bg-accent" },
          { t: "Later", d: "Platform: shared spares and buying across a fund's companies", bar: "bg-line" },
        ].map((c) => (
          <div key={c.t}>
            <div className={`h-1 rounded ${c.bar}`} />
            <div className="mt-3 text-xl font-semibold">{c.t}</div>
            <div className="mt-1 text-[17px] leading-snug">{c.d}</div>
          </div>
        ))}
      </div>
      <p className="mt-10 max-w-4xl text-lg text-muted">In the pilots we measure three things: accuracy on real worn nameplates, which findings changed a decision, and whether the owner pays to keep it running.</p>
    </div>,

    <div key="appendix" className="flex h-full flex-col">
      <div className="flex items-baseline justify-between px-1 pb-2">
        <span className="text-sm font-semibold uppercase tracking-wider text-accent">Appendix · every formula, assumption and source</span>
        <span className="text-xs text-muted">search on the left · click outside, then arrows to leave</span>
      </div>
      <iframe src="/appendix" className="min-h-0 w-full flex-1 rounded-xl border border-line bg-bg" title="Appendix" />
    </div>,
  ];

  const [i, setI] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const full = ["demo", "appendix"].includes(String((slides[i] as React.ReactElement).key));
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
