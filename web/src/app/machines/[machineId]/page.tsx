import Link from "next/link";
import { getJSON, usd } from "@/lib/api";
import { Card, HealthBadge, HealthScore, LifeBar, PageHeader, PartNo, Pill, StatusBadge } from "@/components/ui";

type Part = {
  component_id: string; kb_id: string; part_no: string; part_no_read: string; family: string; component_type: string;
  lifecycle_status: string; method: string; health: string; life_used_pct: number | null; installed: number | null;
  order_by: string | null; order_now: boolean | null; action: string; n_listings: number | null; best_price: number | null;
  health_score: number | null; confidence: string | null; remaining_years_low: number | null; remaining_years_high: number | null;
};
type M = {
  machine: { machine_id: string; make: string; model: string; machine_type: string; year_built: number; criticality: string; serial: string; condition: string; risk: string; value_low: number; value_high: number; parts: number };
  line: { line_name: string; product: string };
  plant: { plant_id: string; plant_name: string; state: string };
  parts: Part[];
};

const when = (p: Part & { covered_by_own_spare?: boolean }) =>
  p.covered_by_own_spare ? "Covered (own spare)" : p.order_now ? "Order now (overdue)" : p.order_by ? new Date(p.order_by).toLocaleDateString("en-US", { month: "short", year: "numeric" }) : "-";

export default async function MachinePage({ params }: { params: Promise<{ machineId: string }> }) {
  const { machineId } = await params;
  const d = await getJSON<M>(`/machines/${machineId}`);
  const m = d.machine;
  return (
    <>
      <PageHeader
        title={`${m.make} ${m.model}`}
        subtitle={<><Link href={`/plants/${d.plant.plant_id}`} className="hover:underline">{d.plant.plant_name}</Link> · {d.line.line_name} ({d.line.product}) · {m.machine_type.replace("_", " ")} · built {m.year_built} {m.criticality === "line_stop" && <Pill tone="alert">line stopper: production halts if it fails</Pill>}</>}
      />
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <Card><div className="text-xs text-muted">Overall</div><div className="mt-1"><HealthBadge health={m.risk} /></div></Card>
        <Card><div className="text-xs text-muted">Replacement value</div><div className="tabular mt-1 text-lg font-semibold">{usd(m.value_low)}–{usd(m.value_high)}</div></Card>
        <Card><div className="text-xs text-muted">Condition</div><div className="mt-1 text-lg font-semibold capitalize">{m.condition}</div></Card>
        <Card><div className="text-xs text-muted">Serial</div><div className="mt-1 font-mono">{m.serial || "not recorded"}</div></Card>
      </div>
      <Card title={`Parts inside (${d.parts.length})`}>
        <table className="w-full text-sm">
          <thead className="text-left text-xs text-muted">
            <tr><th className="pb-2">Part</th><th>Health</th><th>Status</th><th>Life used</th><th>Order by</th><th>Recommended action</th></tr>
          </thead>
          <tbody>
            {d.parts.map((p) => (
              <tr key={p.component_id} className="border-t border-line align-top">
                <td className="py-2">
                  <Link href={`/components/${p.component_id}`} className="hover:underline">
                    {p.kb_id ? <PartNo>{p.part_no}</PartNo> : <span className="font-mono text-[0.85em] text-muted">{p.part_no_read}</span>}
                  </Link>
                  <div className="text-xs text-muted">{p.family || (["other", "power_supply"].includes(p.component_type) ? "commodity part · not tracked" : "label unreadable · re-photograph")}</div>
                  {p.kb_id && <div className="mt-0.5"><StatusBadge status={p.lifecycle_status} /></div>}
                </td>
                <td>
                  <HealthScore score={p.health_score} />
                  {p.remaining_years_low !== null && p.remaining_years_low !== undefined && <div className="text-xs text-muted">{p.remaining_years_low}–{p.remaining_years_high} yrs left</div>}
                </td>
                <td><HealthBadge health={p.health} /></td>
                <td><LifeBar pct={p.life_used_pct} />{p.installed && <div className="text-xs text-muted">since {p.installed}</div>}</td>
                <td className={p.order_now ? "font-medium text-alert" : ""}>{p.kb_id ? when(p) : "-"}</td>
                <td className="max-w-xs text-xs">
                  {p.action}
                  {p.kb_id && p.n_listings ? <div className="mt-1 text-muted">{p.n_listings} market listings{p.best_price ? ` · from ${usd(p.best_price)}` : ""}</div> : null}
                  {p.kb_id && <Link href={`/components/${p.component_id}`} className="text-accent hover:underline">where to buy →</Link>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </>
  );
}
