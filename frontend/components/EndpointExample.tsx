"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";

type Props = {
  method?: "GET" | "POST";
  path: string;
  body?: Record<string, unknown>;
  description?: string;
};

export default function EndpointExample({ method = "GET", path, body, description }: Props) {
  const [lang, setLang] = useState<"curl" | "js" | "py">("curl");
  const [copied, setCopied] = useState(false);
  const base = API_URL.replace(/\/v1$/, "");
  const url = `${base}${path}`;
  const json = body ? JSON.stringify(body) : undefined;

  const snippets = {
    curl: [
      `curl -X ${method} "${url}" \\`,
      `  -H "X-API-Key: $AFRICADATA_KEY"${json ? " \\" : ""}`,
      ...(json ? [`  -H "Content-Type: application/json" \\`, `  -d '${json}'`] : []),
    ].join("\n"),
    js: [
      `const res = await fetch("${url}", {`,
      `  method: "${method}",`,
      `  headers: { "X-API-Key": process.env.AFRICADATA_KEY${json ? `, "Content-Type": "application/json"` : ""} },`,
      ...(json ? [`  body: JSON.stringify(${JSON.stringify(body)}),`] : []),
      `});`,
      `const data = await res.json();`,
    ].join("\n"),
    py: [
      `import httpx`,
      ``,
      `r = httpx.${method.toLowerCase()}(`,
      `    "${url}",`,
      `    headers={"X-API-Key": AFRICADATA_KEY},`,
      ...(json ? [`    json=${JSON.stringify(body)},`] : []),
      `)`,
      `data = r.json()`,
    ].join("\n"),
  };

  async function copy() {
    await navigator.clipboard.writeText(snippets[lang]);
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  }

  return (
    <div className="card overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-4 py-2.5">
        <div className="flex min-w-0 items-center gap-3 font-mono text-xs">
          <span className={`font-semibold ${method === "GET" ? "text-moss" : "text-indigo"}`}>{method}</span>
          <span className="truncate text-ink/80">{path}</span>
        </div>
        <div className="flex items-center gap-1 font-mono text-[11px] uppercase tracking-wider">
          {(["curl", "js", "py"] as const).map((l) => (
            <button key={l} onClick={() => setLang(l)} className={`px-2 py-0.5 transition ${lang === l ? "text-ink underline decoration-accent underline-offset-4" : "text-muted hover:text-ink"}`}>
              {l === "js" ? "JS" : l === "py" ? "Python" : "cURL"}
            </button>
          ))}
          <button onClick={copy} className="ml-2 text-muted hover:text-ink">
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>
      {description && <p className="border-b border-line px-4 py-3 text-sm text-muted">{description}</p>}
      <pre className="code">{snippets[lang]}</pre>
    </div>
  );
}
