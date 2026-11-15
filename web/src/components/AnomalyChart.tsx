"use client";

import { CartesianGrid, Line, LineChart, ReferenceArea, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type SeriesPoint = { day: number; residual_c: number; ewma_c: number | null; limit_c: number; baseline: boolean };

export function AnomalyChart({ data }: { data: SeriesPoint[] }) {
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
