import Link from "next/link";
import { CONTACT, CONTACT_LINKS } from "@/lib/contact";

const rows: [string, string, string, string][] = [
  ["Requests / hour", "100", "5,000", "Unlimited"],
  ["Historical data", "2000 – present", "1960 – present", "1960 – present"],
  ["Indicators", "All 87", "All 87 + forecasts", "All + custom feeds"],
  ["Compare countries", "Up to 5", "Up to 54", "Up to 54"],
  ["GraphQL", "Yes", "Yes", "Yes"],
  ["CSV export", "—", "Yes", "Yes"],
  ["Webhooks", "—", "Yes", "Yes"],
  ["SLA", "None", "99.9%", "99.99%"],
  ["Support", "Community", "Email", "Dedicated"],
];

const tiers = [
  { name: "Free", price: "$0", note: "forever", blurb: "For students, journalists and side projects.", cta: { label: "Get started", href: "/dashboard" }, featured: false },
  { name: "Pro", price: "$29", note: "per month", blurb: "For fintechs, research desks and production apps.", cta: { label: "Contact support about Pro", href: "/contact?topic=pro" }, featured: true },
  { name: "Enterprise", price: "Custom", note: "annual", blurb: "Custom feeds, SLAs and a human on call.", cta: { label: "Contact support about Custom", href: "/contact?topic=custom" }, featured: false },
];

const channels = [
  { label: "Email", value: CONTACT.email, href: CONTACT_LINKS.email("AfricaData API") },
  { label: "Telegram", value: `@${CONTACT.telegram}`, href: CONTACT_LINKS.telegram },
  { label: "WhatsApp", value: CONTACT.phoneDisplay, href: CONTACT_LINKS.whatsapp("Hi Kenean, I'm interested in the AfricaData API.") },
];

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-page px-6 py-12">
      <div className="border-b border-line pb-10">
        <p className="eyebrow">Pricing</p>
        <h1 className="display mt-3 max-w-3xl text-5xl md:text-7xl">
          Free for the curious. <span className="italic text-accent">Paid</span> for the serious.
        </h1>
        <p className="mt-6 max-w-xl text-ink/75">Paid tiers fund the servers and the weekly reconciliation of four upstream feeds. The free tier stays free.</p>
      </div>

      <div className="mt-12 grid gap-px bg-line md:grid-cols-3">
        {tiers.map((t) => (
          <div key={t.name} className={`flex flex-col p-8 md:p-10 ${t.featured ? "bg-ink text-paper" : "bg-surface"}`}>
            <p className={`font-mono text-[11px] uppercase tracking-eyebrow ${t.featured ? "text-paper/60" : "text-muted"}`}>{t.name}</p>
            <p className="num mt-6 text-6xl">
              {t.price} <span className={`font-sans text-sm ${t.featured ? "text-paper/60" : "text-muted"}`}>{t.note}</span>
            </p>
            <p className={`mt-4 text-sm ${t.featured ? "text-paper/75" : "text-muted"}`}>{t.blurb}</p>
            <div className="flex-1" />
            <Link
              href={t.cta.href}
              className={`mt-10 ${t.featured ? "btn bg-paper text-ink hover:bg-accent hover:text-white" : "btn-outline"}`}
            >
              {t.cta.label} <span className="arrow">→</span>
            </Link>
          </div>
        ))}
      </div>

      <div className="mt-16 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-left">
              <th className="eyebrow py-3 pr-4 font-normal">Feature</th>
              <th className="eyebrow py-3 pr-4 font-normal">Free</th>
              <th className="eyebrow py-3 pr-4 font-normal !text-accent">Pro</th>
              <th className="eyebrow py-3 font-normal">Enterprise</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {rows.map(([f, a, b, c]) => (
              <tr key={f}>
                <td className="py-4 pr-4 font-medium">{f}</td>
                <td className="py-4 pr-4 text-muted">{a}</td>
                <td className="py-4 pr-4">{b}</td>
                <td className="py-4 text-muted">{c}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section className="mt-20 border-t border-line pt-12">
        <p className="eyebrow">Get in touch</p>
        <h2 className="display mt-3 text-3xl md:text-4xl">
          <Link href="/contact" className="italic text-accent underline underline-offset-4">Talk with support</Link>
        </h2>
        <div className="mt-8 grid gap-px bg-line sm:grid-cols-3">
          {channels.map((c) => (
            <a
              key={c.label}
              href={c.href}
              target={c.href.startsWith("http") ? "_blank" : undefined}
              rel={c.href.startsWith("http") ? "noopener noreferrer" : undefined}
              className="group flex flex-col bg-surface p-6 transition hover:bg-ink hover:text-paper"
            >
              <span className="font-mono text-[11px] uppercase tracking-eyebrow text-muted group-hover:text-paper/60">{c.label}</span>
              <span className="mt-3 break-all text-base font-medium">{c.value}</span>
              <span className="mt-4 text-sm text-muted group-hover:text-paper/75">Open <span className="arrow">→</span></span>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
