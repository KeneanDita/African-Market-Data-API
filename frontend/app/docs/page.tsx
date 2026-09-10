import EndpointExample from "@/components/EndpointExample";

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/v1").replace(/\/v1$/, "");

type Example = { method?: "GET" | "POST"; path: string; body?: Record<string, unknown> };
type Section = { id: string; n: string; title: string; body: string; examples: Example[] };

const sections: Section[] = [
  {
    id: "auth",
    n: "01",
    title: "Authentication",
    body: "Every request under /v1 needs an X-API-Key header. Register once, keep the key secret, rotate it from the CLI if it leaks. Only a hash of the key is stored server-side.",
    examples: [{ method: "POST", path: "/v1/auth/register", body: { email: "dev@example.com", name: "Abebe Girma" } }, { path: "/v1/auth/me" }],
  },
  {
    id: "countries",
    n: "02",
    title: "Countries",
    body: "All 54 African Union members with ISO codes, capital, currency, area, languages and latest population. Filter by region; sort by name, population or area.",
    examples: [{ path: "/v1/countries?region=East%20Africa&sort=population&order=desc" }, { path: "/v1/countries/ET" }],
  },
  {
    id: "indicators",
    n: "03",
    title: "Indicators",
    body: "87 indicators across economy, demographics, health, education, infrastructure and finance. Each carries its unit, aggregation rule, upstream source and the source's original code.",
    examples: [{ path: "/v1/indicators?category=health" }, { path: "/v1/indicators/GDP_CURRENT_USD" }],
  },
  {
    id: "data",
    n: "04",
    title: "Data",
    body: "A time series for one country and indicator, with from / to / latest filters — or a full country snapshot with the latest value of every indicator.",
    examples: [{ path: "/v1/data/ET/GDP_CURRENT_USD?from=2010&to=2023" }, { path: "/v1/data/NG?category=economy" }],
  },
  {
    id: "compare",
    n: "05",
    title: "Compare",
    body: "Rank up to 5 (free) or 54 (pro) countries on one indicator. The continental average and total are computed across all of Africa. /compare/trend returns aligned series for charting.",
    examples: [{ path: "/v1/compare?countries=ET,NG,KE,ZA&indicator=GDP_CURRENT_USD&year=2023" }, { path: "/v1/compare/trend?countries=ET,KE,GH&indicator=GDP_GROWTH_ANNUAL&from=2010" }],
  },
  {
    id: "regions",
    n: "06",
    title: "Regions",
    body: "Africa's five regions and their members, plus per-region aggregates: absolute indicators (GDP, population) are summed, rates and ratios are averaged.",
    examples: [{ path: "/v1/regions" }, { path: "/v1/regions/west-africa/summary?category=economy" }],
  },
];

const graphqlExample = `query CompareGDP {
  compare(countries: ["ET", "KE", "GH", "NG"], indicator: "GDP_CURRENT_USD", year: 2023) {
    indicator { name unit }
    year
    continentalAverage
    rankings { rank value country { name iso2 } }
  }
  country(iso2: "ET") {
    name
    dataPoints(indicator: "INFLATION_ANNUAL", from: 2015) { year value }
  }
}`;

export default function DocsPage() {
  return (
    <div className="mx-auto max-w-page px-6 py-12">
      <div className="border-b border-line pb-10">
        <p className="eyebrow">Reference</p>
        <h1 className="display mt-3 text-5xl md:text-7xl">Documentation</h1>
        <p className="mt-6 max-w-2xl text-ink/75">
          Base URL <code className="font-mono text-sm text-accent">{API_BASE}/v1</code>. Machine-readable references:{" "}
          <a className="underline decoration-line underline-offset-4 hover:decoration-accent" href={`${API_BASE}/docs`}>Swagger</a>,{" "}
          <a className="underline decoration-line underline-offset-4 hover:decoration-accent" href={`${API_BASE}/redoc`}>ReDoc</a>,{" "}
          <a className="underline decoration-line underline-offset-4 hover:decoration-accent" href={`${API_BASE}/graphql`}>GraphiQL</a>.
        </p>
      </div>

      <div className="mt-10 grid gap-12 lg:grid-cols-[14rem_1fr]">
        {/* TOC */}
        <nav className="hidden lg:block">
          <ol className="sticky top-24 space-y-3">
            {sections.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`} className="group flex items-baseline gap-3 font-mono text-[11px] uppercase tracking-eyebrow text-muted hover:text-ink">
                  <span className="text-line group-hover:text-accent">{s.n}</span> {s.title}
                </a>
              </li>
            ))}
            <li>
              <a href="#graphql" className="group flex items-baseline gap-3 font-mono text-[11px] uppercase tracking-eyebrow text-muted hover:text-ink">
                <span className="text-line group-hover:text-accent">07</span> GraphQL
              </a>
            </li>
            <li>
              <a href="#conventions" className="group flex items-baseline gap-3 font-mono text-[11px] uppercase tracking-eyebrow text-muted hover:text-ink">
                <span className="text-line group-hover:text-accent">08</span> Conventions
              </a>
            </li>
          </ol>
        </nav>

        <div className="min-w-0">
          <div className="grid gap-px bg-line sm:grid-cols-3">
            {[
              ["Rate limits", "100 req/h free · 5,000 pro. Read X-RateLimit-Remaining and Retry-After."],
              ["Caching", "Data endpoints cache for 1h. X-Cache: HIT means the database wasn't touched."],
              ["Errors", "Standard HTTP codes. Bodies are { detail } with a human-readable hint."],
            ].map(([t, b]) => (
              <div key={t} className="bg-surface p-5">
                <p className="display text-xl">{t}</p>
                <p className="mt-2 text-xs leading-5 text-muted">{b}</p>
              </div>
            ))}
          </div>

          {sections.map((s) => (
            <section key={s.id} id={s.id} className="scroll-mt-24 border-t border-line pt-10 mt-14">
              <div className="grid gap-6 md:grid-cols-[4rem_1fr]">
                <span className="num text-4xl text-line">{s.n}</span>
                <div className="min-w-0">
                  <h2 className="display text-3xl md:text-4xl">{s.title}</h2>
                  <p className="mt-3 max-w-2xl text-[15px] leading-7 text-ink/70">{s.body}</p>
                  <div className="mt-6 space-y-3">
                    {s.examples.map((e) => <EndpointExample key={e.path} method={e.method ?? "GET"} path={e.path} body={e.body} />)}
                  </div>
                </div>
              </div>
            </section>
          ))}

          <section id="graphql" className="scroll-mt-24 border-t border-line pt-10 mt-14">
            <div className="grid gap-6 md:grid-cols-[4rem_1fr]">
              <span className="num text-4xl text-line">07</span>
              <div className="min-w-0">
                <h2 className="display text-3xl md:text-4xl">GraphQL</h2>
                <p className="mt-3 max-w-2xl text-[15px] leading-7 text-ink/70">
                  POST to <code className="font-mono text-sm text-accent">{API_BASE}/graphql</code> with the same X-API-Key header. Nested fields resolve lazily, so you pay only for the shape you ask for.
                </p>
                <pre className="code mt-6">{graphqlExample}</pre>
              </div>
            </div>
          </section>

          <section id="conventions" className="scroll-mt-24 border-t border-line pt-10 mt-14">
            <div className="grid gap-6 md:grid-cols-[4rem_1fr]">
              <span className="num text-4xl text-line">08</span>
              <div className="min-w-0">
                <h2 className="display text-3xl md:text-4xl">Conventions</h2>
                <dl className="mt-6 divide-y divide-line">
                  {[
                    ["Country codes", "ISO 3166-1 alpha-2, case-insensitive: ET, ng, Ke all work."],
                    ["Indicator codes", "Stable UPPER_SNAKE_CASE identifiers, e.g. GDP_CURRENT_USD, LIFE_EXPECTANCY, INTERNET_USERS_PCT."],
                    ["Years", "Integers. Free tier sees 2000 onward; Pro sees the full series from 1960."],
                    ["Values", "Numbers or null. Units are on the indicator (USD, percent, per_1000 …). Nothing is interpolated."],
                    ["Provenance", "Every data point carries its source. When sources disagree the higher-priority feed wins (World Bank > IMF)."],
                  ].map(([t, b]) => (
                    <div key={t} className="grid gap-2 py-4 md:grid-cols-[12rem_1fr]">
                      <dt className="font-medium">{t}</dt>
                      <dd className="text-sm leading-6 text-muted">{b}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
