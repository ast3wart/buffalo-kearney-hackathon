"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Row = { year: number; capex_low: number; capex_high: number; capex_type?: string };

export function CapexChart({ rows }: { rows: Row[] }) {
  const byYear = new Map<number, { year: number; low: number; spread: number }>();
  for (const r of rows) {
    const cur = byYear.get(r.year) ?? { year: r.year, low: 0, spread: 0 };
    cur.low += r.capex_low;
    cur.spread += r.capex_high - r.capex_low;
    byYear.set(r.year, cur);
  }
  const data = [...byYear.values()].sort((a, b) => a.year - b.year);
  const k = (v: number) => (v >= 1e6 ? `$${(v / 1e6).toFixed(1)}M` : `$${Math.round(v / 1e3)}k`);
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
        <CartesianGrid vertical={false} stroke="var(--line)" />
        <XAxis dataKey="year" tickLine={false} axisLine={false} fontSize={12} />
        <YAxis tickFormatter={k} tickLine={false} axisLine={false} fontSize={12} width={56} />
        <Tooltip
          cursor={{ fill: "var(--line)", opacity: 0.4 }}
          contentStyle={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 6, fontSize: 12 }}
          labelStyle={{ color: "var(--ink)", fontWeight: 600 }}
          itemStyle={{ color: "var(--ink)" }}
          formatter={(v: number, n: string, item: { payload?: { low: number; spread: number } }) =>
            n === "low" ? [k(v), "Low estimate"] : [k((item.payload?.low ?? 0) + v), "High estimate"]}
        />
        <Bar dataKey="low" stackId="a" fill="var(--alert)" />
        <Bar dataKey="spread" stackId="a" fill="var(--alert-soft)" />
      </BarChart>
    </ResponsiveContainer>
  );
}
