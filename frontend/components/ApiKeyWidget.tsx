"use client";

import { useEffect, useState } from "react";
import { api, ApiError, getApiKey, setApiKey, type MeResponse } from "@/lib/api";

export default function ApiKeyWidget({ onChange }: { onChange?: (me: MeResponse | null) => void }) {
  const [key, setKey] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [freshKey, setFreshKey] = useState<string | null>(null);
  const [me, setMe] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setKey(getApiKey());
  }, []);

  useEffect(() => {
    if (!key) {
      setMe(null);
      onChange?.(null);
      return;
    }
    api
      .me()
      .then((m) => {
        setMe(m);
        setError(null);
        onChange?.(m);
      })
      .catch((e: ApiError) => {
        setMe(null);
        setError(e.status === 401 ? "That key was rejected. Paste a valid key or register a new one." : e.message);
        onChange?.(null);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  async function register(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await api.register(email, name || undefined);
      setFreshKey(res.api_key);
      setApiKey(res.api_key);
      setKey(res.api_key);
    } catch (err) {
      setError((err as ApiError).message);
    } finally {
      setBusy(false);
    }
  }

  function useExisting(e: React.FormEvent) {
    e.preventDefault();
    const k = input.trim();
    if (!k) return;
    setApiKey(k);
    setKey(k);
    setInput("");
  }

  function signOut() {
    setApiKey(null);
    setKey(null);
    setFreshKey(null);
  }

  async function copyKey() {
    if (!freshKey) return;
    await navigator.clipboard.writeText(freshKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  if (key && me) {
    const pct = Math.min(100, Math.round((me.requests_this_hour / me.rate_limit) * 100));
    return (
      <div className="card p-6 md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Signed in as</p>
            <p className="display mt-1 text-3xl">{me.name ?? me.email}</p>
            <p className="mt-1 text-sm text-muted">{me.email}</p>
          </div>
          <span className="tag">{me.tier} tier</span>
        </div>

        {freshKey && (
          <div className="mt-6 border border-accent/50 bg-accent/5 p-4">
            <p className="eyebrow !text-accent">Your new key — shown once</p>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-3">
              <code className="break-all font-mono text-sm">{freshKey}</code>
              <button onClick={copyKey} className="btn-outline !py-1.5 text-xs">{copied ? "Copied" : "Copy"}</button>
            </div>
          </div>
        )}

        <div className="mt-8 grid gap-6 sm:grid-cols-3">
          <div>
            <p className="eyebrow">Key</p>
            <p className="mt-1 font-mono text-sm">{me.key_prefix}</p>
          </div>
          <div>
            <p className="eyebrow">Hourly limit</p>
            <p className="num mt-1 text-2xl">{me.rate_limit.toLocaleString()}</p>
          </div>
          <div>
            <p className="eyebrow">Used this hour</p>
            <p className="num mt-1 text-2xl">{me.requests_this_hour.toLocaleString()}</p>
          </div>
        </div>
        <div className="mt-4 h-1.5 w-full bg-line/60">
          <div className="h-full bg-accent transition-all duration-700" style={{ width: `${pct}%` }} />
        </div>

        <div className="mt-8 flex justify-end">
          <button className="btn-quiet text-xs" onClick={signOut}>Forget key on this device</button>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-px overflow-hidden border border-line bg-line md:grid-cols-2">
      <form onSubmit={register} className="bg-surface p-6 md:p-8">
        <p className="eyebrow">01 — New here?</p>
        <h3 className="display mt-2 text-3xl">Get a free key</h3>
        <div className="mt-6 space-y-5">
          <div>
            <label className="label" htmlFor="email">Email</label>
            <input id="email" className="field" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
          <div>
            <label className="label" htmlFor="name">Name (optional)</label>
            <input id="name" className="field" value={name} onChange={(e) => setName(e.target.value)} placeholder="Abebe Girma" />
          </div>
        </div>
        <button className="btn-ink mt-8" disabled={busy}>
          {busy ? "Creating…" : "Create API key"} <span className="arrow">→</span>
        </button>
        <p className="mt-4 text-xs text-muted">100 requests/hour · data from 2000 · compare up to 5 countries.</p>
      </form>

      <form onSubmit={useExisting} className="bg-surface p-6 md:p-8">
        <p className="eyebrow">02 — Returning</p>
        <h3 className="display mt-2 text-3xl">Use an existing key</h3>
        <div className="mt-6">
          <label className="label" htmlFor="key">API key</label>
          <input id="key" className="field font-mono" value={input} onChange={(e) => setInput(e.target.value)} placeholder="afr_live_…" />
        </div>
        <button className="btn-outline mt-8">Continue</button>
        <p className="mt-4 text-xs text-muted">Stored only in this browser&apos;s localStorage. Never sent anywhere but the API.</p>
      </form>

      {error && <p className="bg-surface px-6 py-3 text-sm text-accent md:col-span-2">{error}</p>}
    </div>
  );
}
