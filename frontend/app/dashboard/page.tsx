"use client";

import Link from "next/link";
import { useState } from "react";
import ApiKeyWidget from "@/components/ApiKeyWidget";
import EndpointExample from "@/components/EndpointExample";
import type { MeResponse } from "@/lib/api";

export default function DashboardPage() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const graphqlUrl = process.env.NEXT_PUBLIC_GRAPHQL_URL ?? "http://localhost:8000/graphql";

  return (
    <div className="mx-auto max-w-page px-6 py-12">
      <div className="flex flex-wrap items-end justify-between gap-6 border-b border-line pb-8">
        <div>
          <p className="eyebrow">Account</p>
          <h1 className="display mt-3 text-5xl md:text-6xl">Dashboard</h1>
        </div>
        {me?.tier === "free" && (
          <Link href="/pricing" className="btn-outline">
            Upgrade to Pro <span className="arrow">→</span>
          </Link>
        )}
      </div>

      <div className="mt-10">
        <ApiKeyWidget onChange={setMe} />
      </div>

      {me && (
        <dl className="mt-10 grid divide-y divide-line border-y border-line md:grid-cols-3 md:divide-x md:divide-y-0">
          <div className="py-6 md:px-8 md:first:pl-0">
            <dt className="eyebrow">Remaining this hour</dt>
            <dd className="num mt-2 text-5xl">{me.requests_remaining.toLocaleString()}</dd>
            <dd className="mt-1 text-xs text-muted">resets at the top of the hour</dd>
          </div>
          <div className="py-6 md:px-8">
            <dt className="eyebrow">Last request</dt>
            <dd className="display mt-2 text-2xl">{me.last_seen_at ? new Date(me.last_seen_at).toLocaleString() : "—"}</dd>
          </div>
          <div className="py-6 md:px-8 md:last:pr-0">
            <dt className="eyebrow">Member since</dt>
            <dd className="display mt-2 text-2xl">{me.created_at ? new Date(me.created_at).toLocaleDateString(undefined, { dateStyle: "long" }) : "—"}</dd>
          </div>
        </dl>
      )}

      <section className="mt-20 grid gap-10 lg:grid-cols-[1fr_2fr]">
        <div>
          <p className="eyebrow">Quick start</p>
          <h2 className="display mt-3 text-3xl md:text-4xl">Your first three calls</h2>
          <p className="mt-4 text-sm leading-6 text-muted">
            Full reference in the <Link href="/docs" className="text-ink underline decoration-line underline-offset-4 hover:decoration-accent">docs</Link>, or try queries live in the{" "}
            <a href={graphqlUrl} className="text-ink underline decoration-line underline-offset-4 hover:decoration-accent">GraphQL playground</a>.
          </p>
        </div>
        <div className="min-w-0 space-y-4">
          <EndpointExample path="/v1/data/ET/GDP_CURRENT_USD?from=2010" description="Ethiopia's GDP time series since 2010." />
          <EndpointExample path="/v1/data/NG" description="Nigeria snapshot — the latest value of every indicator." />
          <EndpointExample path="/v1/regions/west-africa/summary?category=economy" description="West Africa rolled up: sums for totals, means for rates." />
        </div>
      </section>
    </div>
  );
}
