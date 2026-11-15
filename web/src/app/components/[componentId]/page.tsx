import Link from "next/link";
import { API_URL, getJSON, tryJSON, usd } from "@/lib/api";
import { Card, HealthBadge, LifeBar, PageHeader, PartNo, Pending, Pill, StatusBadge } from "@/components/ui";

type Ev = {
  component: Record<string, string | number>;
  evidence: { reading_json: string; source_url: string; confidence: number; reviewer: string } | null;
  photo: { photo_id: string; plant_id: string; quality: string; rendered: string } | null;
  alternatives: { alt_part_no: string; alternative_kind: string; found_by: string; fit_notes: string }[];
};
type Option = {
  kind: "shelf" | "listing"; where?: string; qty?: number; detail?: string; channel?: string; seller?: string; authorized?: string;
  condition?: string; price?: number | null; shipping?: number | null; lead_time_days?: number | null; warranty_months?: string;
  trust_score?: number | null; url?: string; sample?: string;
};
type Health = {
  health: string; life_used_pct: number | null; installed?: number; expected_end_year?: number; lead_time_days?: number;
  order_by?: string; order_now?: boolean; action: string; line_stop?: boolean; options?: Option[]; best_price?: number | null;
};

const CH: Record<string, string> = { shelf: "Shelf, another plant", oem: "Manufacturer", authorized_distributor: "Authorized distributor", refurbisher: "Refurbisher", surplus: "Surplus dealer", marketplace: "Marketplace", broker: "Broker" };

export default async function ComponentPage({ params }: { params: Promise<{ componentId: string }> }) {
  const { componentId } = await params;
  const [e, h] = await Promise.all([getJSON<Ev>(`/components/${componentId}/evidence`), getJSON<Health>(`/components/${componentId}/health`)]);
  const fin = await tryJSON<unknown>(`/plants/${e.component.plant_id}/savings`);
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
        <Card title="Status">
          <div className="space-y-3">
            <HealthBadge health={h.health} />
            <div>
              <div className="text-xs text-muted">Life used since install ({h.installed ?? "?"})</div>
              <LifeBar pct={h.life_used_pct} />
              {h.expected_end_year && <div className="mt-1 text-xs text-muted">Expected end of life: {h.expected_end_year} (conservative end of the typical range)</div>}
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
          {fin.data ? <p className="text-sm">See savings on the plant page.</p> : <Pending what="Cost of waiting vs. replacing now" detail="Brandon's money model" />}
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
                    <tr key={i} className={`border-t border-line ${o.kind === "shelf" ? "bg-accent-soft" : ""}`}>
                      <td className="py-2">{CH[o.kind === "shelf" ? "shelf" : o.channel ?? ""] ?? o.channel}</td>
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
            <p className="mt-2 text-xs text-muted">Shelf first: move a spare you already own before buying. Sample listings are illustrative until real marketplace data is connected.</p>
          </Card>
        </div>
      )}

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Card title="Evidence">
          {e.photo ? (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`${API_URL}/photos/${e.photo.plant_id}/${e.photo.photo_id}.jpg`} alt="label photo" className="w-full rounded border border-line" />
              <p className="mt-2 text-xs text-muted">{e.photo.photo_id} · {e.photo.rendered === "yes" ? "rendered test label" : "photo"} · quality: {e.photo.quality}</p>
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
