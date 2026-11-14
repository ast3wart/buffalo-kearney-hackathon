import { getJSON, resolveCompany, API_URL, type Overview, type Markup, type Harmonization, type Compliance } from "@/lib/api";
import { Card, PageHeader, PartNo, Stat, fmt } from "@/components/ui";
import { CostChart } from "@/components/CostChart";

// Overview: 💲 Asher. GET /overview, /markups, /harmonization (docs/build/api.md)
export default async function OverviewPage({ searchParams }: { searchParams: Promise<{ company?: string }> }) {
  const { company: param } = await searchParams;
  let company = "";
  let o: Overview | null = null;
  let markups: Markup[] = [];
  let harm: Harmonization[] = [];
  let comp: Compliance[] = [];
  let error = "";
  try {
    company = await resolveCompany(param);
    [o, markups, harm, comp] = await Promise.all([
      getJSON<Overview>(`/overview?company=${company}`),
      getJSON<Markup[]>(`/markups?company=${company}&limit=8`),
      getJSON<Harmonization[]>(`/harmonization?company=${company}&limit=6`),
      getJSON<Compliance[]>(`/compliance?company=${company}&limit=6`),
    ]);
  } catch (e) {
    error = String(e);
  }

  if (!o) {
    return (
      <Card tone="alert" title="API not reachable">
        <p className="text-sm">
          Can&apos;t load data from {API_URL}. Run <code>python -m afterlife.run</code>, then{" "}
          <code>uvicorn api.main:app --reload</code>.
        </p>
        <pre className="mt-2 whitespace-pre-wrap text-xs text-muted">{error}</pre>
      </Card>
    );
  }

  const chart = o.products.map((p) => ({
    product: p.product_id, spares: p.spares_per_unit, warranty: p.warranty_per_unit,
  }));
  const cov = o.coverage;

  return (
    <>
      <PageHeader
        title={o.company}
        subtitle={<>{o.industry} · data as of {o.data_as_of}</>}
      />

      <div className="mb-2 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card><Stat label={`Paid above the supplier's own contract price (${o.contract_leakage_lines} PO lines)`} value={fmt.usd(o.contract_leakage_usd)} tone="alert" /></Card>
        <Card><Stat label="Spares bought above series price despite a 'spares at series price' clause" value={fmt.usd(o.spares_clause_gap_usd)} tone="alert" /></Card>
        <Card><Stat label="Price harmonization (paid above best supplier / plant)" value={fmt.usd(o.harmonization_usd)} tone="warn" /></Card>
        {o.acquired_plant_harmonization_usd > 0 ? (
          <Card><Stat label="…of which: acquired-plant premium" value={fmt.usd(o.acquired_plant_harmonization_usd)} tone="warn" /></Card>
        ) : (
          <Card>
            <Stat label="Warranty cost, % of revenue"
                  value={o.has_claims ? `${o.warranty_pct_revenue.toFixed(2)}%` : <span className="text-muted">pending claims</span>} />
          </Card>
        )}
      </div>
      <p className="mb-6 text-xs text-muted">
        Contract figures compare what was paid with the price schedule read from {o.agreements_read} supplier agreements
        (extracted from the documents). Spare-part overspend vs production price: {fmt.usd(o.spare_overspend_usd_per_year)}/yr
        (scenario estimate: most spares are bought near contract price; only off-contract buys carry a real markup).
      </p>

      <div className="mb-6 grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Cost after the sale, per unit built (spares + warranty)">
            <CostChart data={chart} />
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-muted md:grid-cols-4">
              {o.products.map((p) => (
                <div key={p.product_id}>
                  <span className="font-mono text-ink">{p.product_id}</span> build ${Math.round(p.build_cost).toLocaleString()}
                  {" → "}lifecycle ${Math.round(p.lifecycle_cost).toLocaleString()}
                </div>
              ))}
            </div>
            {!o.has_claims && <p className="mt-2 text-xs text-muted">Warranty bars appear once warranty claims are generated.</p>}
          </Card>
        </div>
        <Card title="Records linked to a part">
          <ul className="space-y-3 text-sm">
            <Coverage label="Production purchase lines" all={cov.production_spend_pct} high={cov.production_high_conf_pct} />
            <Coverage label="Service / spare purchase lines" all={cov.service_spend_pct} high={cov.service_high_conf_pct} />
            {cov.claims_pct != null ? (
              <Coverage label="Warranty claims" all={cov.claims_pct} high={null} />
            ) : (
              <li className="text-muted">Warranty claims: not generated yet</li>
            )}
          </ul>
          <p className="mt-4 text-xs text-muted">
            Savings figures use only high-confidence links (≥ 0.8), which are 99.9–100% correct on companies the matcher was never tuned on.
          </p>
        </Card>
      </div>

      <div className="mb-6">
        <Card title="Your own contracts say otherwise: biggest gaps vs the agreed price">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="py-1">Finding</th><th className="py-1">Part</th><th className="py-1">Agreement</th>
                <th className="py-1 text-right">Paid / pc</th><th className="py-1 text-right">Contract / pc</th>
                <th className="py-1 text-right">Gap</th>
              </tr>
            </thead>
            <tbody>
              {comp.map((c) => (
                <tr key={`${c.finding}-${c.po_line_id}`} className="border-t border-line">
                  <td className="py-1.5">
                    <span className={`rounded px-1.5 py-0.5 text-xs ${c.finding === "spares_clause" ? "bg-alert-soft text-alert" : "bg-warn-soft text-warn"}`}>
                      {c.finding === "spares_clause" ? "spares clause" : "price leakage"}
                    </span>
                    <div className="mt-0.5 font-mono text-xs text-muted">{c.po_line_id} · {c.po_date}</div>
                  </td>
                  <td className="py-1.5"><PartNo>{c.part_no}</PartNo><div className="text-xs text-muted">{c.description}</div></td>
                  <td className="py-1.5 font-mono text-xs text-muted">{c.doc_file}</td>
                  <td className="tabular py-1.5 text-right">${c.price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">${c.contract_price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">{fmt.usd(c.gap_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Biggest spare-part markups (same part, scenario estimate)">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="py-1">Part</th><th className="py-1 text-right">Production</th>
                <th className="py-1 text-right">Service</th><th className="py-1 text-right">Markup</th>
                <th className="py-1 text-right">Overspend</th>
              </tr>
            </thead>
            <tbody>
              {markups.map((m) => (
                <tr key={m.part_no} className="border-t border-line">
                  <td className="py-1.5"><PartNo>{m.part_no}</PartNo><div className="text-xs text-muted">{m.description}</div></td>
                  <td className="tabular py-1.5 text-right">${m.prod_price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">${m.svc_price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">
                    <span className={`rounded px-1.5 py-0.5 text-xs ${m.ratio >= 3 ? "bg-alert-soft text-alert" : "bg-warn-soft text-warn"}`}>{fmt.ratio(m.ratio)}</span>
                  </td>
                  <td className="tabular py-1.5 text-right">{fmt.usd(m.overspend_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card title="Price harmonization: paid above the best price for the same part">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted">
                <th className="py-1">Part · supplier · plant</th><th className="py-1 text-right">Paid</th>
                <th className="py-1 text-right">Best</th><th className="py-1 text-right">Savings</th>
              </tr>
            </thead>
            <tbody>
              {harm.map((h) => (
                <tr key={`${h.part_no}-${h.supplier_id}-${h.plant}`} className="border-t border-line">
                  <td className="py-1.5">
                    <PartNo>{h.part_no}</PartNo><div className="text-xs text-muted">{h.description}</div>
                    <div className="text-xs text-muted">{h.supplier_name} · <span className="font-mono">{h.plant}</span></div>
                  </td>
                  <td className="tabular py-1.5 text-right">${h.price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">${h.best_price_ea.toFixed(2)}</td>
                  <td className="tabular py-1.5 text-right">{fmt.usd(h.savings_usd)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
      <p className="mt-6 text-xs text-muted">
        All dollar figures are analytics estimates for a sourcing review, not accruals or amounts owed.
      </p>
    </>
  );
}

function Coverage({ label, all, high }: { label: string; all: number; high: number | null }) {
  return (
    <li>
      <div className="flex justify-between"><span>{label}</span><span className="tabular font-medium">{fmt.pct(all)}</span></div>
      <div className="mt-1 h-1.5 w-full rounded bg-line">
        <div className="h-1.5 rounded bg-accent" style={{ width: `${Math.round((high ?? all) * 100)}%` }} />
      </div>
      {high != null && <div className="mt-0.5 text-xs text-muted">{fmt.pct(high)} high confidence</div>}
    </li>
  );
}
