"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { THEME_STORAGE_KEY, type Theme } from "@/lib/theme";

type ThemeContextValue = { theme: Theme; toggle: () => void; setTheme: (t: Theme) => void };

const ThemeContext = createContext<ThemeContextValue>({ theme: "light", toggle: () => {}, setTheme: () => {} });

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("light");

  useEffect(() => {
    setThemeState(document.documentElement.classList.contains("dark") ? "dark" : "light");
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem(THEME_STORAGE_KEY)) apply(e.matches ? "dark" : "light", false);
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  const apply = (t: Theme, persist = true) => {
    document.documentElement.classList.toggle("dark", t === "dark");
    if (persist) localStorage.setItem(THEME_STORAGE_KEY, t);
    setThemeState(t);
  };

  const setTheme = useCallback((t: Theme) => apply(t), []);
  const toggle = useCallback(() => apply(theme === "dark" ? "light" : "dark"), [theme]);

  const value = useMemo(() => ({ theme, toggle, setTheme }), [theme, toggle, setTheme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}

/** Resolves the current CSS color tokens to rgb() strings for canvas/SVG libraries like Recharts. */
export function useThemeColors() {
  const { theme } = useTheme();
  return useMemo(() => {
    if (typeof window === "undefined") return FALLBACK;
    const css = getComputedStyle(document.documentElement);
    const read = (name: string) => `rgb(${css.getPropertyValue(`--c-${name}`).trim() || FALLBACK_RGB[name]})`;
    return {
      ink: read("ink"),
      muted: read("muted"),
      line: read("line"),
      surface: read("surface"),
      series: [read("accent"), read("indigo"), read("moss"), read("ochre"), read("ink")],
      grid: css.getPropertyValue("--chart-grid").trim() || FALLBACK.grid,
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme]);
}

const FALLBACK_RGB: Record<string, string> = { ink: "22 20 15", muted: "107 101 91", line: "214 206 192", surface: "251 248 242", accent: "194 69 31", indigo: "43 58 140", moss: "31 95 74", ochre: "201 148 24" };
const FALLBACK = {
  ink: "rgb(22 20 15)",
  muted: "rgb(107 101 91)",
  line: "rgb(214 206 192)",
  surface: "rgb(251 248 242)",
  series: ["rgb(194 69 31)", "rgb(43 58 140)", "rgb(31 95 74)", "rgb(201 148 24)", "rgb(22 20 15)"],
  grid: "rgb(22 20 15 / 0.08)",
};
