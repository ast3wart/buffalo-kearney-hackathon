import type { components } from "./api-types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export type Health = components["schemas"]["Health"];
export type Company = components["schemas"]["Company"];
export type Overview = components["schemas"]["Overview"];
export type Markup = components["schemas"]["Markup"];
export type Harmonization = components["schemas"]["Harmonization"];
export type Compliance = components["schemas"]["Compliance"];

/** ?company=… from the URL, or the first company the API knows about. */
export async function resolveCompany(param: string | string[] | undefined): Promise<string> {
  if (typeof param === "string" && param) return param;
  const companies = await getJSON<Company[]>("/companies");
  return companies[0]?.company_id ?? "";
}

export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path} → ${r.status}: ${await r.text()}`);
  return r.json() as Promise<T>;
}
