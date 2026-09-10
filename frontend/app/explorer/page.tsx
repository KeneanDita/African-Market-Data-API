"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import CompareTable from "@/components/CompareTable";
import DataChart, { type ChartSeries } from "@/components/DataChart";
import { api, ApiError, download, formatValue, getApiKey, toCsv, type CompareResponse, type Country, type Indicator, type SeriesResponse } from "@/lib/api";

const CATEGORIES: [string, string][] = [
  ["economy", "Economy"],
  ["demographics", "Demographics"],
  ["health", "Health"],
  ["education", "Education"],
  ["infrastructure", "Infrastructure"],
  ["finance", "Finance"],
];

const MAX_COMPARE = 5;

export default function ExplorerPage() {
  const [hasKey, setHasKey] = useState<boolean | null>(null);
  const [countries, setCountries] = useState<Country[]>([]);
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [category, setCategory] = useState("economy");
  const [indicatorCode, setIndicatorCode] = useState("GDP_CURRENT_USD");
  const [selected, setSelected] = useState<string[]>(["ET"]);
  const [compareMode, setCompareMode] = useState(false);
  const [year, setYear] = useState("");
  const [search, setSearch] = useState("");
  const [series, setSeries] = useState<ChartSeries[]>([]);
  const [single, setSingle] = useState<SeriesResponse | null>(null);
  const [ranking, setRanking] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const key = getApiKey();
    setHasKey(Boolean(key));
    if (!key) return;
    Promise.all([api.countries({ sort: "name" }), api.indicators()])
      .then(([c, i]) => {
        setCountries(c.data);
        setIndicators(i.data);
      })
      .catch((e: ApiError) => setError(e.message));
  }, []);

  const indicator = useMemo(() => indicators.find((i) => i.code === indicatorCode), [indicators, indicatorCode]);
  const categoryIndicators = useMemo(() => indicators.filter((i) => i.category === category), [indicators, category]);
  const visibleCountries = useMemo(() => {
    const q = search.trim().toLowerCase();
    return q ? countries.filter((c) => c.name.toLowerCase().includes(q) || c.iso2.toLowerCase() === q || c.region?.toLowerCase().includes(q)) : countries;
  }, [countries, search]);
  const selectedCountries = useMemo(() => selected.map((iso) => countries.find((c) => c.iso2 === iso)).filter(Boolean) as Country[], [selected, countries]);

  useEffect(() => {
    if (categoryIndicators.length && !categoryIndicators.some((i) => i.code === indicatorCode)) setIndicatorCode(categoryIndicators[0].code);
  }, [categoryIndicators, indicatorCode]);

  const load = useCallback(async () => {
    if (!selected.length || !indicatorCode) return;
    setLoading(true);
    setError(null);
    try {
      if (compareMode) {
        const [trend, cmp] = await Promise.all([api.trend(selected, indicatorCode), api.compare(selected, indicatorCode, year ? Number(year) : undefined)]);
        setSeries(trend.series.map((s) => ({ key: s.iso2, label: s.name, data: s.data })));
        setRanking(cmp);
        setSingle(null);
      } else {
        const res = await api.series(selected[0], indicatorCode);
        setSingle(res);
        setSeries([{ key: res.country.iso2, label: res.country.name, data: res.data }]);
        setRanking(null);
      }
    } catch (e) {
      setError((e as ApiError).message);
      setSeries([]);
      setRanking(null);
      setSingle(null);
    } finally {
      setLoading(false);
    }
  }, [selected, indicatorCode, compareMode, year]);

  useEffect(() => {
    if (hasKey) void load();
  }, [load, hasKey]);

  function toggleCountry(iso2: string) {
    if (!compareMode) return setSelected([iso2]);
    setSelected((prev) => (prev.includes(iso2) ? prev.filter((c) => c !== iso2) : prev.length >= MAX_COMPARE ? prev : [...prev, iso2]));
  }

  function exportCsv() {
    const rows = series.flatMap((s) => s.data.map((d) => ({ country: s.label, iso2: s.key, indicator: indicatorCode, year: d.year, value: d.value })));
    download(`${indicatorCode}_${selected.join("-")}.csv`, toCsv(rows), "text/csv");
  }

  function exportJson() {
    download(`${indicatorCode}_${selected.join("-")}.json`, JSON.stringify(ranking ?? single ?? series, null, 2), "application/json");
  }

  const latestChange = useMemo(() => {
    const pts = single?.data.filter((d) => d.value !== null) ?? [];
    if (pts.length < 2) return null;
    const a = pts[pts.length - 2].value as number;
    const b = pts[pts.length - 1].value as number;
    if (!a) return null;
    return { pct: ((b - a) / Math.abs(a)) * 100, from: pts[pts.length - 2].year, to: pts[pts.length - 1].year };
  }, [single]);

  if (hasKey === false) {
    return (
      <div className="mx-auto max-w-page px-6 py-32">
        <p className="eyebrow">Explorer</p>
        <h1 className="display mt-4 max-w-3xl text-5xl md:text-7xl">The explorer needs a key.</h1>
        <p className="mt-6 max-w-md text-ink/70">It&apos;s free, takes ten seconds, and unlocks every chart on this page.</p>
        <Link href="/dashboard" className="btn-ink mt-10">
          Get a free key <span className="arrow">→</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-page px-6 py-10">
      {/* header */}
      <div className="flex flex-wrap items-end justify-between gap-6 border-b border-line pb-8">
        <div className="min-w-0">
          <p className="eyebrow">Explorer · {compareMode ? "Compare" : "Single country"}</p>
          <h1 className="display mt-3 max-w-4xl text-4xl leading-tight md:text-6xl">{indicator?.name ?? "Loading…"}</h1>
          {indicator?.description && <p className="mt-4 max-w-2xl text-sm leading-6 text-muted">{indicator.description}</p>}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            className={compareMode ? "btn-ink" : "btn-outline"}
            onClick={() => {
              setCompareMode((m) => !m);
              setSelected((s) => s.slice(0, 1));
            }}
          >
            {compareMode ? "Compare: on" : "Compare"}
          </button>
          <button className="btn-quiet" onClick={exportCsv} disabled={!series.length}>CSV ↓</button>
          <button className="btn-quiet" onClick={exportJson} disabled={!series.length}>JSON ↓</button>
        </div>
      </div>

      {/* category tabs */}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
        <div className="segment">
          {CATEGORIES.map(([k, label]) => (
            <button key={k} aria-pressed={category === k} onClick={() => setCategory(k)}>{label}</button>
          ))}
        </div>
        <div className="flex flex-wrap items-end gap-6">
          <div className="w-72">
            <label className="label" htmlFor="indicator">Indicator</label>
            <select id="indicator" className="field" value={indicatorCode} onChange={(e) => setIndicatorCode(e.target.value)}>
              {categoryIndicators.map((i) => <option key={i.code} value={i.code}>{i.name}</option>)}
            </select>
          </div>
          {compareMode && (
            <div className="w-32">
              <label className="label" htmlFor="year">Rank year</label>
              <input id="year" className="field font-mono" inputMode="numeric" placeholder="latest" value={year} onChange={(e) => setYear(e.target.value.replace(/\D/g, "").slice(0, 4))} />
            </div>
          )}
        </div>
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[17rem_1fr]">
        {/* country rail */}
        <aside>
          <div className="flex items-baseline justify-between">
            <p className="eyebrow">Countries</p>
            {compareMode && <p className="font-mono text-[11px] text-muted">{selected.length}/{MAX_COMPARE}</p>}
          </div>
          <input className="field mt-2" placeholder="Search name, ISO or region…" value={search} onChange={(e) => setSearch(e.target.value)} />
          <ul className="scrollbar-thin mt-3 max-h-[36rem] overflow-y-auto pr-2">
            {visibleCountries.map((c) => {
              const active = selected.includes(c.iso2);
              return (
                <li key={c.iso2}>
                  <button
                    onClick={() => toggleCountry(c.iso2)}
                    className={`group flex w-full items-center justify-between border-b border-line py-2.5 text-left text-sm transition ${active ? "text-ink" : "text-muted hover:text-ink"}`}
                  >
                    <span className="flex items-center gap-2">
                      <span className={`h-1.5 w-1.5 rounded-full transition ${active ? "bg-accent" : "bg-transparent group-hover:bg-line"}`} />
                      {c.name}
                    </span>
                    <span className="font-mono text-[11px] tracking-wider">{c.iso2}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* main */}
        <section className="min-w-0 space-y-10">
          {/* stat header */}
          {!compareMode && single && (
            <div className="grid gap-6 border-b border-line pb-8 md:grid-cols-[1fr_auto] md:items-end">
              <div>
                <p className="eyebrow">{single.country.name} · latest {single.latest?.year ?? ""}</p>
                <p className="num mt-3 text-6xl leading-none md:text-8xl">{formatValue(single.latest?.value, indicator?.unit)}</p>
              </div>
              <dl className="grid grid-cols-3 gap-6 text-right md:text-left">
                <div>
                  <dt className="eyebrow">Change</dt>
                  <dd className={`num mt-1 text-xl ${latestChange && latestChange.pct < 0 ? "text-accent" : "text-moss"}`}>
                    {latestChange ? `${latestChange.pct > 0 ? "+" : ""}${latestChange.pct.toFixed(1)}%` : "—"}
                  </dd>
                  {latestChange && <dd className="font-mono text-[10px] text-muted">{latestChange.from}→{latestChange.to}</dd>}
                </div>
                <div>
                  <dt className="eyebrow">Points</dt>
                  <dd className="num mt-1 text-xl">{single.count}</dd>
                </div>
                <div>
                  <dt className="eyebrow">Source</dt>
                  <dd className="mt-1 text-sm">{single.source ?? "—"}</dd>
                </div>
              </dl>
            </div>
          )}
          {compareMode && (
            <div className="flex flex-wrap gap-2 border-b border-line pb-6">
              {selectedCountries.length ? (
                selectedCountries.map((c, i) => (
                  <button key={c.iso2} onClick={() => toggleCountry(c.iso2)} className="tag !normal-case !tracking-normal hover:border-accent" title="Remove">
                    <span className="h-2 w-2 rounded-full" style={{ background: ["rgb(var(--c-accent))", "rgb(var(--c-indigo))", "rgb(var(--c-moss))", "rgb(var(--c-ochre))", "rgb(var(--c-ink))"][i % 5] }} />
                    {c.name} ×
                  </button>
                ))
              ) : (
                <p className="text-sm text-muted">Pick up to {MAX_COMPARE} countries from the list.</p>
              )}
            </div>
          )}

          {/* chart */}
          <div>
            <div className="mb-3 flex items-baseline justify-between">
              <p className="eyebrow">{compareMode ? "Trend" : "Time series"}</p>
              {indicator?.unit && <p className="eyebrow">{indicator.unit.replace(/_/g, " ")}</p>}
            </div>
            <div className={`transition-opacity ${loading ? "opacity-40" : ""}`}>
              <DataChart series={series} unit={indicator?.unit} />
            </div>
            {error && <p className="mt-3 text-sm text-accent">{error}</p>}
          </div>

          {/* ranking */}
          {ranking && (
            <div>
              <p className="eyebrow mb-4">Ranking · {ranking.year ?? "latest available"}</p>
              <CompareTable result={ranking} />
            </div>
          )}

          {/* raw */}
          {single && !compareMode && single.data.length > 0 && (
            <div>
              <p className="eyebrow mb-4">Observations</p>
              <div className="grid grid-cols-3 gap-px bg-line sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8">
                {single.data.map((d) => (
                  <div key={d.year} className="bg-paper p-3 transition hover:bg-surface">
                    <p className="font-mono text-[10px] text-muted">{d.year}</p>
                    <p className="num mt-1 text-sm">{formatValue(d.value, indicator?.unit)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
