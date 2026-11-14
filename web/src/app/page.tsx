import { getJSON, type Health, API_URL } from "@/lib/api";
import { Card, PageHeader } from "@/components/ui";

export default async function Overview() {
  let health: Health | null = null;
  try {
    health = await getJSON<Health>("/health");
  } catch {
    health = null;
  }
  return (
    <>
      <PageHeader title="Equipment X-Ray" subtitle="Pre-deal equipment diligence: CapEx cliff, single points of failure, parts sourcing." />
      {health?.ok ? (
        <Card title="API connected">
          <p className="text-sm">Screens get added here as the MVP is built.</p>
        </Card>
      ) : (
        <Card tone="alert" title="API not reachable">
          <p className="text-sm">
            Can&apos;t reach {API_URL}. Run <code>uvicorn api.main:app --reload</code>.
          </p>
        </Card>
      )}
    </>
  );
}
