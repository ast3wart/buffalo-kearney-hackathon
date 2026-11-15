import Link from "next/link";
import { getJSON, pct, type Accuracy, type Portfolio } from "@/lib/api";
import { Card, PageHeader, PartNo, Pill, Stat, StatusBadge } from "@/components/ui";

export default async function PortfolioPage() {
  let p: Portfolio, a: Accuracy;
  try {
    [p, a] = await Promise.all([getJSON<Portfolio>("/portfolio"), getJSON<Accuracy>("/accuracy")]);
  } catch (e) {
    return (
      <Card tone="alert" title="API not reachable">
        <p className="text-sm">
          Run <code>python scripts/seed.py</code> then <code>uvicorn api.main:app --reload</code>. ({String(e)})
        </p>
      </Card>
    );
  }
  const totals = p.totals as { plants_owned: number; machines: number; components: number; at_risk_pct: number; line_stop_at_risk: number };
  const name = Object.fromEntries(p.plants.map((t) => [t.plant_id, t.plant_name]));
  const lineStop = p.shelf_matches.filter((m) => m.criticality === "line_stop");
  return (
    <>
      <PageHeader
        title={p.fund_name}
        subtitle="Every machine and every critical part across the portfolio: what's discontinued, what stops a line, and what's already on a shelf somewhere."
      />
      <div className="grid gap-4 md:grid-cols-5">
        <Card><Stat label="owned plants" value={totals.plants_owned} /></Card>
        <Card><Stat label="machines scanned" value={totals.machines} /></Card>
        <Card><Stat label="critical parts identified" value={totals.components} /></Card>
        <Card><Stat label="discontinued or end-of-life" value={pct(totals.at_risk_pct)} tone="alert" /></Card>
        <Card><Stat label="at-risk parts that stop a line" value={totals.line_stop_at_risk} tone="alert" /></Card>
      </div>

      {p.companies.map((co) => (
        <div key={co.company_id} className="mt-8">
          <h2 className="mb-3 text-sm font-semibold">
            {co.company_name}{" "}
            <span className="font-normal text-muted">
              {co.fund_id ? "· owned" : "· acquisition target"} · {co.plants.length} plant{co.plants.length > 1 ? "s" : ""}
            </span>
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            {p.plants.filter((t) => co.plants.includes(t.plant_id)).map((t) => (
              <Link key={t.plant_id} href={`/plants/${t.plant_id}`} className="block rounded border border-line bg-surface p-5 hover:border-accent">
                <div className="mb-3 flex items-baseline justify-between">
                  <span className="font-semibold">{t.plant_name}, {t.state}</span>
                  {t.status === "target" ? <Pill tone="warn">target</Pill> : <span className="text-xs text-muted">{t.employees} people</span>}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <Stat label="parts" value={t.components} />
                  <Stat label="at risk" value={pct(t.at_risk_pct)} tone={t.at_risk_pct > 0.4 ? "alert" : "warn"} />
                  <Stat label="stop a line" value={t.line_stop_at_risk} tone={t.line_stop_at_risk ? "alert" : undefined} />
                </div>
                <div className="mt-3 text-xs text-muted">
                  {t.machines} machines · {t.lines} lines · {t.idle_spares} shelf items idle 5+ yrs · {t.needs_review} to review
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card title="The spare is already on another shelf">
            <p className="mb-3 text-sm text-muted">
              Discontinued parts that stop a line, where another plant in the portfolio has one in stock. Check the shelf before
              buying, and move the spare instead of waiting weeks.
            </p>
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-muted">
                <tr><th className="pb-2">Needed at</th><th>Part</th><th>Status</th><th>On the shelf at</th></tr>
              </thead>
              <tbody>
                {lineStop.map((m) => (
                  <tr key={m.component_id} className="border-t border-line">
                    <td className="py-2"><Link className="hover:underline" href={`/components/${m.component_id}`}>{name[m.plant_id]} · {m.machine}</Link></td>
                    <td><PartNo>{m.part_no}</PartNo> <span className="text-xs text-muted">{m.family}</span></td>
                    <td><StatusBadge status={m.lifecycle_status} /></td>
                    <td>
                      <b>{m.spare_plant_name}</b> · qty {m.spare_qty}{" "}
                      {!m.same_company && <Pill tone="ok">other company, same fund</Pill>}
                      <div className="font-mono text-[11px] text-muted">&ldquo;{m.spare_description}&rdquo;</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
        <Card title="Measured, not assumed">
          <div className="space-y-4">
            <Stat label={`photos read exactly (Claude vision)`} value={`${a.photos_exact}/${a.photos_read}`} tone="ok" />
            <Stat label="part-identification precision" value={pct(a.components_precision)} tone="ok" />
            <Stat label="recall (rest goes to a person)" value={pct(a.components_recall)} />
            <Stat label="auto-accepted parts that were right" value={`${a.auto_accepted_correct}/${a.auto_accepted}`} tone="ok" />
            <p className="text-xs text-muted">{a.note}</p>
          </div>
        </Card>
      </div>
    </>
  );
}
