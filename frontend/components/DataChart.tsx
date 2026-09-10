"use client";

import { Area, AreaChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useThemeColors } from "@/components/ThemeProvider";
import { formatValue } from "@/lib/api";

export type ChartSeries = { key: string; label: string; data: { year: number; value: number | null }[] };

export default function DataChart({ series, unit, height = 380 }: { series: ChartSeries[]; unit?: string | null; height?: number }) {
  const c = useThemeColors();
  const years = Array.from(new Set(series.flatMap((s) => s.data.map((d) => d.year)))).sort((a, b) => a - b);
  const rows = years.map((year) => {
    const row: Record<string, number | null> = { year };
    for (const s of series) row[s.key] = s.data.find((d) => d.year === year)?.value ?? null;
    return row;
  });

  if (!rows.length) {
    return (
      <div className="grid place-items-center text-center" style={{ height }}>
        <div>
          <p className="display text-2xl text-muted">No observations</p>
          <p className="mt-1 text-xs text-muted">Try another indicator or country.</p>
        </div>
      </div>
    );
  }

  const axis = { stroke: c.line, tick: { fill: c.muted, fontSize: 11, fontFamily: "var(--font-mono)" }, tickLine: false, axisLine: false };
  const tooltip = {
    contentStyle: { background: c.surface, border: `1px solid ${c.line}`, borderRadius: 0, fontSize: 12, fontFamily: "var(--font-sans)", color: c.ink },
    labelStyle: { color: c.muted, fontFamily: "var(--font-mono)", fontSize: 11, marginBottom: 4 },
    formatter: (v: number) => formatValue(v, unit),
    cursor: { stroke: c.muted, strokeDasharray: "3 3" },
  };

  if (series.length === 1) {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={rows} margin={{ top: 16, right: 8, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={c.series[0]} stopOpacity={0.28} />
              <stop offset="100%" stopColor={c.series[0]} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke={c.grid} vertical={false} />
          <XAxis dataKey="year" {...axis} minTickGap={24} />
          <YAxis {...axis} tickFormatter={(v) => formatValue(v, unit)} width={72} />
          <Tooltip {...tooltip} />
          <Area type="monotone" dataKey={series[0].key} name={series[0].label} stroke={c.series[0]} strokeWidth={2} fill="url(#fill)" connectNulls dot={false} activeDot={{ r: 4, fill: c.series[0], stroke: c.surface, strokeWidth: 2 }} />
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 16, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid stroke={c.grid} vertical={false} />
        <XAxis dataKey="year" {...axis} minTickGap={24} />
        <YAxis {...axis} tickFormatter={(v) => formatValue(v, unit)} width={72} />
        <Tooltip {...tooltip} />
        <Legend iconType="plainline" wrapperStyle={{ fontSize: 11, fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.08em", color: c.muted, paddingTop: 12 }} />
        {series.map((s, i) => (
          <Line key={s.key} type="monotone" dataKey={s.key} name={s.label} stroke={c.series[i % c.series.length]} strokeWidth={2} dot={false} connectNulls activeDot={{ r: 4, stroke: c.surface, strokeWidth: 2 }} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
