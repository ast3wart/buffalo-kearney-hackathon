import { readFile } from "node:fs/promises";
import path from "node:path";
import { Deck, type DeckData } from "@/components/Deck";
import { tryJSON } from "@/lib/api";

type Portfolio = {
  companies: { company_id: string; company_name: string; fund_id: string }[];
  plants: { plant_name: string; state: string; employees: number; lines: number; machines: number; status: string; company_id: string }[];
};

// owned_since and deal values live only in the seed CSV (fictional client).
async function companyFacts(): Promise<Record<string, { since: string; dealLow: number; dealHigh: number }>> {
  try {
    const csv = await readFile(path.join(process.cwd(), "..", "data/seed/demo/portfolio.csv"), "utf8");
    const [head, ...rows] = csv.trim().split("\n").map((l) => l.split(","));
    return Object.fromEntries(rows.map((r) => {
      const o = Object.fromEntries(head.map((h, i) => [h, r[i] ?? ""]));
      return [o.company_id, { since: o.owned_since.slice(0, 4), dealLow: Number(o.deal_value_low) || 0, dealHigh: Number(o.deal_value_high) || 0 }];
    }));
  } catch {
    return {};
  }
}

export default async function PitchPage() {
  const [pf, facts] = await Promise.all([tryJSON<Portfolio>("/portfolio"), companyFacts()]);
  const plants = pf.data?.plants ?? [];
  const companies: DeckData["companies"] = (pf.data?.companies ?? []).map((c) => ({
    name: c.company_name,
    owned: Boolean(c.fund_id),
    since: facts[c.company_id]?.since ?? "",
    deal: facts[c.company_id]?.dealHigh ? `$${facts[c.company_id].dealLow / 1e6}–${facts[c.company_id].dealHigh / 1e6}M` : "",
    plants: plants
      .filter((p) => p.company_id === c.company_id)
      .map((p) => ({ name: p.plant_name, state: p.state, employees: Number(p.employees), lines: Number(p.lines), machines: Number(p.machines) })),
  }));
  return <Deck data={{ companies }} />;
}
