import type { components } from "./api-types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
/** Path prefix when served from a subfolder (GitHub Pages project site). */
export const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
// Static export caches forever; the local app revalidates every second (live enough, and compatible with the
// pre-renderable dynamic routes the static export needs).
const FETCH_OPTS: RequestInit & { next?: { revalidate: number } } =
  process.env.STATIC_EXPORT === "1" ? { cache: "force-cache" } : { next: { revalidate: 1 } };
/** Photos are served by the API locally, and copied next to the pages in the static site. */
export const fileUrl = (path: string) => (process.env.STATIC_EXPORT === "1" ? `${BASE}/files${path}` : `${API_URL}${path}`);
export type Health = components["schemas"]["Health"];
export type Portfolio = components["schemas"]["Portfolio"];
export type PlantTile = components["schemas"]["PlantTile"];
export type ShelfMatch = components["schemas"]["ShelfMatch"];
export type Accuracy = components["schemas"]["Accuracy"];

export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, FETCH_OPTS);
  if (!r.ok) throw new Error(`${path} → ${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}

/** For Brandon's money routes: 501 = his module hasn't landed yet. */
export async function tryJSON<T>(path: string): Promise<{ data?: T; pending?: string; error?: string }> {
  try {
    const r = await fetch(`${API_URL}${path}`, FETCH_OPTS);
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
