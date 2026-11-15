"use client";

import { useMemo, useState } from "react";

export type IndexItem = { id: string; title: string; section: string; keywords: string };

// Sticky index: type a word ("weibull", "28%", "install", "cellular") and jump straight to it.
export function AppendixIndex({ items, sections }: { items: IndexItem[]; sections: { id: string; title: string }[] }) {
  const [q, setQ] = useState("");
  const hits = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!words.length) return [];
    return items.filter((it) => words.every((w) => `${it.title} ${it.section} ${it.keywords}`.toLowerCase().includes(w))).slice(0, 12);
  }, [q, items]);
  const go = (id: string) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    el.classList.add("ring-2", "ring-accent");
    setTimeout(() => el.classList.remove("ring-2", "ring-accent"), 1600);
  };
  return (
    <nav className="sticky top-4 space-y-4">
      <div>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && hits[0] && go(hits[0].id)}
          placeholder="Search the appendix…"
          className="w-full rounded border border-line bg-surface px-3 py-2 text-sm outline-none focus:border-accent"
          aria-label="Search the appendix"
        />
        {q && (
          <ul className="mt-1 max-h-72 overflow-auto rounded border border-line bg-surface text-sm shadow-sm">
            {hits.length ? hits.map((h) => (
              <li key={h.id}>
                <button onClick={() => go(h.id)} className="w-full px-3 py-1.5 text-left hover:bg-accent-soft">
                  <div className="font-medium">{h.title}</div>
                  <div className="text-xs text-muted">{h.section}</div>
                </button>
              </li>
            )) : <li className="px-3 py-2 text-muted">No match. Try another word.</li>}
          </ul>
        )}
      </div>
      <ol className="space-y-1 text-sm">
        {sections.map((s, i) => (
          <li key={s.id}>
            <button onClick={() => go(s.id)} className="text-left text-muted hover:text-accent">
              <span className="tabular mr-1.5 text-xs">{String(i + 1).padStart(2, "0")}</span>{s.title}
            </button>
          </li>
        ))}
      </ol>
    </nav>
  );
}
