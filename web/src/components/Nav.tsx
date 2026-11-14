"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";
import type { components } from "@/lib/api-types";

type Company = components["schemas"]["Company"];

// Owners: Overview 💲 Asher · Early warning 🛠 Brandon · Linking + Brief shared
const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/links", label: "Linking" },
  { href: "/alerts", label: "Early warning" },
  { href: "/brief", label: "Supplier brief" },
];

export function Nav() {
  const path = usePathname();
  const params = useSearchParams();
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const company = params.get("company") ?? companies[0]?.company_id ?? "";

  useEffect(() => {
    fetch(`${API_URL}/companies`).then((r) => (r.ok ? r.json() : [])).then(setCompanies).catch(() => setCompanies([]));
  }, []);

  const withCompany = (href: string) => (company ? `${href}?company=${company}` : href);

  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
        <Link href={withCompany("/")} className="text-lg font-semibold tracking-tight">
          Afterlife
        </Link>
        <nav className="flex flex-wrap gap-1 text-sm">
          {LINKS.map((l) => {
            const active = l.href === "/" ? path === "/" : path.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={withCompany(l.href)}
                className={`rounded px-3 py-1.5 ${active ? "bg-accent-soft font-medium text-accent" : "text-muted hover:text-ink"}`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
        <label className="ml-auto flex items-center gap-2 text-sm text-muted">
          Company
          <select
            id="company"
            value={company}
            onChange={(e) => router.push(`${path}?company=${e.target.value}`)}
            className="rounded border border-line bg-surface px-2 py-1 text-ink"
          >
            {companies.map((c) => (
              <option key={c.company_id} value={c.company_id}>
                {c.company_name}
              </option>
            ))}
          </select>
        </label>
      </div>
    </header>
  );
}
