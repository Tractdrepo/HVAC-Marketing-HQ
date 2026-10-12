// Report card request handler (Vercel serverless function).
// Verifies Turnstile, checks the fields, then emails the lead to the team through Resend.
// Env vars: TURNSTILE_SECRET, RESEND_API_KEY, LEAD_TO (e.g. reports@yourdomain), LEAD_FROM (verified sender).

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

const clean = (v, max = 200) => String(v == null ? "" : v).replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
const escapeHtml = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }
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
    sms_consent: body.sms_consent === "yes" ? "yes" : "no",
    trade: clean(body.trade, 40),
    page: clean(body.page, 120),
  };
  if (!lead.website || !lead.business || !lead.first_name) return res.status(400).json({ error: "Please fill in every step." });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(lead.email)) return res.status(400).json({ error: "Please check your email address." });
  if (lead.phone.replace(/\D/g, "").length < 10) return res.status(400).json({ error: "Please check your phone number." });

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

  const rows = Object.entries(lead).map(([k, v]) => `<tr><td><b>${k}</b></td><td>${escapeHtml(v)}</td></tr>`).join("");
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
  if (!sent || !sent.ok) return res.status(502).json({ error: "Something went wrong on our end. Please try again." });

  return res.status(200).json({ ok: true });
};

function safeJson(s) {
  try { return JSON.parse(s); } catch { return {}; }
}
