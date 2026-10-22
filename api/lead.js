// Report card request handler (Vercel serverless function).
// Verifies Turnstile, checks the fields, then emails the lead to the team through Resend.
// Env vars: TURNSTILE_SECRET (needed for automatic reports), RESEND_API_KEY, LEAD_TO (e.g. reports@yourdomain), LEAD_FROM (verified sender).
// Automatic report card (grader/): REPORT_CARD_AUTO=on, GOOGLE_PLACES_API_KEY, ANTHROPIC_API_KEY,
// PAGESPEED_API_KEY (optional), GRADER_MODEL (optional), ANTHROPIC_WORKSPACE_ID (optional),
// REPORT_FROM (optional), REPORT_TEST_EMAILS (optional), UPSTASH_REDIS_REST_URL/_TOKEN (optional, shared caps).

const hits = new Map(); // best-effort per-instance rate limit
const LIMIT = 5;
const WINDOW_MS = 10 * 60 * 1000;

function rateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  list.push(now);
  hits.set(ip, list);
  return list.length > LIMIT;
}

// Caps on automatic reports (the Zero Vacancy rules): one per email a day, one per website a day,
// 20 an hour in all. Shared across servers when Upstash Redis is connected in Vercel; otherwise each
// server copy counts on its own.
const counts = new Map();
const REDIS_URL = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const REDIS_TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
async function bump(key, ttlSec) {
  if (REDIS_URL && REDIS_TOKEN) {
    try {
      const r = await fetch(`${REDIS_URL}/pipeline`, {
        method: "POST",
        headers: { Authorization: `Bearer ${REDIS_TOKEN}`, "Content-Type": "application/json" },
        body: JSON.stringify([["INCR", key], ["EXPIRE", key, String(ttlSec), "NX"]]),
        signal: AbortSignal.timeout(3000),
      });
      if (r.ok) return Number((await r.json())[0].result);
    } catch { /* fall back to this server's own count */ }
  }
  const now = Date.now();
  const c = counts.get(key);
  const next = c && c.until > now ? { n: c.n + 1, until: c.until } : { n: 1, until: now + ttlSec * 1000 };
  counts.set(key, next);
  return next.n;
}
// Addresses in REPORT_TEST_EMAILS (comma separated) skip the daily caps, for testing.
const testers = () => (process.env.REPORT_TEST_EMAILS || "").toLowerCase().split(",").map((x) => x.trim()).filter(Boolean);
async function autoBlocked(lead) {
  if (testers().includes(lead.email.toLowerCase())) return (await bump(`rc:hour:${Math.floor(Date.now() / 3600000)}`, 3600)) > 20 ? "over 20 reports this hour" : null;
  const site = lead.website.toLowerCase().replace(/^https?:\/\//, "").replace(/^www\./, "").replace(/\/.*$/, "");
  const [e, w, h] = await Promise.all([
    bump(`rc:email:${lead.email.toLowerCase()}`, 86400),
    bump(`rc:site:${site}`, 86400),
    bump(`rc:hour:${Math.floor(Date.now() / 3600000)}`, 3600),
  ]);
  if (e > 1) return "this email already got a report today";
  if (w > 1) return "this website was already graded today";
  if (h > 20) return "over 20 reports this hour";
  return null;
}

const BOOKING_URL = "https://calendar.app.google/dr7ELTg8SP7y8Z5q7";
const SITE_URL = "https://www.hvacmarketinghq.com";
const GRADE_MS = 48000; // the function's limit is 60s (vercel.json)

const clean = (v, max = 200) => String(v == null ? "" : v).replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }
  // Only our own pages may post here, and only as JSON (blocks other sites and plain HTML forms).
  const origin = String(req.headers.origin || "");
  if (origin && !/^https:\/\/(www\.)?hvacmarketinghq\.com$|^https:\/\/[a-z0-9-]+\.vercel\.app$|^http:\/\/localhost(:\d+)?$/.test(origin)) {
    return res.status(403).json({ error: "Please use the form on hvacmarketinghq.com." });
  }
  if (!/application\/json/i.test(String(req.headers["content-type"] || ""))) return res.status(415).json({ error: "Please use the form on the site." });
  const ip = clean(req.headers["x-forwarded-for"] || "", 100).split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) return res.status(429).json({ error: "Too many requests. Please try again in a few minutes." });

  const body = typeof req.body === "string" ? safeJson(req.body) : req.body || {};
  if (body.company_fax) return res.status(200).json({ ok: true }); // honeypot: pretend success

  const lead = {
    website: clean(body.website),
    business: clean(body.business),
    town: clean(body.town, 80),
    first_name: clean(body.first_name, 80),
    email: clean(body.email, 120),
    phone: clean(body.phone, 30),
    sms_service: body.sms_service === "yes" || body.sms_consent === "yes" ? "yes" : "no",
    sms_marketing: body.sms_marketing === "yes" ? "yes" : "no",
    trade: clean(body.trade, 40),
    page: clean(body.page, 120),
  };
  if (!lead.website || !lead.business || !lead.first_name) return res.status(400).json({ error: "Please fill in every step." });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(lead.email)) return res.status(400).json({ error: "Please check your email address." });
  if (lead.phone && lead.phone.replace(/\D/g, "").length < 10) return res.status(400).json({ error: "Please check your phone number, or leave it blank." });
  if ((lead.sms_service === "yes" || lead.sms_marketing === "yes") && !lead.phone) return res.status(400).json({ error: "Add a mobile number so we can text you, or uncheck the text boxes." });

  if (!process.env.RESEND_API_KEY || !process.env.LEAD_TO || !process.env.LEAD_FROM) {
    return res.status(503).json({ error: "Report cards open in a few days. Email hello@hvacmarketinghq.com and we'll send yours." });
  }

  // Turnstile is checked once its secret is set; until then the honeypot and rate limit apply.
  const token = clean(body["cf-turnstile-response"], 2048);
  const verify = !process.env.TURNSTILE_SECRET ? { success: true } : await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ secret: process.env.TURNSTILE_SECRET || "", response: token, remoteip: ip }),
  }).then((r) => r.json()).catch(() => ({ success: false }));
  if (!verify.success) return res.status(400).json({ error: "We couldn't verify you're human. Please try again." });

  // Automatic reports spend API money, so they need the human check (Turnstile) and the caps above.
  let auto = process.env.REPORT_CARD_AUTO === "on" && Boolean(process.env.GOOGLE_PLACES_API_KEY);
  let handWhy = auto ? null : "automatic report cards are off";
  if (auto && !process.env.TURNSTILE_SECRET) { auto = false; handWhy = "TURNSTILE_SECRET is not set in Vercel"; }
  if (auto) { handWhy = await autoBlocked(lead); if (handWhy) auto = false; }
  const rows = Object.entries({ ...lead, report_card: auto ? "grading automatically; a copy will follow" : `send by hand (${handWhy})` }).map(([k, v]) => `<tr><td><b>${k}</b></td><td>${escapeHtml(v)}</td></tr>`).join("");
  const sent = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: process.env.LEAD_FROM,
      to: [process.env.LEAD_TO],
      reply_to: lead.email,
      subject: `Report card request: ${lead.business} (${lead.trade || "trade"})`,
      html: `<table cellpadding="6">${rows}<tr><td><b>received</b></td><td>${new Date().toISOString()}</td></tr></table>`,
    }),
  }).catch(() => null);
  if (!sent || !sent.ok) {
    // Shows in Vercel > Logs, so a bad key or unverified domain is easy to spot.
    console.error("lead email failed", sent ? `Resend ${sent.status}: ${(await sent.text().catch(() => "")).slice(0, 300)}` : "network error");
    return res.status(502).json({ error: "Something went wrong on our end. Please try again." });
  }

  if (!auto && process.env.REPORT_CARD_AUTO === "on" && !/today/.test(handWhy || "")) await tellShop(lead);
  if (auto) {
    // Grade after answering, so the visitor isn't kept waiting.
    const job = autoReport(lead).catch((err) => console.error("auto report failed", err));
    let waitUntil;
    try { ({ waitUntil } = require("@vercel/functions")); } catch { waitUntil = null; }
    if (waitUntil) waitUntil(job); else await job;
  }
  return res.status(200).json({ ok: true });
};

function sendEmail(msg) {
  return fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: process.env.LEAD_FROM, ...msg }),
  }).then((r) => (r.ok ? r : Promise.reject(new Error(`Resend ${r.status}`))));
}

// The shop was told to expect an email, so when the automatic report can't go out they hear that a
// person will send it, instead of nothing.
async function tellShop(lead) {
  const { greetName } = await import("./_grader/report.mjs");
  const from = process.env.REPORT_FROM || `Logan at HVAC Marketing HQ <${(process.env.LEAD_FROM.match(/<([^>]+)>/) || [, process.env.LEAD_FROM])[1].trim()}>`;
  return sendEmail({
    from,
    to: [lead.email],
    reply_to: process.env.LEAD_TO,
    subject: `Your report card: ${lead.business}`,
    text: `Hi ${greetName(lead.first_name) || "there"},\n\nThanks for asking for a report card for ${lead.business}. Our automatic check couldn't finish this one, so I'll put it together myself and send it within one business day.\n\nIf you have a question in the meantime, just reply to this email.\n\nLogan\nHVAC Marketing HQ`,
  }).catch((err) => console.error("shop notice failed", err));
}

// Tell the team the automatic report didn't go out, so it can be sent by hand.
// debug (team only) is extra plain text appended after the ask, e.g. the Google candidates tried.
async function tellTeam(lead, why, { shop = true, debug = "" } = {}) {
  if (shop) await tellShop(lead);
  return sendEmail({
    to: [process.env.LEAD_TO],
    reply_to: lead.email,
    subject: `NEEDS YOU: report card for ${lead.business}`,
    text: `The automatic report card for ${lead.business} (${lead.website}) did not go out: ${why}.\nSend it by hand to ${lead.first_name} at ${lead.email}.${debug ? `\n\n${debug}` : ""}`,
  }).catch((err) => console.error("team notice failed", err));
}

async function autoReport(lead) {
  const { gradeWithDeadline, renderReport, isPublicSite, teamNote, holdReason, lookupDebugText } = await import("./_grader/report.mjs");
  const started = Date.now();
  if (!isPublicSite(lead.website)) return tellTeam(lead, "the website address isn't a public site");
  let result;
  try {
    result = await gradeWithDeadline({ website: lead.website, businessName: lead.business, town: lead.town, trade: "hvac" }, GRADE_MS);
  } catch (err) {
    return tellTeam(lead, `grading failed (${err.message})`);
  }
  // A partial run (a failed AI step, a Places error, or no Google profile for a shop that gave its name
  // and website) or an empty one is not sent: the shop hears a person will send it, the team gets why.
  const hold = holdReason(result);
  if (hold) {
    const graded = result.report.overall != null ? `\nWhat the automatic check got (not sent): ${result.report.grade} (${result.report.overall}), town used: ${[result.facts.town, result.facts.state].filter(Boolean).join(", ") || "none"}` : "";
    return tellTeam(lead, `${hold}${graded}`, { debug: lookupDebugText(result.facts) });
  }
  const r = renderReport(result, { firstName: lead.first_name, bookingUrl: `${SITE_URL}/book`, siteUrl: SITE_URL });
  try {
    // From a person, not a brand: REPORT_FROM if set, else "Logan at HVAC Marketing HQ" on the LEAD_FROM address.
    const addr = (process.env.LEAD_FROM.match(/<([^>]+)>/) || [, process.env.LEAD_FROM])[1].trim();
    const from = process.env.REPORT_FROM || `Logan at HVAC Marketing HQ <${addr}>`;
    await sendEmail({ from, to: [lead.email], reply_to: process.env.LEAD_TO, subject: r.subject, html: r.html, text: r.text });
  } catch (err) {
    return tellTeam(lead, `the email failed (${err.message})`, { shop: false });
  }
  // The team's copy: what ran and what didn't, then the report exactly as the shop got it.
  const note = teamNote(result, lead, Date.now() - started);
  await sendEmail({
    to: [process.env.LEAD_TO],
    reply_to: lead.email,
    subject: `Sent: ${r.subject.replace(/^Your report card: /, "")}`,
    text: `${note}\n\nResults page: ${r.link}\n\n${r.text}`,
    html: `<pre style="font:13px/1.5 monospace;white-space:pre-wrap;background:#f1f5f9;padding:12px;border-radius:8px">${escapeHtml(note)}</pre><p><a href="${escapeHtml(r.link)}">Open their results page</a></p>${r.html}`,
  }).catch((err) => console.error("team copy failed", err));
}

function safeJson(s) {
  try { return JSON.parse(s); } catch { return {}; }
}
