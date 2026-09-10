"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import ThemeToggle from "@/components/ThemeToggle";
import { getApiKey } from "@/lib/api";

const links = [
  { href: "/explorer", label: "Explorer" },
  { href: "/docs", label: "Docs" },
  { href: "/pricing", label: "Pricing" },
  { href: "/contact", label: "Support" },
];

export default function Nav() {
  const pathname = usePathname();
  const [hasKey, setHasKey] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const sync = () => setHasKey(Boolean(getApiKey()));
    sync();
    window.addEventListener("africadata:key-changed", sync);
    return () => window.removeEventListener("africadata:key-changed", sync);
  }, []);

  useEffect(() => setOpen(false), [pathname]);

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-page items-center justify-between px-6">
        <Link href="/" className="display text-xl leading-none">
          Africa<span className="italic text-accent">Data</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {links.map((l) => {
            const active = pathname?.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`relative font-mono text-[11px] uppercase tracking-eyebrow transition ${active ? "text-ink" : "text-muted hover:text-ink"}`}
              >
                {l.label}
                {active && <span className="absolute -bottom-[23px] left-0 h-px w-full bg-accent" />}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link href="/dashboard" className="btn-ink hidden !py-2 md:inline-flex">
            {hasKey ? "Dashboard" : "Get API key"} <span className="arrow">→</span>
          </Link>
          <button className="grid h-8 w-8 place-items-center md:hidden" aria-label="Menu" onClick={() => setOpen((o) => !o)}>
            <span className={`block h-px w-5 bg-ink transition ${open ? "translate-y-[1px] rotate-45" : "-translate-y-1"}`} />
            <span className={`block h-px w-5 bg-ink transition ${open ? "-translate-y-[1px] -rotate-45" : "translate-y-1"}`} />
          </button>
        </div>
      </div>
      {open && (
        <div className="border-t border-line bg-paper md:hidden">
          <div className="mx-auto flex max-w-page flex-col px-6 py-4">
            {[...links, { href: "/dashboard", label: hasKey ? "Dashboard" : "Get API key" }].map((l) => (
              <Link key={l.href} href={l.href} className="border-b border-line py-3 font-mono text-xs uppercase tracking-eyebrow last:border-0">
                {l.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
