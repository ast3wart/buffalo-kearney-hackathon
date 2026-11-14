import { getJSON, type Health, API_URL } from "@/lib/api";
import { Card, PageHeader, Todo } from "@/components/ui";

// Overview: 💲 Asher. Calls GET /overview?company=… (docs/build/api.md)
export default async function Overview() {
  let health: Health | null = null;
  let error = "";
  try {
    health = await getJSON<Health>("/health");
  } catch (e) {
    error = String(e);
  }
  return (
    <>
      <PageHeader title="Overview" subtitle="Build cost vs. lifecycle cost, and how much of the spend and claims we could link." />
      <div className="space-y-4">
        <Todo owner="💲 Asher">coverage stats + build vs. lifecycle cost per product from GET /overview</Todo>
        {error ? (
          <Card tone="alert" title="API not reachable">
            <p className="text-sm">
              Can&apos;t reach {API_URL}. Run <code>python -m afterlife.run</code>, then{" "}
              <code>uvicorn api.main:app --reload</code>.
            </p>
          </Card>
        ) : (
          health && (
            <Card title={`Pipeline status · run at ${health.run_at}`}>
              <ul className="mb-3 text-sm">
                {health.companies.map((c) => (
                  <li key={c.company_id}>
                    <b>{c.company_name}</b> <span className="text-muted">· {c.industry} · data as of {c.data_as_of}</span>
                  </li>
                ))}
              </ul>
              <table className="w-full text-sm">
                <tbody>
                  {health.tables.map((t) => (
                    <tr key={t.name} className="border-t border-line">
                      <td className="py-1 font-mono">{t.name}</td>
                      <td className="tabular py-1 text-right">{t.rows}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )
        )}
      </div>
    </>
  );
}
