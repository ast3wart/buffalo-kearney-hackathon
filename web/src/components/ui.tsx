// Shared building blocks. Use these on every screen so both threads look like one app.
import type { ReactNode } from "react";

export function PageHeader({ title, subtitle }: { title: string; subtitle?: ReactNode }) {
  return (
    <div className="mb-6 space-y-1">
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      {subtitle && <p className="text-sm text-muted">{subtitle}</p>}
    </div>
  );
}

export function Card({ title, children, tone, className = "" }: { title?: string; children: ReactNode; tone?: "alert"; className?: string }) {
  return (
    <section className={`rounded border bg-surface p-5 ${tone === "alert" ? "border-alert" : "border-line"} ${className}`}>
      {title && <h2 className="mb-3 text-xs font-medium uppercase tracking-wider text-muted">{title}</h2>}
      {children}
    </section>
  );
}

export function Stat({ label, value, tone }: { label: string; value: ReactNode; tone?: "alert" | "ok" | "warn" }) {
  const color = tone === "alert" ? "text-alert" : tone === "ok" ? "text-ok" : tone === "warn" ? "text-warn" : "text-ink";
  return (
    <div className="space-y-0.5">
      <div className={`tabular text-2xl font-semibold ${color}`}>{value}</div>
      <div className="text-xs text-muted">{label}</div>
    </div>
  );
}

export function PartNo({ children }: { children: ReactNode }) {
  return <span className="font-mono text-[0.85em]">{children}</span>;
}

export function Todo({ owner, children }: { owner: string; children: ReactNode }) {
  return (
    <div className="rounded border border-dashed border-line p-4 text-sm text-muted">
      <b className="text-ink">{owner}:</b> {children}
    </div>
  );
}

// Number formatting: use these everywhere ($1.2M, 3.0×, 74%)
export const fmt = {
  usd: (v: number) =>
    v >= 1e6 ? `$${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `$${(v / 1e3).toFixed(0)}K` : `$${v.toFixed(2)}`,
  pct: (v: number) => `${Math.round(v * 100)}%`,
  ratio: (v: number) => `${v.toFixed(1)}×`,
  rate: (v: number) => `${v.toFixed(1)} / 1,000`,
};

const STATUS: Record<string, string> = {
  discontinued: "bg-alert-soft text-alert",
  end_of_life: "bg-warn-soft text-warn",
  active_mature: "bg-warn-soft text-warn",
  active: "bg-accent-soft text-accent",
  unknown: "bg-bg text-muted",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-block rounded px-1.5 py-0.5 text-[11px] font-medium ${STATUS[status] ?? STATUS.unknown}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

export function Pill({ children, tone }: { children: ReactNode; tone?: "alert" | "warn" | "ok" | "muted" }) {
  const c = tone === "alert" ? "border-alert text-alert" : tone === "warn" ? "border-warn text-warn" : tone === "ok" ? "border-ok text-ok" : "border-line text-muted";
  return <span className={`inline-block rounded-full border px-2 py-0.5 text-[11px] ${c}`}>{children}</span>;
}

export function Pending({ what, detail }: { what: string; detail?: string }) {
  return (
    <div className="rounded border border-dashed border-line p-4 text-sm text-muted">
      <b className="text-ink">{what}</b> appears here once the money model has run.
      {detail && <div className="mt-1 font-mono text-[11px]">{detail}</div>}
    </div>
  );
}

const HEALTH: Record<string, [string, string]> = {
  working: ["Working", "bg-accent-soft text-accent"],
  replace_soon: ["Replace soon", "bg-warn-soft text-warn"],
  replace_asap: ["Replace ASAP", "bg-alert-soft text-alert"],
  unidentified: ["Unidentified", "bg-bg text-muted"],
};

export function HealthBadge({ health }: { health?: string | null }) {
  const [label, cls] = HEALTH[health ?? "unidentified"] ?? HEALTH.unidentified;
  return <span className={`inline-block whitespace-nowrap rounded px-1.5 py-0.5 text-[11px] font-medium ${cls}`}>{label}</span>;
}

const SRC: Record<string, string> = {
  diagnostics: "Self-reported diagnostics",
  records: "Plant records (part install date)",
  machine_records: "Plant records (machine install date)",
  label_date_code: "Label date code (age floor)",
  thermal_continuous: "Cabinet thermal camera (continuous)",
  thermal_snapshot: "Thermal snapshot (walkthrough)",
  current_signature: "Motor current sensor",
  thermal_trend: "90-day temperature history (statistical anomaly detection)",
};
export const sourceLabel = (s: string) => SRC[s] ?? s;

export function HealthScore({ score, confidence }: { score?: number | null; confidence?: string | null }) {
  if (score === null || score === undefined) return <span className="text-xs text-muted">no data</span>;
  const c = score >= 60 ? "text-ok" : score >= 30 ? "text-warn" : "text-alert";
  return (
    <span className="whitespace-nowrap">
      <b className={`tabular text-lg ${c}`}>{Math.round(score)}</b>
      <span className="text-xs text-muted">/100{confidence ? ` · ${confidence} confidence` : ""}</span>
    </span>
  );
}

export function LifeBar({ pct }: { pct?: number | null }) {
  if (pct === null || pct === undefined) return <span className="text-xs text-muted">n/a</span>;
  const w = Math.min(100, Math.round(pct * 100));
  const color = pct >= 1 ? "bg-alert" : pct >= 0.75 ? "bg-warn" : "bg-accent";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded bg-line"><div className={`h-full ${color}`} style={{ width: `${w}%` }} /></div>
      <span className="tabular text-xs">{Math.round(pct * 100)}%</span>
    </div>
  );
}
