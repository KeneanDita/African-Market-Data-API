"use client";

import { useRef, useState } from "react";
import { CheckCircle2, LoaderCircle, Send } from "lucide-react";

export default function SupportForm({ initialTopic }: { initialTopic: string }) {
  const submitting = useRef(false);
  const [state, setState] = useState<"idle" | "sending" | "success" | "error">("idle");
  const [feedback, setFeedback] = useState("");

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    const form = event.currentTarget;
    const fields = new FormData(form);
    submitting.current = true;
    setState("sending");
    setFeedback("");
    try {
      const response = await fetch("/contact/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.fromEntries(fields)),
        signal: AbortSignal.timeout(30_000),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "Your message could not be sent. Please try again.");
      setFeedback(result.message);
      setState("success");
      form.reset();
    } catch (error) {
      setState("error");
      setFeedback(error instanceof Error && error.name !== "TimeoutError" && error.name !== "TypeError"
        ? error.message
        : "We couldn't confirm delivery. Please try later or use the contact links. Your message is still here.");
    } finally {
      submitting.current = false;
    }
  }

  return (
    <form onSubmit={submit} className="min-w-0 space-y-8" aria-busy={state === "sending"}>
      <fieldset disabled={state === "sending"} className="min-w-0 space-y-8">
        <legend className="display mb-8 text-3xl">Send an inquiry</legend>
        <div className="grid gap-8 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="support-name">Name</label>
            <input className="field" id="support-name" name="name" autoComplete="name" required maxLength={100} />
          </div>
          <div>
            <label className="label" htmlFor="support-email">Email address</label>
            <input className="field" id="support-email" name="email" type="email" autoComplete="email" required maxLength={254} />
          </div>
        </div>
        <div>
          <label className="label" htmlFor="support-topic">Inquiry type</label>
          <select className="field" id="support-topic" name="topic" defaultValue={initialTopic} required>
            <option value="general">General question</option>
            <option value="pro">Pro subscription</option>
            <option value="custom">Custom subscription</option>
            <option value="support">Technical support</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="support-message">Message</label>
          <textarea className="field min-h-40 resize-y" id="support-message" name="message" required minLength={10} maxLength={5000} rows={6} />
        </div>
        <div hidden aria-hidden="true">
          <label htmlFor="support-website">Website</label>
          <input id="support-website" name="website" tabIndex={-1} autoComplete="off" />
        </div>
        <p className="text-xs text-muted">Your name, email, and message will be sent to support so we can reply to your inquiry. Do not include passwords or API keys.</p>
        <button type="submit" className="btn-ink justify-center">
          {state === "sending" ? <LoaderCircle size={16} className="animate-spin" aria-hidden /> : <Send size={16} aria-hidden />}
          {state === "sending" ? "Sending..." : "Send message"}
        </button>
      </fieldset>
      <div aria-live="polite" aria-atomic="true">
        {feedback && <p className={`flex items-start gap-2 border-l-2 py-2 pl-4 text-sm ${state === "success" ? "border-moss text-moss" : "border-accent text-accent"}`}>
          {state === "success" && <CheckCircle2 size={18} className="shrink-0" aria-hidden />}
          {feedback}
        </p>}
      </div>
    </form>
  );
}