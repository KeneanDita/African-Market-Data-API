import type { Metadata } from "next";
import { Fraunces, JetBrains_Mono, Manrope } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";
import { ThemeProvider } from "@/components/ThemeProvider";
import { CONTACT, CONTACT_LINKS, SOURCES } from "@/lib/contact";
import { themeInitScript } from "@/lib/theme";

const display = Fraunces({ subsets: ["latin"], style: ["normal", "italic"], variable: "--font-display", display: "swap" });
const sans = Manrope({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "African Market Data API — 54 economies, one API",
  description: "Structured economic, demographic and market data for all 54 African countries. REST + GraphQL. Free to start.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${display.variable} ${sans.variable} ${mono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="relative flex min-h-screen flex-col">
        <ThemeProvider>
          <div className="kente" aria-hidden />
          <Nav />
          <main className="relative z-10 flex-1">{children}</main>
          <footer className="relative z-10 mt-24 border-t border-line">
            <div className="mx-auto grid max-w-page gap-8 px-6 py-12 md:grid-cols-[2fr_1fr_1fr_1fr]">
              <div>
                <p className="display text-2xl">
                  Africa<span className="italic text-accent">Data</span>
                </p>
                <p className="mt-3 max-w-sm text-sm text-muted">
                  The Bloomberg terminal for the African continent — built in the open by{" "}
                  <a className="text-ink underline decoration-line underline-offset-4 hover:decoration-accent" href={CONTACT.website}>
                    {CONTACT.name}
                  </a>
                  .
                </p>
              </div>
              <div>
                <p className="eyebrow mb-3">Contact</p>
                <ul className="space-y-2 text-sm">
                  <li><a className="hover:text-accent" href={CONTACT_LINKS.email()}>{CONTACT.email}</a></li>
                  <li><a className="hover:text-accent" href={CONTACT_LINKS.telegram} target="_blank" rel="noopener noreferrer">Telegram @{CONTACT.telegram}</a></li>
                  <li><a className="hover:text-accent" href={CONTACT_LINKS.whatsapp()} target="_blank" rel="noopener noreferrer">WhatsApp {CONTACT.phoneDisplay}</a></li>
                </ul>
              </div>
              <div>
                <p className="eyebrow mb-3">Product</p>
                <ul className="space-y-2 text-sm">
                  <li><a className="hover:text-accent" href="/explorer">Explorer</a></li>
                  <li><a className="hover:text-accent" href="/docs">Documentation</a></li>
                  <li><a className="hover:text-accent" href="/pricing">Pricing</a></li>
                </ul>
              </div>
              <div>
                <p className="eyebrow mb-3">Sources</p>
                <ul className="space-y-2 text-sm text-muted">
                  {SOURCES.map((s) => (
                    <li key={s.name}>
                      <a className="hover:text-accent" href={s.href} target="_blank" rel="noopener noreferrer">{s.name} ↗</a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="border-t border-line">
              <div className="mx-auto flex max-w-page items-center justify-between px-6 py-4 font-mono text-[11px] uppercase tracking-wider text-muted">
                <span>© {new Date().getFullYear()} AfricaData · MIT</span>
                <a className="hover:text-ink" href={CONTACT.github}>GitHub ↗</a>
              </div>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
