import Link from "next/link";
import { getJSON, tryJSON, type ShelfMatch } from "@/lib/api";
import { Card, PageHeader, PartNo, Pending, Pill, StatusBadge } from "@/components/ui";
import { CapexChart } from "@/components/CapexChart";

type Comp = {
  component_id: string; kb_id: string; part_no: string; part_no_read: string; family: string; manufacturer: string;
  component_type: string; lifecycle_status: string; date_code: string; confidence: number; method: string;
  needs_review: string; review_reason: string; successor_part_no: string;
};
type Machine = { machine_id: string; description: string; make: string; model: string; machine_type: string; year_built: number; criticality: string; components: Comp[] };
type Registry = { plant: { plant_id: string; plant_name: string; state: string; status: string; employees: number }; lines: { line_id: string; line_name: string; product: string; machines: Machine[] }[] };
type CapexRow = { year: number; capex_low: number; capex_high: number; capex_type: string };

export default async function PlantPage({ params }: { params: Promise<{ plantId: string }> }) {
  const { plantId } = await params;
  const [reg, shelf, capex] = await Promise.all([
    getJSON<Registry>(`/plants/${plantId}/registry`),
    getJSON<ShelfMatch[]>(`/plants/${plantId}/shelf-matches`),
    tryJSON<{ capex_by_year: CapexRow[] }>(`/plants/${plantId}/capex`),
  ]);
  const all = reg.lines.flatMap((l) => l.machines.flatMap((m) => m.components.map((c) => ({ ...c, m, l }))));
  const lineStop = all.filter((c) => c.m.criticality === "line_stop" && ["discontinued", "end_of_life"].includes(c.lifecycle_status));
  const shelfBy = Object.fromEntries(shelf.map((s) => [s.component_id, s]));
  return (
    <>
      <PageHeader
        title={`${reg.plant.plant_name}, ${reg.plant.state}`}
        subtitle={<>{reg.plant.employees} people · {reg.lines.length} lines · {all.length} critical parts identified {reg.plant.status === "target" && <Pill tone="warn">acquisition target</Pill>}</>}
      />
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="CapEx cliff · equipment spending needed by year">
          {capex.data ? <CapexChart rows={capex.data.capex_by_year} /> : <Pending what="The CapEx cliff" detail={capex.pending ?? capex.error} />}
        </Card>
        <Card title="Parts that stop a line if they fail" tone={lineStop.length ? "alert" : undefined}>
          {lineStop.length === 0 && <p className="text-sm text-muted">None at risk.</p>}
          <ul className="space-y-3 text-sm">
            {lineStop.map((c) => (
              <li key={c.component_id} className="border-b border-line pb-2 last:border-0">
                <div className="flex items-center justify-between gap-2">
                  <Link href={`/components/${c.component_id}`} className="hover:underline">
                    {c.l.line_name} · {c.m.make} {c.m.model}
                  </Link>
                  <StatusBadge status={c.lifecycle_status} />
                </div>
                <div className="text-muted">
                  <PartNo>{c.part_no}</PartNo> {c.family} · installed {c.date_code}
                  {c.successor_part_no && <> · successor <PartNo>{c.successor_part_no}</PartNo></>}
                </div>
                {shelfBy[c.component_id] ? (
                  <div className="mt-1 text-ok">
                    ✓ Spare on the shelf at <b>{shelfBy[c.component_id].spare_plant_name}</b> (qty {shelfBy[c.component_id].spare_qty})
                    {!shelfBy[c.component_id].same_company && " · other company, same fund"}
                  </div>
                ) : (
                  <div className="mt-1 text-alert">No spare anywhere in the portfolio</div>
                )}
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <h2 className="mb-3 mt-8 text-sm font-semibold">Registry: every machine and the parts inside</h2>
      <div className="space-y-4">
        {reg.lines.map((l) => (
          <Card key={l.line_id} title={`${l.line_name} · ${l.product}`}>
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted">
                <tr><th className="pb-2">Machine</th><th>Part</th><th>Status</th><th>Installed</th><th>How identified</th></tr>
              </thead>
              <tbody>
                {l.machines.map((m) =>
                  (m.components.length ? m.components : [null]).map((c, i) => (
                    <tr key={`${m.machine_id}-${i}`} className="border-t border-line align-top">
                      <td className="py-2">
                        {i === 0 && (
                          <>
                            {m.make} {m.model}{" "}
                            {m.criticality === "line_stop" && <Pill tone="alert">stops the line</Pill>}
                            <div className="text-xs text-muted">{m.machine_type.replace("_", " ")} · built {m.year_built}</div>
                          </>
                        )}
                      </td>
                      {c ? (
                        <>
                          <td>
                            <Link href={`/components/${c.component_id}`} className="hover:underline">
                              {c.kb_id ? <PartNo>{c.part_no}</PartNo> : <span className="text-muted">not in KB</span>}
                            </Link>
                            <div className="text-xs text-muted">{c.family || <span className="font-mono">read: {c.part_no_read}</span>}</div>
                          </td>
                          <td><StatusBadge status={c.lifecycle_status} /></td>
                          <td className="tabular">{c.date_code}</td>
                          <td className="text-xs">
                            {c.method === "vision" ? "📷 photo (Claude)" : c.method === "list" ? "equipment list" : "scan"}
                            {c.needs_review === "yes" && <div><Pill tone="warn">review: {c.review_reason}</Pill></div>}
                          </td>
                        </>
                      ) : (
                        <td colSpan={4} className="text-xs text-muted">no control parts recorded</td>
                      )}
                    </tr>
                  )),
                )}
              </tbody>
            </table>
          </Card>
        ))}
      </div>
    </>
  );
}
