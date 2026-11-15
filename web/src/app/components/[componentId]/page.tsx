import Link from "next/link";
import { API_URL, getJSON, tryJSON, usd } from "@/lib/api";
import { Card, HealthBadge, HealthScore, LifeBar, PageHeader, PartNo, Pending, Pill, StatusBadge, sourceLabel } from "@/components/ui";

type Ev = {
  component: Record<string, string | number>;
  evidence: { reading_json: string; source_url: string; confidence: number; reviewer: string } | null;
  photo: { photo_id: string; plant_id: string; quality: string; rendered: string } | null;
  alternatives: { alt_part_no: string; alternative_kind: string; found_by: string; fit_notes: string }[];
  real_photos: { file: string; author: string; license: string; license_url: string; source_url: string; match_level: string; shows: string }[];
};
const MATCH: Record<string, string> = {
  exact_family: "real photo of this product family",
  same_family: "real photo of the same family (different model)",
  brand_style: "real photo of the same manufacturer's PLCs",
  part_type: "real photo of this type of part (other brand)",
};
type Option = {
  kind: "shelf" | "listing" | "successor"; where?: string; recommended?: boolean; part_no?: string; qty?: number; detail?: string; channel?: string; seller?: string; authorized?: string;
  condition?: string; price?: number | null; shipping?: number | null; lead_time_days?: number | null; warranty_months?: string;
  trust_score?: number | null; url?: string; sample?: string;
};
type Health = {
  health: string; life_used_pct: number | null; installed?: number; expected_end_year?: number; lead_time_days?: number;
  order_by?: string; order_now?: boolean; action: string; line_stop?: boolean; options?: Option[]; best_price?: number | null;
  health_score?: number | null; remaining_years_low?: number | null; remaining_years_high?: number | null; confidence?: string | null;
  sources?: string | null; drivers?: string | null; age_basis?: string | null; simulated?: string | null;
  anomaly_severity?: number | null; resid_mean_c?: number | null; ewma_out_days?: number | null; cusum_max?: number | null;
  trend_c_per_month?: number | null; trend_t?: number | null; peer_z?: number | null; peer_n?: number | null; mahalanobis?: number | null;
};

const fmt = (v: number | null | undefined, d = 1) => (v === null || v === undefined ? null : v.toFixed(d));

const CH: Record<string, string> = { shelf: "Shelf, another plant", successor: "Successor, from manufacturer", oem: "Manufacturer", authorized_distributor: "Authorized distributor", refurbisher: "Refurbisher", surplus: "Surplus dealer", marketplace: "Marketplace", broker: "Broker" };

export default async function ComponentPage({ params }: { params: Promise<{ componentId: string }> }) {
  const { componentId } = await params;
  const [e, h] = await Promise.all([getJSON<Ev>(`/components/${componentId}/evidence`), getJSON<Health>(`/components/${componentId}/health`)]);
  const [sp, so] = await Promise.all([
    tryJSON<{ spof: { component_id: string; hours_down_low: number; hours_down_high: number; downtime_exposure_per_year_low: number; downtime_exposure_per_year_high: number; annual_failure_rate: number; why: string }[] }>(`/plants/${e.component.plant_id}/spof`),
    tryJSON<{ recommendations: { component_id: string; action: string; reason: string; part_value_low: number | null; part_value_high: number | null }[] }>(`/plants/${e.component.plant_id}/sourcing`),
  ]);
  const myS = sp.data?.spof.find((x) => x.component_id === componentId);
  const myR = so.data?.recommendations.find((x) => x.component_id === componentId);
  const c = e.component;
  const reading = e.evidence ? (JSON.parse(e.evidence.reading_json) as { raw_text: string; read_confidence: number }) : null;
  const options = h.options ?? [];
  const orderBy = (h as Health & { covered_by_own_spare?: boolean }).covered_by_own_spare ? "Covered by a spare on this plant's shelf" : h.order_now ? "Now: it's overdue" : h.order_by ? new Date(h.order_by).toLocaleDateString("en-US", { month: "long", year: "numeric" }) : "-";
  return (
    <>
      <PageHeader
        title={c.kb_id ? `${c.manufacturer} ${c.part_no}` : "Unidentified part"}
        subtitle={<><Link className="hover:underline" href={`/plants/${c.plant_id}`}>Plant {String(c.plant_id)}</Link> · {c.line_name} · <Link className="hover:underline" href={`/machines/${c.machine_id}`}>{c.make} {c.model}</Link> {h.line_stop && <Pill tone="alert">line stopper</Pill>}</>}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <Card title="Health">
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-2"><HealthScore score={h.health_score} confidence={h.confidence} /><HealthBadge health={h.health} /></div>
            {h.remaining_years_low !== null && h.remaining_years_low !== undefined && (
              <div className="text-sm">Remaining life: <b>{h.remaining_years_low}–{h.remaining_years_high} years</b></div>
            )}
            {h.drivers && (
              <ul className="list-disc space-y-0.5 pl-4 text-xs">
                {h.drivers.split(";").map((d) => <li key={d}>{d}</li>)}
              </ul>
            )}
            {(h.resid_mean_c != null || h.peer_z != null || h.mahalanobis != null) && (
              <div className="rounded border border-line p-2 text-xs">
                <div className="mb-1 flex justify-between font-medium">
                  <span>Anomaly detection</span>
                  <span className={(h.anomaly_severity ?? 0) > 0 ? "text-alert" : "text-muted"}>severity {fmt(h.anomaly_severity, 2) ?? "0.00"}</span>
                </div>
                <table className="tabular w-full">
                  <tbody>
                    {h.resid_mean_c != null && <tr><td className="text-muted">vs. expected for load + ambient</td><td className="text-right">{h.resid_mean_c > 0 ? "+" : ""}{fmt(h.resid_mean_c)} °C</td></tr>}
                    {h.ewma_out_days != null && <tr><td className="text-muted">EWMA shift (days out of control)</td><td className="text-right">{h.ewma_out_days}</td></tr>}
                    {h.cusum_max != null && <tr><td className="text-muted">CUSUM drift (alarm at 5)</td><td className="text-right">{fmt(h.cusum_max)}</td></tr>}
                    {h.trend_c_per_month != null && <tr><td className="text-muted">Trend °C/month (t)</td><td className="text-right">{fmt(h.trend_c_per_month)} ({fmt(h.trend_t)})</td></tr>}
                    {h.peer_z != null && <tr><td className="text-muted">vs. {h.peer_n} identical parts (robust z)</td><td className="text-right">{fmt(h.peer_z)}</td></tr>}
                    {h.mahalanobis != null && <tr><td className="text-muted">Motor current (Mahalanobis, alarm at 3)</td><td className="text-right">{fmt(h.mahalanobis)}</td></tr>}
                  </tbody>
                </table>
              </div>
            )}
            {h.sources && (
              <div className="text-xs text-muted">
                Based on: {h.sources.split(";").map(sourceLabel).join(" · ")}
                {h.simulated === "yes" && <> <Pill>simulated sensor data</Pill></>}
              </div>
            )}
            <div>
              <div className="text-xs text-muted">Life used since install ({h.installed ?? "?"})</div>
              <LifeBar pct={h.life_used_pct} />
              {h.expected_end_year && <div className="mt-1 text-xs text-muted">Expected end of life: {h.expected_end_year} (middle of the typical life range)</div>}
            </div>
            {c.kb_id && <div className="text-sm"><StatusBadge status={String(c.lifecycle_status)} /> {c.family}</div>}
          </div>
        </Card>
        <Card title="Recommended action">
          <p className="text-sm">{h.action}</p>
          {c.kb_id && (
            <div className="mt-3 space-y-1 text-sm">
              <div>Order by: <b className={h.order_now ? "text-alert" : ""}>{orderBy}</b></div>
              <div className="text-xs text-muted">Fastest delivery: ~{h.lead_time_days} days + 14-day safety buffer before expected end of life</div>
            </div>
          )}
        </Card>
        <Card title="Financial view">
          {sp.pending || so.pending ? (
            <Pending what="Cost of waiting vs. replacing now" detail="money model" />
          ) : (
            <div className="space-y-2 text-sm">
              {myS ? (
                <>
                  <div>Downtime exposure: <b className="text-alert">{usd(myS.downtime_exposure_per_year_low)}–{usd(myS.downtime_exposure_per_year_high)} / yr</b></div>
                  <div className="text-xs text-muted">{Math.round(myS.annual_failure_rate * 100)}% chance of failing this year × {Math.round(myS.hours_down_low)}–{Math.round(myS.hours_down_high)} h down × line cost per hour</div>
                </>
              ) : (
                <div className="text-muted">Not a line stopper: no downtime exposure counted.</div>
              )}
              {myR && (
                <>
                  <div>Money model says: <b>{myR.action.replace(/_/g, " ")}</b></div>
                  <div className="text-xs text-muted">{myR.reason}</div>
                  {myR.part_value_low ? <div className="text-xs">Part value (real listings): {usd(myR.part_value_low)}–{usd(myR.part_value_high ?? 0)}</div> : null}
                </>
              )}
            </div>
          )}
        </Card>
      </div>

      {c.kb_id && (
        <div className="mt-4">
          <Card title={`Where to get one (${options.length} options)`}>
            {options.length === 0 ? (
              <p className="text-sm text-muted">No listings found. See alternatives below.</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="text-left text-xs text-muted">
                  <tr><th className="pb-2">Source</th><th>Seller</th><th>Condition</th><th>Price</th><th>Delivery</th><th>Warranty</th><th>Trust</th></tr>
                </thead>
                <tbody>
                  {options.map((o, i) => (
                    <tr key={i} className={`border-t border-line ${o.recommended ? "bg-accent-soft" : ""}`}>
                      <td className="py-2">
                        {CH[o.kind === "listing" ? o.channel ?? "" : o.kind] ?? o.channel}
                        {o.recommended && <div><Pill tone="ok">Recommended</Pill></div>}
                        {o.kind === "successor" && <div className="font-mono text-[11px] text-muted">{o.part_no}: needs migration</div>}
                      </td>
                      <td>
                        {o.kind === "shelf" ? <><b>{o.where}</b> · qty {o.qty}<div className="font-mono text-[11px] text-muted">&ldquo;{o.detail}&rdquo;</div></> : o.seller}
                        {o.kind === "listing" && o.authorized === "no" && <div className="text-[11px] text-warn">not authorized: counterfeit risk, test on arrival</div>}
                      </td>
                      <td className="capitalize">{(o.condition ?? "").replace(/_/g, " ")}</td>
                      <td className="tabular">{o.kind === "shelf" ? "already owned" : o.price ? usd(o.price) : "-"}{o.shipping ? <div className="text-[11px] text-muted">+{usd(o.shipping)} ship</div> : null}</td>
                      <td className="tabular">{o.lead_time_days ? `${Math.round(o.lead_time_days)} days` : "-"}</td>
                      <td className="tabular">{o.kind === "shelf" ? "-" : o.warranty_months ? `${o.warranty_months} mo` : "none"}</td>
                      <td className="tabular">{o.trust_score ? Math.round(o.trust_score * 100) : "-"}{o.sample === "yes" && <div><Pill>sample listing</Pill></div>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <p className="mt-2 text-xs text-muted">Recommended order: a spare already on a shelf, then the manufacturer or your usual authorized distributor (for discontinued parts, the official successor), then other sources. Sample listings are illustrative until real marketplace data is connected.</p>
          </Card>
        </div>
      )}

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Card title="Evidence">
          {e.real_photos.length > 0 && (
            <div className="mb-4 space-y-3">
              {e.real_photos.map((rp) => (
                <figure key={rp.file}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`${API_URL}/refphotos/${rp.file}`} alt={rp.shows} className="w-full rounded border border-line" />
                  <figcaption className="mt-1 text-xs text-muted">
                    <b className="text-ink">{rp.shows}</b> · {MATCH[rp.match_level] ?? rp.match_level} · Photo: {rp.author},{" "}
                    <a className="text-accent hover:underline" href={rp.license_url || rp.source_url} target="_blank">{rp.license}</a>, via{" "}
                    <a className="text-accent hover:underline" href={rp.source_url} target="_blank">Wikimedia Commons</a>
                  </figcaption>
                </figure>
              ))}
              <div className="text-xs font-medium uppercase tracking-wider text-muted">The label photo image recognition read:</div>
            </div>
          )}
          {e.photo ? (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`${API_URL}/photos/${e.photo.plant_id}/${e.photo.photo_id}.jpg`} alt="label photo" className="w-full rounded border border-line" />
              <p className="mt-2 text-xs text-muted">{e.photo.photo_id} · {e.photo.rendered === "yes" ? "rendered photo" : "photo"} · quality: {e.photo.quality}</p>
            </>
          ) : (
            <p className="text-sm text-muted">No photo yet.</p>
          )}
          {reading && (
            <div className="mt-3 space-y-1 text-sm">
              <div>Image recognition read: <PartNo>{reading.raw_text}</PartNo></div>
              <div className="text-muted">Read confidence {reading.read_confidence} · overall {e.evidence?.confidence} · reviewer {e.evidence?.reviewer || "not yet reviewed"}</div>
            </div>
          )}
        </Card>
        <Card title="Lifecycle source and alternatives">
          <div className="space-y-2 text-sm">
            <div className="text-muted">{c.kb_description}</div>
            {c.successor_part_no && <div>Official successor: <PartNo>{c.successor_part_no}</PartNo></div>}
            {c.source_url && <div className="text-xs">Source ({c.source_type}): <a className="text-accent hover:underline" href={String(c.source_url)} target="_blank">{String(c.source_url).slice(0, 70)}…</a></div>}
          </div>
          {e.alternatives.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm">
              {e.alternatives.map((a, i) => (
                <li key={i}>{a.alt_part_no ? <PartNo>{a.alt_part_no}</PartNo> : "Similar-part search"} · {a.alternative_kind} · <span className="text-muted">{a.fit_notes}</span></li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </>
  );
}
