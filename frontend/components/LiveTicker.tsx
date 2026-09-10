"use client";

import { useEffect, useState } from "react";
import Ticker, { type TickerItem } from "@/components/Ticker";
import { api, formatValue, getApiKey } from "@/lib/api";

// Real 2023 World Bank figures so the page reads true even before the visitor has a key.
const STATIC: TickerItem[] = [
  { label: "Nigeria · GDP 2023", value: "$487.4B" },
  { label: "Egypt · GDP 2023", value: "$395.9B" },
  { label: "South Africa · GDP 2023", value: "$381.4B" },
  { label: "Ethiopia · GDP 2023", value: "$135.9B" },
  { label: "Kenya · GDP 2023", value: "$107.5B" },
  { label: "Africa · GDP 2023", value: "$2.99T" },
  { label: "East Africa · population", value: "512M" },
  { label: "Countries covered", value: "54" },
  { label: "Indicators", value: "87" },
  { label: "Observations", value: "1.2M+" },
];

export default function LiveTicker() {
  const [items, setItems] = useState<TickerItem[]>(STATIC);

  useEffect(() => {
    if (!getApiKey()) return;
    api
      .compare(["NG", "EG", "ZA", "ET", "KE"], "GDP_CURRENT_USD")
      .then((r) => {
        const live: TickerItem[] = r.data.map((d) => ({ label: `${d.name} · GDP ${d.year ?? ""}`, value: formatValue(d.value, "USD") }));
        if (r.continental_total) live.push({ label: `Africa · GDP ${r.year ?? ""}`, value: formatValue(r.continental_total, "USD") });
        setItems([...live, ...STATIC.slice(6)]);
      })
      .catch(() => {});
  }, []);

  return <Ticker items={items} />;
}
