import { PageHeader, Todo } from "@/components/ui";

// Linking explorer: shared. Calls GET /links?company=…&source=&q=&min_conf=
export default function LinksPage() {
  return (
    <>
      <PageHeader title="Linking" subtitle="Every raw record next to the part it was matched to, how, and how confidently." />
      <Todo owner="Shared">table of links (raw record · matched part · method · confidence) + accuracy from GET /accuracy</Todo>
    </>
  );
}
