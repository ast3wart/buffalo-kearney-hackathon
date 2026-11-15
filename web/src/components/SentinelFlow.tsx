// How Cabinet Sentinel turns raw signals into a decision: a vertical flow with line icons (no toy shapes).
const I = {
  thermal: (
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0zM11.5 9v7" />
  ),
  current: <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />,
  chip: (
    <>
      <rect x="5" y="5" width="14" height="14" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4" />
    </>
  ),
  edge: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="M7 8h10M7 12h4M7 16h2" />
      <circle cx="16" cy="15" r="1.5" />
    </>
  ),
  stats: <path d="M3 3v18h18M7 14l4-4 3 3 6-7" />,
  heart: <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z" />,
  cart: (
    <>
      <circle cx="9" cy="21" r="1" />
      <circle cx="20" cy="21" r="1" />
      <path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6" />
    </>
  ),
};

function Icon({ d, tone = "accent" }: { d: React.ReactNode; tone?: "accent" | "ink" }) {
  return (
    <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${tone === "accent" ? "bg-accent-soft text-accent" : "bg-ink text-surface"}`}>
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">{d}</svg>
    </span>
  );
}

function Step({ icon, title, sub, tone }: { icon: React.ReactNode; title: string; sub: string; tone?: "accent" | "ink" }) {
  return (
    <div className="flex items-center gap-3">
      <Icon d={icon} tone={tone} />
      <div className="min-w-0">
        <div className="text-[15px] font-semibold leading-tight">{title}</div>
        <div className="text-[13px] leading-snug text-muted">{sub}</div>
      </div>
    </div>
  );
}

const Down = () => <div className="ml-[17px] h-2.5 w-0.5 bg-line" />;

export function SentinelFlow() {
  return (
    <div className="flex h-full flex-col justify-center">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted">Inside the cabinet</div>
      <div className="grid gap-1.5">
        <Step icon={I.thermal} title="Thermal camera" sub="every part's temperature, at once" />
        <Step icon={I.current} title="Current clamps" sub="motor health, from the motor leads" />
        <Step icon={I.chip} title="Built-in diagnostics" sub="newer drives & PLCs, read-only" />
      </div>
      <Down />
      <Step icon={I.edge} title="Sentinel edge box" sub="one summary a day, one way out" tone="ink" />
      <Down />
      <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted">In Equipment X-Ray</div>
      <div className="grid gap-1.5">
        <Step icon={I.stats} title="Anomaly statistics" sub="shift, drift, peers, motor current" />
        <Step icon={I.heart} title="Health score 0–100" sub="+ years left + confidence" />
        <Step icon={I.cart} title="Order by / where to buy" sub="before it stops the line" />
      </div>
    </div>
  );
}
