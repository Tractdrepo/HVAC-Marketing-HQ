// Free download handler (Vercel serverless function).
// Emails the visitor a link to the PDF and tells the team. Env vars: RESEND_API_KEY, LEAD_TO, LEAD_FROM.
// Until email is set up, it answers 503 with the direct link, so nobody leaves empty-handed.

const MAGNETS = {
  scorecard: { title: "The 40-point HVAC online scorecard", file: "/downloads/hvac-online-scorecard.pdf" },
};
const SITE_URL = "https://hvacmarketinghq.com";
const hits = new Map();
const clean = (v, max = 200) => String(v == null ? "" : v).replace(/[\r\n\t]+/g, " ").trim().slice(0, max);
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function rateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < 10 * 60 * 1000);
  list.push(now);
  hits.set(ip, list);
  return list.length > 5;
}

function send(msg) {
  return fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: process.env.LEAD_FROM, ...msg }),
  });
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ error: "Method not allowed." }); }
  const origin = String(req.headers.origin || "");
  if (origin && !/^https:\/\/(www\.)?hvacmarketinghq\.com$|^https:\/\/[a-z0-9-]+\.vercel\.app$|^http:\/\/localhost(:\d+)?$/.test(origin)) {
    return res.status(403).json({ error: "Please use the form on hvacmarketinghq.com." });
  }
  if (!/application\/json/i.test(String(req.headers["content-type"] || ""))) return res.status(415).json({ error: "Please use the form on the site." });
  const ip = clean(req.headers["x-forwarded-for"] || "", 100).split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) return res.status(429).json({ error: "Too many requests. Please try again in a few minutes." });

  let body = req.body || {};
  if (typeof body === "string") { try { body = JSON.parse(body); } catch { body = {}; } }
  if (body.company_fax) return res.status(200).json({ ok: true }); // honeypot
  const m = MAGNETS[clean(body.magnet, 40)];
  if (!m) return res.status(400).json({ error: "Unknown download." });
  const lead = { first_name: clean(body.first_name, 80), email: clean(body.email, 120), page: clean(body.page, 120) };
  if (!lead.first_name) return res.status(400).json({ error: "Please add your first name." });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(lead.email)) return res.status(400).json({ error: "Please check your email address." });

  const link = SITE_URL + m.file;
  if (!process.env.RESEND_API_KEY || !process.env.LEAD_TO || !process.env.LEAD_FROM) {
    return res.status(503).json({ error: "Email delivery isn't switched on yet. Here's your download.", link: m.file });
  }
  const addr = (process.env.LEAD_FROM.match(/<([^>]+)>/) || [, process.env.LEAD_FROM])[1].trim();
  const toShop = await send({
    from: `Logan at HVAC Marketing HQ <${addr}>`,
    to: [lead.email],
    reply_to: process.env.LEAD_TO,
    subject: `Your copy: ${m.title}`,
    text: `Hi ${lead.first_name},\n\nHere's your copy of ${m.title}:\n${link}\n\nPrint it, go down the list on your phone, and add up your score. If you'd rather have it checked for you, the free report card grades your Google profile, reviews, website and listings against the shops near you: ${SITE_URL}/report-card\n\nLogan\nHVAC Marketing HQ`,
  }).catch(() => null);
  await send({
    to: [process.env.LEAD_TO],
    reply_to: lead.email,
    subject: `Download: ${m.title} (${lead.first_name})`,
    html: `<p><b>${esc(lead.first_name)}</b> &lt;${esc(lead.email)}&gt; downloaded ${esc(m.title)} from ${esc(lead.page || "the site")}.</p>`,
  }).catch(() => null);
  if (!toShop || !toShop.ok) return res.status(502).json({ error: "We couldn't send the email. Here's your download.", link: m.file });
  return res.status(200).json({ ok: true, link: m.file });
};
