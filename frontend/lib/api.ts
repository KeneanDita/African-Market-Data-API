// Typed client for the African Market Data API. Runs in the browser; the API key lives in localStorage.

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/v1";
export const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL ?? "http://localhost:8000/graphql";
export const API_KEY_STORAGE = "africadata.apiKey";

export type Country = {
  iso2: string;
  iso3: string;
  name: string;
  region: string | null;
  capital: string | null;
  currency: string | null;
  currency_code: string | null;
  population: number | null;
  area_km2: number | null;
  languages: string[] | null;
};

export type Indicator = {
  code: string;
  name: string;
  category: string;
  subcategory: string | null;
  unit: string | null;
  aggregation: "sum" | "mean";
  source: string | null;
  source_code: string | null;
  description: string | null;
};

export type DataPoint = { year: number; value: number | null };

export type SeriesResponse = {
  country: { iso2: string; name: string };
  indicator: { code: string; name: string; unit: string | null };
  data: DataPoint[];
  latest: DataPoint | null;
  count: number;
  source: string | null;
  last_updated: string | null;
};

export type CompareResponse = {
  indicator: { code: string; name: string; unit: string | null };
  year: number | null;
  data: { iso2: string; name: string; value: number | null; year: number | null; rank: number }[];
  continental_average: number | null;
  continental_total: number | null;
  countries_reporting: number;
  missing: string[];
};

export type TrendResponse = {
  indicator: { code: string; name: string; unit: string | null };
  from_year: number | null;
  to_year: number | null;
  series: { iso2: string; name: string; data: DataPoint[] }[];
};

export type MeResponse = {
  email: string;
  name: string | null;
  key_prefix: string;
  tier: string;
  rate_limit: number;
  requests_this_hour: number;
  requests_remaining: number;
  created_at: string | null;
  last_seen_at: string | null;
};

export class ApiError extends Error {
  constructor(public status: number, message: string, public detail?: unknown) {
    super(message);
  }
}

export function getApiKey(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(API_KEY_STORAGE);
}

export function setApiKey(key: string | null) {
  if (typeof window === "undefined") return;
  if (key) window.localStorage.setItem(API_KEY_STORAGE, key);
  else window.localStorage.removeItem(API_KEY_STORAGE);
  window.dispatchEvent(new Event("africadata:key-changed"));
}

type Query = Record<string, string | number | boolean | undefined | null>;

function qs(params?: Query): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "");
  if (!entries.length) return "";
  return "?" + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
}

async function request<T>(path: string, init: RequestInit = {}, params?: Query): Promise<T> {
  const key = getApiKey();
  const headers: Record<string, string> = { Accept: "application/json", ...(init.headers as Record<string, string>) };
  if (key) headers["X-API-Key"] = key;
  if (init.body) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_URL}${path}${qs(params)}`, { ...init, headers, cache: "no-store" });
  const text = await res.text();
  const body = text ? safeJson(text) : null;
  if (!res.ok) {
    const detail = (body as { detail?: unknown })?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : (detail as { error?: string })?.error ?? (detail as { hint?: string })?.hint ?? `Request failed (${res.status})`;
    throw new ApiError(res.status, message, detail);
  }
  return body as T;
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export const api = {
  register: (email: string, name?: string) =>
    request<{ api_key: string; tier: string; rate_limit: string; docs: string; message: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, name }),
    }),
  me: () => request<MeResponse>("/auth/me"),
  countries: (params?: { region?: string; sort?: string; order?: "asc" | "desc" }) =>
    request<{ data: Country[]; total: number }>("/countries", {}, params),
  country: (iso2: string) => request<Country>(`/countries/${iso2}`),
  indicators: (category?: string) => request<{ data: Indicator[]; total: number; categories: string[] }>("/indicators", {}, { category }),
  series: (iso2: string, code: string, params?: { from?: number; to?: number; latest?: boolean }) =>
    request<SeriesResponse>(`/data/${iso2}/${code}`, {}, params),
  snapshot: (iso2: string, category?: string) =>
    request<{ country: { iso2: string; name: string }; data: { indicator: { code: string; name: string; unit: string | null }; category: string; year: number; value: number | null }[]; total: number }>(
      `/data/${iso2}`,
      {},
      { category },
    ),
  compare: (countries: string[], indicator: string, year?: number) =>
    request<CompareResponse>("/compare", {}, { countries: countries.join(","), indicator, year }),
  trend: (countries: string[], indicator: string, from?: number, to?: number) =>
    request<TrendResponse>("/compare/trend", {}, { countries: countries.join(","), indicator, from, to }),
  regions: () =>
    request<{ data: { name: string; slug: string; country_count: number; population: number | null; countries: { iso2: string; name: string }[] }[]; total: number }>("/regions"),
};

export function formatValue(value: number | null | undefined, unit?: string | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const abs = Math.abs(value);
  const isMoney = unit === "USD" || unit === "international_USD";
  const prefix = isMoney ? "$" : "";
  if (unit === "percent" || unit === "percent_gdp") return `${value.toFixed(1)}%`;
  if (abs >= 1e12) return `${prefix}${(value / 1e12).toFixed(2)}T`;
  if (abs >= 1e9) return `${prefix}${(value / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `${prefix}${(value / 1e6).toFixed(1)}M`;
  if (abs >= 1e4) return `${prefix}${Math.round(value).toLocaleString()}`;
  return `${prefix}${Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2)}`;
}

export function toCsv(rows: Record<string, string | number | null>[]): string {
  if (!rows.length) return "";
  const cols = Object.keys(rows[0]);
  const esc = (v: string | number | null) => (v === null ? "" : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
  return [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
}

export function download(filename: string, content: string, type = "text/plain") {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
