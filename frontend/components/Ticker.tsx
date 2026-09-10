export type TickerItem = { label: string; value: string; delta?: string };

export default function Ticker({ items }: { items: TickerItem[] }) {
  const doubled = [...items, ...items];
  return (
    <div className="ticker-mask overflow-hidden border-y border-line bg-surface/60">
      <div className="flex w-max animate-ticker gap-12 py-3 hover:[animation-play-state:paused]">
        {doubled.map((it, i) => (
          <div key={i} className="flex items-baseline gap-3 whitespace-nowrap">
            <span className="font-mono text-[11px] uppercase tracking-eyebrow text-muted">{it.label}</span>
            <span className="num text-lg">{it.value}</span>
            {it.delta && <span className={`font-mono text-[11px] ${it.delta.startsWith("-") ? "text-accent" : "text-moss"}`}>{it.delta}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
