import { Deck, type DeckData, type SeriesPoint } from "@/components/Deck";
import { tryJSON } from "@/lib/api";

type Portfolio = {
  companies: { company_id: string; company_name: string }[];
  plants: { plant_name: string; state: string; employees: number; status: string; company_id: string }[];
};

export default async function PitchPage() {
  const [pf, s] = await Promise.all([
    tryJSON<Portfolio>("/portfolio"),
    tryJSON<{ points: SeriesPoint[] }>("/components/PA-L2-M01-C1/series"),
  ]);
  const names = Object.fromEntries((pf.data?.companies ?? []).map((c) => [c.company_id, c.company_name]));
  const plants: DeckData["plants"] = (pf.data?.plants ?? [])
    .filter((p) => p.status === "owned")
    .map((p) => ({ name: p.plant_name, state: p.state, employees: Number(p.employees), company: names[p.company_id] ?? "" }));
  return <Deck data={{ plants, series: s.data?.points ?? [] }} />;
}
