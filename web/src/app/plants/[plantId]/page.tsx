import Link from "next/link";
import { getJSON, tryJSON, usd } from "@/lib/api";
import { Card, HealthBadge, PageHeader, Pending, Pill, Stat } from "@/components/ui";
import { CapexChart } from "@/components/CapexChart";

type MachineRow = {
  machine_id: string; make: string; model: string; machine_type: string; year_built: number; criticality: string;
  parts: number; asap: number; soon: number; risk: string; value_low: number; value_high: number;
};
type Lines = {
  plant: { plant_id: string; plant_name: string; state: string; status: string; employees: number };
  lines: { line_id: string; line_name: string; product: string; machines: MachineRow[]; asap: number; soon: number; value_low: number; value_high: number }[];
  health: Record<string, number>;
  machines: number;
};
type CapexRow = { year: number; capex_low: number; capex_high: number; capex_type: string };

export default async function PlantPage({ params }: { params: Promise<{ plantId: string }> }) {
  const { plantId } = await params;
  const [p, capex] = await Promise.all([
    getJSON<Lines>(`/plants/${plantId}/lines`),
    tryJSON<{ capex_by_year: CapexRow[] }>(`/plants/${plantId}/capex`),
  ]);
  const value = p.lines.reduce((a, l) => [a[0] + l.value_low, a[1] + l.value_high], [0, 0]);
  return (
    <>
      <PageHeader
        title={`${p.plant.plant_name}, ${p.plant.state}`}
        subtitle={<>{p.plant.employees} employees · {p.lines.length} lines · {p.machines} machines {p.plant.status === "target" && <Pill tone="warn">acquisition target</Pill>}</>}
      />
      <div className="grid gap-4 md:grid-cols-4">
        <Card><Stat label="parts to replace ASAP" value={p.health.replace_asap ?? 0} tone="alert" /></Card>
        <Card><Stat label="parts to replace soon" value={p.health.replace_soon ?? 0} tone="warn" /></Card>
        <Card><Stat label="parts working" value={p.health.working ?? 0} tone="ok" /></Card>
        <Card><Stat label="machine replacement value" value={`${usd(value[0])}–${usd(value[1])}`} /></Card>
      </div>
      <div className="mt-4">
        <Card title="CapEx cliff · equipment spending needed by year">
          {capex.data ? <CapexChart rows={capex.data.capex_by_year} /> : <Pending what="The CapEx cliff" detail={capex.pending ?? capex.error} />}
        </Card>
      </div>
      <div className="mt-6 space-y-4">
        {p.lines.map((l) => (
          <Card key={l.line_id} title={`${l.line_name} · ${l.product}`}>
            <div className="mb-2 flex gap-2 text-xs">
              {l.asap > 0 && <Pill tone="alert">{l.asap} replace ASAP</Pill>}
              {l.soon > 0 && <Pill tone="warn">{l.soon} replace soon</Pill>}
              <span className="text-muted">machines worth {usd(l.value_low)}–{usd(l.value_high)}</span>
            </div>
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted">
                <tr><th className="pb-2">Machine</th><th>Parts</th><th>Risk</th><th>Replacement value</th><th></th></tr>
              </thead>
              <tbody>
                {l.machines.map((m) => (
                  <tr key={m.machine_id} className="border-t border-line">
                    <td className="py-2">
                      <Link href={`/machines/${m.machine_id}`} className="font-medium hover:underline">{m.make} {m.model}</Link>{" "}
                      {m.criticality === "line_stop" && <Pill tone="alert">line stopper</Pill>}
                      <div className="text-xs text-muted">{m.machine_type.replace("_", " ")} · built {m.year_built}</div>
                    </td>
                    <td className="tabular">{m.parts}</td>
                    <td><HealthBadge health={m.risk} /></td>
                    <td className="tabular">{usd(m.value_low)}–{usd(m.value_high)}</td>
                    <td className="text-right"><Link href={`/machines/${m.machine_id}`} className="text-xs text-accent hover:underline">details →</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        ))}
      </div>
    </>
  );
}
