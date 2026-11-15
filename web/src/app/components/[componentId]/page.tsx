import Link from "next/link";
import { API_URL, getJSON } from "@/lib/api";
import { Card, PageHeader, PartNo, Pill, StatusBadge } from "@/components/ui";

type Ev = {
  component: Record<string, string | number>;
  evidence: { reading_json: string; source_url: string; confidence: number; reviewer: string } | null;
  photo: { photo_id: string; plant_id: string; quality: string; rendered: string } | null;
  listings: Record<string, string>[];
  alternatives: { alt_part_no: string; alternative_kind: string; found_by: string; fit_notes: string }[];
};

export default async function ComponentPage({ params }: { params: Promise<{ componentId: string }> }) {
  const { componentId } = await params;
  const e = await getJSON<Ev>(`/components/${componentId}/evidence`);
  const c = e.component;
  const reading = e.evidence ? (JSON.parse(e.evidence.reading_json) as { raw_text: string; read_confidence: number; match: Record<string, unknown> }) : null;
  return (
    <>
      <PageHeader
        title={c.kb_id ? `${c.manufacturer} ${c.part_no}` : "Unidentified part"}
        subtitle={<><Link className="hover:underline" href={`/plants/${c.plant_id}`}>Plant {String(c.plant_id)}</Link> · {c.line_name} · {c.make} {c.model} {c.criticality === "line_stop" && <Pill tone="alert">stops the line</Pill>}</>}
      />
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Evidence">
          {e.photo ? (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`${API_URL}/photos/${e.photo.plant_id}/${e.photo.photo_id}.jpg`} alt="label photo" className="w-full rounded border border-line" />
              <p className="mt-2 text-xs text-muted">
                {e.photo.photo_id} · {e.photo.rendered === "yes" ? "rendered test label" : "photo"} · quality: {e.photo.quality}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted">No photo: identified from the {c.method === "list" ? "equipment list" : "scan reading"}.</p>
          )}
          {reading && (
            <div className="mt-3 space-y-1 text-sm">
              <div>Read: <PartNo>{reading.raw_text}</PartNo></div>
              <div className="text-muted">Read confidence {reading.read_confidence} · match {JSON.stringify(reading.match)}</div>
              <div className="text-muted">Overall confidence {e.evidence?.confidence} · reviewer {e.evidence?.reviewer || "not yet reviewed"}</div>
            </div>
          )}
          {c.needs_review === "yes" && <div className="mt-2"><Pill tone="warn">needs review: {String(c.review_reason)}</Pill></div>}
        </Card>
        <Card title="Lifecycle">
          <div className="space-y-2 text-sm">
            <div><StatusBadge status={String(c.lifecycle_status)} /> {c.family}</div>
            <div className="text-muted">{c.kb_description}</div>
            <div>Installed: {c.date_code}</div>
            {c.successor_part_no && <div>Successor: <PartNo>{c.successor_part_no}</PartNo></div>}
            {c.source_url && (
              <div className="text-xs">
                Source ({c.source_type}): <a className="text-accent hover:underline" href={String(c.source_url)} target="_blank">{String(c.source_url).slice(0, 70)}…</a>
              </div>
            )}
          </div>
          {e.alternatives.length > 0 && (
            <div className="mt-4">
              <h3 className="mb-1 text-xs font-medium uppercase tracking-wider text-muted">If you can&apos;t get this part</h3>
              <ul className="space-y-1 text-sm">
                {e.alternatives.map((a, i) => (
                  <li key={i}>{a.alt_part_no ? <PartNo>{a.alt_part_no}</PartNo> : "similar part search"} · {a.alternative_kind} · <span className="text-muted">{a.fit_notes}</span></li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-4">
            <h3 className="mb-1 text-xs font-medium uppercase tracking-wider text-muted">Market listings</h3>
            {e.listings.length ? (
              <ul className="space-y-1 text-sm">
                {e.listings.map((l, i) => (
                  <li key={i}>{l.channel} · {l.condition} · ${l.price} · <a className="text-accent hover:underline" href={l.url} target="_blank">{l.seller}</a></li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">Listings for this part come from Brandon&apos;s sourcing data.</p>
            )}
          </div>
        </Card>
      </div>
    </>
  );
}
