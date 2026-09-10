import type { CompareResponse } from "@/lib/api";
import { formatValue } from "@/lib/api";

export default function CompareTable({ result }: { result: CompareResponse }) {
  const unit = result.indicator.unit;
  const max = Math.max(...result.data.map((r) => Math.abs(r.value ?? 0)), 1);

  return (
    <div>
      <ol className="divide-y divide-line">
        {result.data.map((r) => (
          <li key={r.iso2} className="grid grid-cols-[2.5rem_1fr_auto] items-center gap-4 py-3 sm:grid-cols-[2.5rem_1fr_1fr_auto]">
            <span className="num text-2xl text-muted">{String(r.rank).padStart(2, "0")}</span>
            <div className="min-w-0">
              <p className="truncate font-medium">{r.name}</p>
              <p className="font-mono text-[11px] uppercase tracking-wider text-muted">
                {r.iso2} · {r.year ?? "—"}
              </p>
            </div>
            <div className="hidden h-1.5 w-full bg-line/60 sm:block">
              <div className="h-full bg-accent transition-all duration-700" style={{ width: `${Math.max(1.5, (Math.abs(r.value ?? 0) / max) * 100)}%` }} />
            </div>
            <span className="num text-xl tabular-nums">{formatValue(r.value, unit)}</span>
          </li>
        ))}
      </ol>
      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 border-t border-line pt-4 font-mono text-[11px] uppercase tracking-wider text-muted">
        <span>
          Continental avg <span className="text-ink">{formatValue(result.continental_average, unit)}</span>
        </span>
        {result.continental_total !== null && (
          <span>
            Total <span className="text-ink">{formatValue(result.continental_total, unit)}</span>
          </span>
        )}
        <span>
          <span className="text-ink">{result.countries_reporting}</span> countries reporting
        </span>
        {result.missing.length > 0 && <span>No data: {result.missing.join(", ")}</span>}
      </div>
    </div>
  );
}
