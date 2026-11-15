// Static export (GitHub Pages): every page is pre-rendered from the local API at build time.
import { API_URL } from "./api";

export const STATIC = process.env.STATIC_EXPORT === "1";

async function j<T>(path: string): Promise<T> {
  const r = await fetch(`${API_URL}${path}`, { cache: "force-cache" });
  return (await r.json()) as T;
}

export async function plantIds(): Promise<string[]> {
  const p = await j<{ plants: { plant_id: string }[] }>("/portfolio");
  return p.plants.map((x) => x.plant_id);
}

export async function machineIds(): Promise<string[]> {
  const out: string[] = [];
  for (const pid of await plantIds()) {
    const l = await j<{ lines: { machines: { machine_id: string }[] }[] }>(`/plants/${pid}/lines`);
    for (const ln of l.lines) for (const m of ln.machines) out.push(m.machine_id);
  }
  return out;
}

export async function componentIds(): Promise<string[]> {
  const out: string[] = [];
  for (const mid of await machineIds()) {
    const m = await j<{ parts: { component_id: string }[] }>(`/machines/${mid}`);
    for (const p of m.parts) out.push(p.component_id);
  }
  return out;
}
