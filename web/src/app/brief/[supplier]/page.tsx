import { PageHeader, Todo } from "@/components/ui";

// Brief: shared. Streams POST /brief/{supplier_id}?company=… (🛠 warranty section + 💲 pricing section)
export default async function BriefPage({ params }: { params: Promise<{ supplier: string }> }) {
  const { supplier } = await params;
  return (
    <>
      <PageHeader title={`Supplier brief · ${supplier}`} />
      <Todo owner="Shared">stream the brief; Ask 1 warranty recovery (🛠), Ask 2 price harmonization (💲)</Todo>
    </>
  );
}
