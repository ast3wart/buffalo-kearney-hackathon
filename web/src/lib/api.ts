import type { components } from "./api-types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export type Health = components["schemas"]["Health"];

export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path} → ${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}
