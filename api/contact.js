// Contact form handler (Vercel serverless function), the site's main text opt-in form for A2P 10DLC.
// Checks Turnstile, then emails the message and a consent record (what was checked, when, from which page) to the team.
// Env vars: RESEND_API_KEY, LEAD_TO, LEAD_FROM, TURNSTILE_SECRET (optional until set).

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
const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const safeJson = (s) => { try { return JSON.parse(s); } catch { return {}; } };

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }
  const origin = String(req.headers.origin || "");
  if (origin && !/^https:\/\/(www\.)?hvacmarketinghq\.com$|^https:\/\/[a-z0-9-]+\.vercel\.app$|^http:\/\/localhost(:\d+)?$/.test(origin)) {
    return res.status(403).json({ error: "Please use the form on hvacmarketinghq.com." });
  }
  if (!/application\/json/i.test(String(req.headers["content-type"] || ""))) return res.status(415).json({ error: "Please use the form on the site." });
  const ip = clean(req.headers["x-forwarded-for"] || "", 100).split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) return res.status(429).json({ error: "Too many requests. Please try again in a few minutes." });

  const body = typeof req.body === "string" ? safeJson(req.body) : req.body || {};
  if (body.company_fax) return res.status(200).json({ ok: true }); // honeypot: pretend success

  const msg = {
    first_name: clean(body.first_name, 80),
    email: clean(body.email, 120),
    phone: clean(body.phone, 30),
    business: clean(body.business, 120),
    message: String(body.message == null ? "" : body.message).trim().slice(0, 2000),
    sms_service: body.sms_service === "yes" ? "yes" : "no",
    sms_marketing: body.sms_marketing === "yes" ? "yes" : "no",
    page: clean(body.page, 120),
  };
  if (!msg.first_name) return res.status(400).json({ error: "Please add your first name." });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(msg.email)) return res.status(400).json({ error: "Please check your email address." });
  if (msg.phone && msg.phone.replace(/\D/g, "").length < 10) return res.status(400).json({ error: "Please check your phone number, or leave it blank." });
  if ((msg.sms_service === "yes" || msg.sms_marketing === "yes") && !msg.phone) return res.status(400).json({ error: "Add a mobile number so we can text you, or uncheck the text boxes." });
  if (!msg.message) return res.status(400).json({ error: "Please add a short message." });

  if (!process.env.RESEND_API_KEY || !process.env.LEAD_TO || !process.env.LEAD_FROM) {
    return res.status(503).json({ error: "The form is down for a moment. Email hello@hvacmarketinghq.com instead." });
  }
  const token = clean(body["cf-turnstile-response"], 2048);
  const verify = !process.env.TURNSTILE_SECRET ? { success: true } : await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ secret: process.env.TURNSTILE_SECRET || "", response: token, remoteip: ip }),
  }).then((r) => r.json()).catch(() => ({ success: false }));
  if (!verify.success) return res.status(400).json({ error: "We couldn't verify you're human. Please try again." });

  // Consent record: keep this email. It shows what the person agreed to, when, and where.
  const record = { ...msg, received: new Date().toISOString(), ip };
  const rows = Object.entries(record).map(([k, v]) => `<tr><td><b>${k}</b></td><td>${escapeHtml(v)}</td></tr>`).join("");
  const sent = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: process.env.LEAD_FROM,
      to: [process.env.LEAD_TO],
      reply_to: msg.email,
      subject: `Contact form: ${msg.first_name}${msg.business ? ` (${msg.business})` : ""}`,
      html: `<table cellpadding="6">${rows}</table>`,
    }),
  }).catch(() => null);
  if (!sent || !sent.ok) {
    console.error("contact email failed", sent ? `Resend ${sent.status}: ${(await sent.text().catch(() => "")).slice(0, 300)}` : "network error");
    return res.status(502).json({ error: "Something went wrong on our end. Please try again." });
  }
  return res.status(200).json({ ok: true });
};
