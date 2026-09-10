import assert from "node:assert/strict";
import { test } from "node:test";
import { createContactHandler } from "../lib/contact-handler";

const env = { SMTP_HOST: "smtp.example.com", SMTP_PORT: "587", SMTP_USER: "sender", SMTP_PASS: "test-only", SMTP_FROM: "sender@example.com" };
const inquiry = { name: "Ada", email: "ada@example.com", topic: "pro", message: "I'd like a Pro subscription.", website: "" };
const request = (body: unknown = inquiry, origin = "https://africadata.example") => new Request("https://africadata.example/contact/send", {
  method: "POST", headers: { origin, "Content-Type": "application/json" }, body: JSON.stringify(body),
});

test("sends each inquiry type to a fixed support address with visitor reply-to", async () => {
  for (const topic of ["pro", "custom", "support", "general"]) {
    let sent = false;
    const handler = createContactHandler(env, async (config, mail) => {
      assert.equal(config.SMTP_PORT, 587);
      assert.equal(mail.to, "Keneansufa@gmail.com");
      assert.equal(mail.from, "sender@example.com");
      assert.equal(mail.replyTo, inquiry.email);
      assert.match(mail.text, /Ada/);
      assert.ok(mail.subject.startsWith("[AfricaData]"));
      sent = true;
    });
    assert.equal((await handler(request({ ...inquiry, topic }))).status, 200);
    assert.equal(sent, true);
  }
});

test("rejects invalid input, spam, oversized bodies, and cross-origin requests without sending", async () => {
  const handler = createContactHandler(env, async () => assert.fail("Must not send"));
  for (const change of [{ email: "invalid" }, { name: "Ada\r\nBcc: victim@example.com" }, { message: "short" }, { topic: "invalid" }, { website: "spam" }, { to: "victim@example.com" }]) {
    assert.equal((await handler(request({ ...inquiry, ...change }))).status, 400);
  }
  assert.equal((await handler(request({ ...inquiry, message: "x".repeat(20_000) }))).status, 413);
  assert.equal((await handler(request(inquiry, "https://other.example"))).status, 403);
});

test("reports missing configuration and delivery failure without exposing secrets", async () => {
  assert.equal((await createContactHandler({})(request())).status, 503);
  const response = await createContactHandler(env, async () => { throw new Error("private SMTP credentials"); })(request());
  assert.equal(response.status, 502);
  assert.doesNotMatch(await response.text(), /credentials/);
});

test("throttles repeated send attempts and resets the window", async () => {
  let timestamp = 1;
  const handler = createContactHandler(env, async () => {}, () => timestamp);
  for (let attempt = 0; attempt < 3; attempt++) assert.equal((await handler(request())).status, 200);
  const limited = await handler(request());
  assert.equal(limited.status, 429);
  assert.ok(limited.headers.has("Retry-After"));
  timestamp += 3_600_000;
  assert.equal((await handler(request())).status, 200);
});

test("caps overall traffic even when sender addresses change", async () => {
  const handler = createContactHandler(env, async () => {});
  for (let attempt = 0; attempt < 30; attempt++) {
    assert.equal((await handler(request({ ...inquiry, email: `visitor${attempt}@example.com` }))).status, 200);
  }
  assert.equal((await handler(request())).status, 429);
});