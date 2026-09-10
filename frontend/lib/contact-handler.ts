import nodemailer from "nodemailer";
import { z } from "zod";
import { CONTACT } from "./contact";

const inquirySchema = z.object({
  name: z.string().trim().min(1).max(100).regex(/^[^\r\n]+$/),
  email: z.string().trim().email().max(254),
  topic: z.enum(["pro", "custom", "support", "general"]),
  message: z.string().trim().min(10).max(5000),
  website: z.string().max(0).optional(),
}).strict();

const smtpSchema = z.object({
  SMTP_HOST: z.string().min(1),
  SMTP_PORT: z.coerce.number().int().refine((port) => port === 465 || port === 587).default(587),
  SMTP_USER: z.string().min(1),
  SMTP_PASS: z.string().min(1),
  SMTP_FROM: z.string().email(),
});

const topics = { pro: "Pro subscription", custom: "Custom subscription", support: "Technical support", general: "General question" };
const maxBytes = 16_384;
const windowMs = 3_600_000;
type Mail = { from: string; to: string; replyTo: string; subject: string; text: string };
type Smtp = z.infer<typeof smtpSchema>;

async function sendMail(config: Smtp, mail: Mail) {
  const transport = nodemailer.createTransport({
    host: config.SMTP_HOST,
    port: config.SMTP_PORT,
    secure: config.SMTP_PORT === 465,
    requireTLS: config.SMTP_PORT === 587,
    auth: { user: config.SMTP_USER, pass: config.SMTP_PASS },
    connectionTimeout: 10_000,
    greetingTimeout: 10_000,
    socketTimeout: 15_000,
  });
  const result = await transport.sendMail(mail);
  if (!result.accepted?.length) throw new Error("Message not accepted");
}

export function createContactHandler(
  env: Record<string, string | undefined> = process.env,
  deliver: (config: Smtp, mail: Mail) => Promise<void> = sendMail,
  now: () => number = Date.now,
) {
  let resetAt = 0;
  let attempts = 0;
  const emailAttempts = new Map<string, number>();

  return async function handle(request: Request): Promise<Response> {
    const respond = (status: number, message: string, headers = {}) =>
      Response.json({ message }, { status, headers: { "Cache-Control": "no-store", ...headers } });
    if (request.headers.get("origin") !== new URL(request.url).origin) {
      return respond(403, "Please send your message from the contact page.");
    }
    if (!request.headers.get("content-type")?.startsWith("application/json")) {
      return respond(415, "A JSON message is required.");
    }
    const timestamp = now();
    if (timestamp >= resetAt) {
      resetAt = timestamp + windowMs;
      attempts = 0;
      emailAttempts.clear();
    }
    if (++attempts > 30) {
      return respond(429, "Too many inquiries. Please try later or contact us on Telegram or WhatsApp.", { "Retry-After": String(Math.ceil((resetAt - timestamp) / 1000)) });
    }
    const reader = request.body?.getReader();
    if (!reader) return respond(400, "Please complete all required fields.");
    let body = "";
    let size = 0;
    const decoder = new TextDecoder();
    let raw: unknown;
    try {
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        size += chunk.value.byteLength;
        if (size > maxBytes) {
          await reader.cancel();
          return respond(413, "Your message is too long.");
        }
        body += decoder.decode(chunk.value, { stream: true });
      }
      raw = JSON.parse(body + decoder.decode());
    } catch {
      return respond(400, "The message could not be read. Please try again.");
    } finally {
      reader.releaseLock();
    }
    const parsed = inquirySchema.safeParse(raw);
    if (!parsed.success) return respond(400, "Enter a valid name, email, inquiry type, and a message of 10 to 5,000 characters.");
    const inquiry = parsed.data;
    const email = inquiry.email.toLowerCase();
    const count = (emailAttempts.get(email) ?? 0) + 1;
    emailAttempts.set(email, count);
    if (count > 3) {
      return respond(429, "Please wait before sending another inquiry.", { "Retry-After": String(Math.ceil((resetAt - timestamp) / 1000)) });
    }
    const config = smtpSchema.safeParse(env);
    if (!config.success) {
      return respond(503, "The email form is not available yet. Please use email, Telegram, or WhatsApp below.");
    }
    try {
      await deliver(config.data, {
        from: config.data.SMTP_FROM,
        to: CONTACT.email,
        replyTo: inquiry.email,
        subject: `[AfricaData] ${topics[inquiry.topic]}`,
        text: `Name: ${inquiry.name}\nEmail: ${inquiry.email}\nInquiry: ${topics[inquiry.topic]}\n\n${inquiry.message}`,
      });
      return respond(200, "Your inquiry has been sent to support. We'll reply to your email.");
    } catch {
      return respond(502, "We couldn't send your message. Please try later or use the contact links below.");
    }
  };
}