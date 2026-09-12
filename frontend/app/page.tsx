import Link from "next/link";
import AfricaDotMap from "@/components/AfricaDotMap";
import EndpointExample from "@/components/EndpointExample";
import LiveTicker from "@/components/LiveTicker";
import CountUp from "@/components/motion/CountUp";
import GrowBar from "@/components/motion/GrowBar";
import Reveal from "@/components/motion/Reveal";

const sample = [
  { rank: "01", name: "Nigeria", iso2: "NG", value: "$487.4B", pct: 100 },
  { rank: "02", name: "Egypt", iso2: "EG", value: "$395.9B", pct: 81 },
  { rank: "03", name: "South Africa", iso2: "ZA", value: "$381.4B", pct: 78 },
  { rank: "04", name: "Ethiopia", iso2: "ET", value: "$135.9B", pct: 28 },
  { rank: "05", name: "Kenya", iso2: "KE", value: "$107.5B", pct: 22 },
];

const pillars = [
  { n: "01", title: "One schema for the whole continent", body: "World Bank, IMF, WHO and UN feeds normalized to the same ISO codes, units and indicator names. No more reconciling five spreadsheets." },
  { n: "02", title: "Comparison is the primitive", body: "Rank any set of countries on any indicator, pull aligned multi-country trends, or roll numbers up by region — one request each." },
  { n: "03", title: "REST when you want it, GraphQL when you need it", body: "Typed REST with generated docs, or a GraphQL schema with lazy nested resolvers so you fetch exactly the shape you render." },
  { n: "04", title: "Honest about the gaps", body: "Every value carries its source and year. Missing data is reported as missing, never interpolated silently." },
];

const categories = [
  ["Economy", "25", "GDP, inflation, debt, trade, FDI, remittances, poverty"],
  ["Demographics", "18", "Population, fertility, mortality, migration, urbanization"],
  ["Health", "15", "Expenditure, immunization, HIV, malaria, WASH, nutrition"],
  ["Education", "12", "Literacy, enrollment, completion, teacher ratios"],
  ["Infrastructure", "10", "Electricity, internet, mobile, transport, CO₂"],
  ["Finance", "7", "Account ownership, credit, market cap, lending rates"],
];

export default function Home() {
  return (
    <>
      {/* ---------------------------------------------------------------- hero */}
      <section className="relative mx-auto max-w-page overflow-hidden px-6 pb-16 pt-20 md:overflow-visible md:pt-28">
        <AfricaDotMap className="pointer-events-none absolute right-0 top-1/2 w-[30rem] -translate-y-1/2 opacity-40 animate-rise [animation-delay:240ms] md:w-[42rem] lg:w-[50rem] xl:w-[56rem] [mask-image:radial-gradient(62%_62%_at_center,black_45%,transparent_98%)]" />
        <div className="relative z-10">
          <p className="eyebrow animate-rise">Vol. 01 — Public beta</p>
          <h1 className="display mt-6 max-w-5xl text-[13vw] leading-[0.92] sm:text-7xl md:text-8xl lg:text-[7.5rem] animate-rise [animation-delay:80ms]">
            Fifty-four economies.
            <br />
            <span className="italic text-accent">One</span> API.
          </h1>
          <div className="mt-12 grid gap-10 md:grid-cols-[1fr_auto] md:items-end animate-rise [animation-delay:160ms]">
            <p className="max-w-xl text-lg leading-8 text-ink/75">
              Economic, demographic, health and market data for every African country — cleaned, normalized and served over REST and GraphQL.
              The reference desk the continent never had.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/dashboard" className="btn-ink">
                Get a free key <span className="arrow">→</span>
              </Link>
              <Link href="/explorer" className="btn-outline">
                Open the explorer
              </Link>
            </div>
          </div>
        </div>
      </section>

      <LiveTicker />

      {/* ---------------------------------------------------------------- numbers */}
      <section className="mx-auto max-w-page px-6 py-20">
        <div className="grid divide-y divide-line border-y border-line md:grid-cols-4 md:divide-x md:divide-y-0">
          {[
            ["54", "countries", "Every African Union member state, ISO-coded."],
            ["87", "indicators", "Across six categories, with unit and provenance."],
            ["1960", "onward", "Six decades of annual observations where they exist."],
            ["4", "sources", "World Bank · IMF · WHO · UN, reconciled nightly."],
          ].map(([n, label, body], i) => (
            <div key={label} className="py-8 md:px-8 md:first:pl-0 md:last:pr-0">
              <Reveal delay={i * 0.08}>
                <p className="num text-6xl md:text-7xl">
                  <CountUp value={Number(n)} />
                </p>
                <p className="eyebrow mt-2">{label}</p>
                <p className="mt-3 text-sm text-muted">{body}</p>
              </Reveal>
            </div>
          ))}
        </div>
      </section>

      {/* ---------------------------------------------------------------- sample */}
      <section className="mx-auto max-w-page px-6 pb-24">
        <div className="grid gap-12 lg:grid-cols-[5fr_7fr] lg:gap-20">
          <Reveal className="min-w-0">
            <p className="eyebrow">A single call</p>
            <h2 className="display mt-4 text-4xl md:text-5xl">
              Who has the biggest economy in Africa?
            </h2>
            <p className="mt-6 text-ink/75">
              <code className="font-mono text-sm text-accent">GET /v1/compare</code> ranks any group of countries and adds the continental average and total — computed across all 54, not just the ones you asked about.
            </p>
            <div className="mt-8">
              <EndpointExample path="/v1/compare?countries=NG,EG,ZA,ET,KE&indicator=GDP_CURRENT_USD&year=2023" />
            </div>
          </Reveal>
          <Reveal delay={0.1} className="card min-w-0 p-6 md:p-10">
            <div className="flex items-baseline justify-between">
              <p className="eyebrow">GDP, current US$ · 2023</p>
              <a className="eyebrow hover:text-accent" href="https://data.worldbank.org/indicator/NY.GDP.MKTP.CD" target="_blank" rel="noopener noreferrer">Source: World Bank ↗</a>
            </div>
            <ol className="mt-6 divide-y divide-line">
              {sample.map((r, i) => (
                <li key={r.iso2} className="grid grid-cols-[3rem_1fr_auto] items-center gap-4 py-4">
                  <span className="num text-3xl text-muted">{r.rank}</span>
                  <div>
                    <p className="display text-2xl">{r.name}</p>
                    <div className="mt-2 h-1 w-full bg-line/60">
                      <GrowBar pct={r.pct} delay={0.15 + i * 0.08} className="h-full bg-accent" />
                    </div>
                  </div>
                  <span className="num text-2xl">{r.value}</span>
                </li>
              ))}
            </ol>
            <div className="mt-6 flex flex-wrap gap-x-8 gap-y-2 border-t border-line pt-5 font-mono text-[11px] uppercase tracking-wider text-muted">
              <span>Continental total <span className="text-ink">$2.99T</span></span>
              <span>Average <span className="text-ink">$57.6B</span></span>
              <span><span className="text-ink">52</span> reporting</span>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ---------------------------------------------------------------- pillars */}
      <section className="border-y border-line bg-surface/50">
        <div className="mx-auto max-w-page px-6 py-24">
          <p className="eyebrow">Why it exists</p>
          <div className="mt-10 grid gap-px bg-line md:grid-cols-2">
            {pillars.map((p, i) => (
              <article key={p.n} className="group bg-paper p-8 transition hover:bg-surface md:p-12">
                <Reveal delay={(i % 2) * 0.1}>
                  <p className="num text-5xl text-line transition group-hover:text-accent">{p.n}</p>
                  <h3 className="display mt-6 text-2xl md:text-3xl">{p.title}</h3>
                  <p className="mt-4 max-w-md text-[15px] leading-7 text-ink/70">{p.body}</p>
                </Reveal>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------------- catalogue */}
      <section className="mx-auto max-w-page px-6 py-24">
        <Reveal className="flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="eyebrow">The catalogue</p>
            <h2 className="display mt-4 text-4xl md:text-5xl">Eighty-seven indicators, six shelves</h2>
          </div>
          <Link href="/docs" className="btn-outline">
            Read the docs <span className="arrow">→</span>
          </Link>
        </Reveal>
        <ul className="mt-12 divide-y divide-line border-y border-line">
          {categories.map(([name, count, desc], i) => (
            <li key={name} className="py-5">
              <Reveal delay={i * 0.05} className="grid items-baseline gap-2 md:grid-cols-[14rem_4rem_1fr]">
                <span className="display text-2xl">{name}</span>
                <span className="num text-2xl text-accent">{count}</span>
                <span className="text-sm text-muted">{desc}</span>
              </Reveal>
            </li>
          ))}
        </ul>
      </section>

      {/* ---------------------------------------------------------------- CTA */}
      <section className="mx-auto max-w-page px-6">
        <div className="relative overflow-hidden bg-ink px-8 py-16 text-paper md:px-16 md:py-24">
          <div className="kente absolute inset-x-0 top-0 opacity-90" aria-hidden />
          <Reveal>
            <p className="font-mono text-[11px] uppercase tracking-eyebrow text-paper/60">Start building</p>
            <h2 className="display mt-4 max-w-3xl text-4xl !text-paper md:text-6xl">
              Free for hackers, students and journalists. <span className="italic text-ochre">Forever.</span>
            </h2>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link href="/dashboard" className="btn bg-paper text-ink hover:bg-accent hover:text-white">
                Get a free key <span className="arrow">→</span>
              </Link>
              <Link href="/pricing" className="btn border border-paper/30 text-paper hover:border-paper hover:bg-paper hover:text-ink">
                See pricing
              </Link>
            </div>
          </Reveal>
        </div>
      </section>
    </>
  );
}
