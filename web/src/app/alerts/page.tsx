import { PageHeader, Todo } from "@/components/ui";

// Early warning: 🛠 Brandon. Calls GET /alerts and GET /claim-rates/{part_no} (both views: raw + MIS)
export default function AlertsPage() {
  return (
    <>
      <PageHeader title="Early warning" subtitle="Shared parts failing more often across products, measured at 3 months in service." />
      <Todo owner="🛠 Brandon">alert cards + claim-rate chart (raw build-month view next to the months-in-service view)</Todo>
    </>
  );
}
