"use client";

// Cost after the sale per unit built: stacked bars (spares, warranty). Build cost is shown separately,
// because at ~100x the size it would hide the after-sale costs that are the story.
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type CostRow = { product: string; spares: number; warranty: number };

const usd = (v: number) => (v >= 1000 ? `$${(v / 1000).toFixed(1)}k` : `$${v.toFixed(0)}`);

export function CostChart({ data }: { data: CostRow[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
          <XAxis dataKey="product" tick={{ fill: "var(--muted)", fontSize: 12 }} axisLine={{ stroke: "var(--line)" }} tickLine={false} />
          <YAxis tickFormatter={usd} tick={{ fill: "var(--muted)", fontSize: 12 }} axisLine={false} tickLine={false} width={60} />
          <Tooltip formatter={(v: number) => `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
                   contentStyle={{ border: "1px solid var(--line)", borderRadius: 4, fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="spares" name="Spares / unit" stackId="c" fill="var(--warn)" />
          <Bar dataKey="warranty" name="Warranty / unit" stackId="c" fill="var(--alert)" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
