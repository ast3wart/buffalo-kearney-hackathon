import { PageHeader, Todo } from "@/components/ui";

// Supplier list → /brief/[supplier]: shared
export default function BriefIndex() {
  return (
    <>
      <PageHeader title="Supplier brief" subtitle="Pick a supplier to generate its recovery + pricing brief." />
      <Todo owner="Shared">supplier list ranked by linked claim cost (recovery opportunity, scenario range) + spare-part overspend</Todo>
    </>
  );
}
