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

// Data collection workflow (three sources): each source, when it happens, what we collect, and what it changes in the health score.
function Ladder() {
  const steps = [
    { n: "1", t: "Label photos", when: "day 1 · every cabinet", got: "part number, maker, date code", feeds: <>what the part is → <b>rated life</b> from its manual, discontinued or not; date code = <b>minimum age</b></> },
    { n: "2", t: "Plant records", when: "week 1 · where they exist (~28%)", got: "install dates from the maintenance system and purchase orders", feeds: <>true <b>age</b> → how far along its wear-out curve the part is</> },
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
                <div className="text-xl font-semibold leading-tight">{s.t}</div>
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
              <div className="text-xl font-semibold">{t}</div>
              <div className="text-base text-muted">{d}</div>
            </div>
          ))}
        </div>
      </div>
    </Slide>,

    <Slide key="diagram" kicker="The hardware" title="How the Cabinet Monitor works">
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

    <Slide key="ask" kicker="Recommendation" title="3 paid plant pilots + 1 portfolio">
      <div className="grid grid-cols-3 gap-10 pt-6">
        <Big n="90 days" label="per pilot: registry + Cabinet Monitors on line stoppers" />
        <Big n="10" label="cabinets monitored per plant to calibrate the score" />
        <Big n="1" label="Granite Ridge portfolio to prove sharing spares across plants" />
      </div>
    </Slide>,

    <div key="end" className="flex h-full flex-col justify-center">
      <h2 className="text-5xl font-semibold tracking-tight">Know before it stops.</h2>
      <p className="mt-6 text-2xl text-muted">Records first. A small box where it matters. Statistics that say why.</p>
    </div>,

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
