"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";
import { Card, PageHeader, PartNo, Pill, StatusBadge } from "@/components/ui";

type ScanResult = {
  reading: { manufacturer: string; part_no: string; series: string; serial: string; date_code: string; description: string; unclear: string[]; confidence: number; cached: boolean };
  match: { kb_id: string; manufacturer: string; part_no: string; family: string; lifecycle_status: string; successor_part_no: string; source_url: string } | null;
  match_method: string;
  confidence: number;
  needs_review: boolean;
};

export default function ScanPage() {
  const [preview, setPreview] = useState<string>();
  const [res, setRes] = useState<ScanResult>();
  const [err, setErr] = useState<string>();
  const [busy, setBusy] = useState(false);

  async function onFile(f: File) {
    setPreview(URL.createObjectURL(f));
    setRes(undefined);
    setErr(undefined);
    setBusy(true);
    const body = new FormData();
    body.append("file", f);
    try {
      const r = await fetch(`${API_URL}/scan`, { method: "POST", body });
      if (!r.ok) throw new Error((await r.json()).detail ?? r.statusText);
      setRes(await r.json());
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Live scan" subtitle="Photograph a nameplate or component label. Claude reads it, and we match it to the lifecycle knowledge base." />
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Photo">
          <input type="file" accept="image/*" capture="environment" onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} className="text-sm" />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          {preview && <img src={preview} alt="uploaded label" className="mt-3 w-full rounded border border-line" />}
          {busy && <p className="mt-2 text-sm text-muted">Reading the label…</p>}
          {err && <p className="mt-2 text-sm text-alert">{err}</p>}
        </Card>
        <Card title="What we found">
          {!res && <p className="text-sm text-muted">Upload a photo to start.</p>}
          {res && (
            <div className="space-y-3 text-sm">
              <div>
                <div className="text-xs text-muted">Read from the label {res.reading.cached && "(cached)"}</div>
                <div><b>{res.reading.manufacturer}</b> <PartNo>{res.reading.part_no}</PartNo> {res.reading.series && `ser ${res.reading.series}`}</div>
                <div className="text-muted">{res.reading.description} · S/N {res.reading.serial || "-"} · date {res.reading.date_code || "-"}</div>
                {res.reading.unclear.length > 0 && <Pill tone="warn">unclear: {res.reading.unclear.join(", ")}</Pill>}
              </div>
              {res.match ? (
                <div>
                  <div className="text-xs text-muted">Matched in the knowledge base ({res.match_method}, confidence {res.confidence})</div>
                  <div><PartNo>{res.match.part_no}</PartNo> {res.match.family} <StatusBadge status={res.match.lifecycle_status} /></div>
                  {res.match.successor_part_no && <div>Successor: <PartNo>{res.match.successor_part_no}</PartNo></div>}
                </div>
              ) : (
                <div className="text-muted">Not in our knowledge base yet. It goes to a person, and the KB grows with every scan.</div>
              )}
              {res.needs_review ? <Pill tone="warn">needs a person to confirm</Pill> : <Pill tone="ok">high confidence</Pill>}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
