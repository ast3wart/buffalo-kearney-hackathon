import { getJSON, type Health, API_URL } from "@/lib/api";

// Hello-world: proves Next.js → FastAPI → DuckDB works. Replace with the Overview screen.
export default async function Home() {
  let health: Health | null = null;
  let error = "";
  try {
    health = await getJSON<Health>("/health");
  } catch (e) {
    error = String(e);
  }
  return (
    <main className="mx-auto max-w-3xl px-4 py-12 space-y-6">
      <h1 className="text-3xl font-semibold">Afterlife</h1>
      {error ? (
        <div className="rounded border border-red-300 bg-red-50 p-4 text-sm text-red-800">
          Can&apos;t reach the API at {API_URL}. Start it with{" "}
          <code>uvicorn api.main:app --reload</code> after <code>python -m afterlife.run</code>.
          <pre className="mt-2 whitespace-pre-wrap">{error}</pre>
        </div>
      ) : (
        health && (
          <>
            <p className="text-sm text-gray-500">
              Data source: <code>{health.source}</code> · pipeline run at {health.run_at}
            </p>
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th className="py-1">Table</th><th className="py-1 text-right">Rows</th></tr></thead>
              <tbody>
                {health.tables.map((t) => (
                  <tr key={t.name} className="border-t"><td className="py-1 font-mono">{t.name}</td><td className="py-1 text-right tabular-nums">{t.rows}</td></tr>
                ))}
              </tbody>
            </table>
          </>
        )
      )}
    </main>
  );
}
