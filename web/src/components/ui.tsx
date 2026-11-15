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

export function Card({ title, children, tone }: { title?: string; children: ReactNode; tone?: "alert" }) {
  return (
    <section className={`rounded border bg-surface p-5 ${tone === "alert" ? "border-alert" : "border-line"}`}>
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
      <b className="text-ink">{what}</b> appears here when Brandon&apos;s money model lands.
      {detail && <div className="mt-1 font-mono text-[11px]">{detail}</div>}
    </div>
  );
}
