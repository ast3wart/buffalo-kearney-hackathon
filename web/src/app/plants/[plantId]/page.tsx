import Link from "next/link";
import { getJSON, pct, tryJSON, usd } from "@/lib/api";
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
type Spof = { component_id: string; kb_id: string; hours_down_low: number; hours_down_high: number; downtime_exposure_per_year_low: number; downtime_exposure_per_year_high: number; why: string; action: string };
type Lever = { lever: string; savings_low: number; savings_base: number; savings_high: number; one_time: string; in_price_base: string; basis: string };
type Price = { price_per_plant_low: number; price_per_plant_base: number; price_per_plant_high: number; customer_payback_months: number; recurring_savings_base: number; failed_checks: string; value_capture_pct: number };
type Rescue = { component_id: string; spare_id: string; spare_plant_id: string; hours_down_without_low: number; hours_down_without_high: number; hours_down_with_low: number; hours_down_with_high: number; at_stake_base: number; p_fail_horizon_base: number; expected_pv_base: number; horizon_years: number };
type Deal = { deferred_capex_low: number; deferred_capex_high: number; suggested_price_reduction_low: number; suggested_holdback: number; rationale: string };

export default async function PlantPage({ params }: { params: Promise<{ plantId: string }> }) {
  const { plantId } = await params;
  const [p, capex, spof, sav] = await Promise.all([
    getJSON<Lines>(`/plants/${plantId}/lines`),
    tryJSON<{ capex_by_year: CapexRow[] }>(`/plants/${plantId}/capex`),
    tryJSON<{ spof: Spof[] }>(`/plants/${plantId}/spof`),
    tryJSON<{ plant_savings: Lever[]; price: Price[]; sample_price: Price[]; downtime_rescues?: Rescue[] }>(`/plants/${plantId}/savings`),
  ]);
  const deal = p.plant.status === "target" ? await tryJSON<{ deal_adjustment: Deal[] }>(`/companies/${(p.plant as { company_id?: string }).company_id}/deal`) : null;
  const d = deal?.data?.deal_adjustment?.[0];
  const top = [...(spof.data?.spof ?? [])].sort((a, b) => b.downtime_exposure_per_year_high - a.downtime_exposure_per_year_high).slice(0, 5);
  const capexTotal = (capex.data?.capex_by_year ?? []).reduce((a, r) => [a[0] + r.capex_low, a[1] + r.capex_high], [0, 0]);
  const pr = sav.data?.price?.[0];
  const spr = sav.data?.sample_price?.[0];
  const rescues = sav.data?.downtime_rescues ?? [];
  const label = (s: string) => s.replace(/_/g, " ");
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
      {d && (
        <div className="mt-4">
          <Card title="Deal view · what this scan means for the purchase price" tone="alert">
            <div className="grid gap-4 md:grid-cols-3">
              <Stat label="deferred CapEx the buyer inherits" value={`${usd(d.deferred_capex_low)}–${usd(d.deferred_capex_high)}`} tone="alert" />
              <Stat label="pay this much less (PV of the low case)" value={usd(d.suggested_price_reduction_low)} tone="alert" />
              <Stat label="plus hold back at closing" value={usd(d.suggested_holdback)} tone="warn" />
            </div>
            <p className="mt-3 text-xs text-muted">{d.rationale}</p>
          </Card>
        </div>
      )}
      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card title={`CapEx cliff · next 5 years ${capex.data ? `(${usd(capexTotal[0])}–${usd(capexTotal[1])})` : ""}`}>
            {capex.data ? <CapexChart rows={capex.data.capex_by_year} /> : <Pending what="The CapEx cliff" detail={capex.pending ?? capex.error} />}
            <p className="mt-1 text-xs text-muted">Dark = low estimate, light = up to high estimate. Control-part replacements + migration engineering. How we got this: Sources page.</p>
          </Card>
        </div>
        <Card title="Savings and price (per year)">
          {pr ? (
            <div className="space-y-3">
              <Stat label="recurring savings we can audit (whole plant, extrapolated)" value={usd(pr.recurring_savings_base)} tone="ok" />
              <Stat label={`price per plant (${Math.round((pr.value_capture_pct ?? 0.2) * 100)}% of savings, extrapolated)`} value={`${usd(pr.price_per_plant_base)}`} />
              <div className="text-xs text-muted">range {usd(pr.price_per_plant_low)}–{usd(pr.price_per_plant_high)} · customer payback {pr.customer_payback_months} months</div>
              {spr && (
                <details className="text-xs text-muted">
                  <summary className="cursor-pointer">Evidence: only the parts scanned so far</summary>
                  savings {usd(spr.recurring_savings_base)} / yr → price {usd(spr.price_per_plant_base)} (range {usd(spr.price_per_plant_low)}–{usd(spr.price_per_plant_high)}). The whole-plant number scales this by the share of the plant the register covers.
                </details>
              )}
              <ul className="space-y-1 text-xs">
                {(sav.data?.plant_savings ?? []).map((l) => (
                  <li key={l.lever} className="flex justify-between gap-2">
                    <span>{label(l.lever)}{l.in_price_base !== "yes" && <span className="text-muted"> (not priced)</span>}{l.one_time === "yes" && <span className="text-muted"> · one-time</span>}</span>
                    <span className="tabular">{usd(l.savings_base)}</span>
                  </li>
                ))}
              </ul>
              {rescues.length > 0 && (
                <div className="border-t border-line pt-2 text-xs">
                  <div className="font-medium">Outages a sister-plant spare prevents (if it fails)</div>
                  <ul className="mt-1 space-y-1 text-muted">
                    {rescues.slice(0, 3).map((r) => (
                      <li key={r.component_id}>
                        <Link href={`/components/${r.component_id}`} className="font-mono hover:underline">{r.component_id}</Link>: spare {r.spare_id} from {r.spare_plant_id} cuts{" "}
                        {Math.round((r.hours_down_without_low + r.hours_down_without_high) / 2)} h down to {Math.round((r.hours_down_with_low + r.hours_down_with_high) / 2)} h ·{" "}
                        <span className="text-ink">{usd(r.at_stake_base)} at stake</span> · {pct(r.p_fail_horizon_base)} chance in {r.horizon_years} yrs
                      </li>
                    ))}
                  </ul>
                  <p className="mt-1 text-muted">Downtime avoided above = expected value of these over {rescues[0].horizon_years} years, per year, scanned parts only. Not in the price.</p>
                </div>
              )}
            </div>
          ) : (
            p.plant.status === "target" ? <p className="text-sm text-muted">Not priced yet: this plant is an acquisition target. See the deal view above.</p>
              : <Pending what="Savings and price" detail={sav.pending ?? sav.error} />
          )}
        </Card>
      </div>
      {top.length > 0 && (
        <div className="mt-4">
          <Card title="Line stoppers · downtime exposure per year (failure odds × hours down × $/hour × share not made up later)">
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted">
                <tr><th className="pb-2">Part</th><th>Hours down if it fails</th><th>Exposure / year</th><th>Why</th></tr>
              </thead>
              <tbody>
                {top.map((x) => (
                  <tr key={x.component_id} className="border-t border-line align-top">
                    <td className="py-2"><Link href={`/components/${x.component_id}`} className="font-mono text-[0.85em] hover:underline">{x.component_id}</Link></td>
                    <td className="tabular">{Math.round(x.hours_down_low)}–{Math.round(x.hours_down_high)} h</td>
                    <td className="tabular font-medium text-alert">{usd(x.downtime_exposure_per_year_low)}–{usd(x.downtime_exposure_per_year_high)}</td>
                    <td className="text-xs text-muted">{x.why}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
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
