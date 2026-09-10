import type { Metadata } from "next";
import { ArrowUpRight, Mail, MessageCircle } from "lucide-react";
import SupportForm from "@/components/SupportForm";
import { CONTACT, CONTACT_LINKS } from "@/lib/contact";

export const metadata: Metadata = { title: "Talk with support | AfricaData" };

export default function ContactPage({ searchParams }: { searchParams: { topic?: string | string[] } }) {
  const requested = typeof searchParams.topic === "string" ? searchParams.topic : "general";
  const topic = ["pro", "custom", "support", "general"].includes(requested) ? requested : "general";
  const channels = [
    { label: "Email", value: CONTACT.email, href: CONTACT_LINKS.email("AfricaData support"), icon: Mail },
    { label: "Telegram", value: `@${CONTACT.telegram}`, href: CONTACT_LINKS.telegram, icon: MessageCircle },
    { label: "WhatsApp", value: CONTACT.phoneDisplay, href: CONTACT_LINKS.whatsapp(), icon: MessageCircle },
  ];

  return (
    <div className="mx-auto max-w-page px-6 py-12">
      <header className="border-b border-line pb-10">
        <p className="eyebrow">Contact</p>
        <h1 className="display mt-3 text-4xl sm:text-5xl">Talk with <span className="italic text-accent">support</span></h1>
        <p className="mt-5 max-w-xl text-ink/75">Subscriptions, custom data, or a question about your account. Get in touch with Kenean.</p>
      </header>
      <div className="grid gap-12 py-12 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] lg:gap-20">
        <SupportForm key={topic} initialTopic={topic} />
        <aside className="min-w-0 border-t border-line pt-8 lg:border-l lg:border-t-0 lg:pl-10 lg:pt-0">
          <h2 className="eyebrow mb-5">Direct contact</h2>
          <ul className="divide-y divide-line">
            {channels.map(({ label, value, href, icon: Icon }) => (
              <li key={label}>
                <a href={href} className="group flex items-start gap-3 py-6 hover:text-accent" target={href.startsWith("https") ? "_blank" : undefined} rel={href.startsWith("https") ? "noopener noreferrer" : undefined}>
                  <Icon size={20} className="shrink-0" aria-hidden />
                  <span className="min-w-0 flex-1"><span className="eyebrow block">{label}</span><span className="mt-2 block break-words text-sm">{value}</span></span>
                  <ArrowUpRight size={16} className="shrink-0" aria-hidden />
                </a>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </div>
  );
}