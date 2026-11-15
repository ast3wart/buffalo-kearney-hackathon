export default function Loading() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-7 w-64 rounded bg-line" />
      <div className="h-4 w-96 rounded bg-line" />
      <div className="grid gap-4 md:grid-cols-4">
        {[0, 1, 2, 3].map((i) => <div key={i} className="h-24 rounded border border-line bg-surface" />)}
      </div>
      <div className="h-64 rounded border border-line bg-surface" />
    </div>
  );
}
