import type { components } from "./api-types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export type Health = components["schemas"]["Health"];
export type Portfolio = components["schemas"]["Portfolio"];
export type PlantTile = components["schemas"]["PlantTile"];
export type ShelfMatch = components["schemas"]["ShelfMatch"];
export type Accuracy = components["schemas"]["Accuracy"];

export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path} → ${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}

/** For Brandon's money routes: 501 = his module hasn't landed yet. */
export async function tryJSON<T>(path: string): Promise<{ data?: T; pending?: string; error?: string }> {
  try {
    const r = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (r.status === 501) return { pending: ((await r.json()) as { detail: string }).detail };
    if (!r.ok) return { error: `${r.status}: ${await r.text()}` };
    return { data: (await r.json()) as T };
  } catch (e) {
    return { error: String(e) };
  }
}

export const pct = (x: number) => `${Math.round(x * 100)}%`;
export const usd = (x: number) =>
  x >= 1e6 ? `$${(x / 1e6).toFixed(1)}M` : x >= 1e5 ? `$${Math.round(x / 1e3)}k` : `$${Math.round(x).toLocaleString("en-US")}`;
