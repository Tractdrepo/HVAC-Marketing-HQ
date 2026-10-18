// Client website form → GoHighLevel (Vercel serverless function). Part of client-kit; NOT an HMHQ route.
// Copy this folder into a client's site repo so the handler lands at /api/form-lead.
// Takes name, email, town/zip, service and message (no phone), then in the client's GHL sub-account:
// upserts the contact by email, adds the lead-web-form tag, adds the message as a note, and opens an
// opportunity in the pipeline unless the contact already has an open one there.
// Env vars: GHL_TOKEN, GHL_LOCATION_ID, GHL_FIELD_LEAD_SOURCE, GHL_FIELD_SERVICE, GHL_PIPELINE_ID,
// GHL_STAGE_ID, ALLOWED_ORIGINS (comma separated). Optional: GHL_FIELD_UTM_SOURCE, GHL_FIELD_UTM_MEDIUM,
// GHL_FIELD_UTM_CAMPAIGN, GHL_FIELD_UTM_TERM, GHL_FIELD_UTM_CONTENT, GHL_FIELD_GCLID. See README.md and .env.example.

const GHL_BASE = "https://services.leadconnectorhq.com";
const GHL_VERSION = "2021-07-28";
const GHL_TIMEOUT_MS = 8000;
const TAG = "lead-web-form";
const LEAD_SOURCE = "Website Form";
const SERVICES = ["Repair", "Tune-Up/Maintenance", "New System Estimate", "Indoor Air Quality", "Other"];
const MAX_BODY_BYTES = 16 * 1024;
const LIMITS = { name: 100, email: 254, townZip: 100, service: 100, message: 2000 };
// Tracking hidden fields (UTMs and gclid) → custom field IDs from env. Sent only when the value is present and
// the env var is set. They go only into the upsert's customFields: never into the note, the logs or the response.
// gclid uses the "Google Click ID" custom field, NEVER the built-in top-level contact gclid: a live test
// (Oct 18, 2026) showed upsert echoes a top-level gclid but GET /contacts/{id} doesn't return it afterwards.
const TRACKING_FIELDS = { utm_source: "GHL_FIELD_UTM_SOURCE", utm_medium: "GHL_FIELD_UTM_MEDIUM", utm_campaign: "GHL_FIELD_UTM_CAMPAIGN", utm_term: "GHL_FIELD_UTM_TERM", utm_content: "GHL_FIELD_UTM_CONTENT", gclid: "GHL_FIELD_GCLID" };
const TRACKING_MAX = 250;
const HONEYPOT = "company_fax"; // hidden input real people leave empty
const GENERIC_ERROR = "Sorry, something went wrong sending your request. Please try again, or give us a call.";

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
const safeJson = (s) => { try { return JSON.parse(s); } catch { return null; } };
const isEmail = (s) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(s);
// Outcome-only logging: step names and HTTP statuses, never the token, email, name or message.
const log = (step, ok, extra = {}) => (ok ? console.log : console.error)("form-lead", JSON.stringify({ step, ok, ...extra }));

const allowedOrigins = () => String(process.env.ALLOWED_ORIGINS || "").split(",").map((o) => o.trim().replace(/\/+$/, "")).filter(Boolean);

// Map whatever the form sent onto exactly one of SERVICES; anything unknown is Other.
const norm = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
function mapService(raw) {
  const s = norm(raw);
  if (!s) return "Other";
  const exact = SERVICES.find((o) => norm(o) === s);
  if (exact) return exact;
  if (/\b(tune ?up|maintenance|maintain|check ?up|inspection|service plan|cleaning|clean)\b/.test(s)) return "Tune-Up/Maintenance";
  if (/\b(new system|new unit|estimate|quote|replace|replacement|install|installation)\b/.test(s)) return "New System Estimate";
  if (/\b(indoor air|air quality|iaq|purifier|humidifier|dehumidifier|uv light|air filter|air scrubber)\b/.test(s)) return "Indoor Air Quality";
  if (/\b(repair|fix|broken|not cooling|not heating|no heat|no cool|no ac|emergency|leak|leaking)\b/.test(s)) return "Repair";
  return "Other";
}

// One "town/zip" input: a ZIP goes to postalCode, the rest to city.
function splitTownZip(raw) {
  const m = raw.match(/\b(\d{5})(?:-\d{4})?\b/);
  const postalCode = m ? m[1] : "";
  const city = clean(raw.replace(/\b\d{5}(?:-\d{4})?\b/, "").replace(/[,\s]+$/, "").replace(/^[,\s]+/, ""), 60);
  return { city, postalCode };
}

function trackingFields(body, env) {
  return Object.entries(TRACKING_FIELDS)
    .map(([key, envName]) => ({ id: clean(env[envName], 100), field_value: clean(body[key], TRACKING_MAX) }))
    .filter((f) => f.id && f.field_value && !/consent/i.test(f.field_value)); // never let a tracking value carry consent
}

function splitName(name) {
  const parts = name.split(/\s+/).filter(Boolean);
  return { firstName: parts[0] || "", lastName: parts.slice(1).join(" ") };
}

function readBody(req) {
  const type = String(req.headers["content-type"] || "").toLowerCase();
  let body = req.body;
  if (Buffer.isBuffer(body)) body = body.toString("utf8");
  if (typeof body === "string") {
    if (body.length > MAX_BODY_BYTES) return { tooBig: true };
    if (type.includes("application/json")) return { body: safeJson(body) };
    return { body: Object.fromEntries(new URLSearchParams(body)) };
  }
  if (body && typeof body === "object" && JSON.stringify(body).length > MAX_BODY_BYTES) return { tooBig: true };
  return { body: body && typeof body === "object" ? body : null };
}

async function ghl(method, path, payload) {
  const r = await fetch(`${GHL_BASE}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${process.env.GHL_TOKEN}`,
      Version: GHL_VERSION,
      Accept: "application/json",
      ...(payload ? { "Content-Type": "application/json" } : {}),
    },
    body: payload ? JSON.stringify(payload) : undefined,
    signal: AbortSignal.timeout(GHL_TIMEOUT_MS),
  }).catch(() => null);
  if (!r) return { ok: false, status: 0, data: null };
  const data = await r.json().catch(() => null);
  return { ok: r.ok, status: r.status, data };
}

module.exports = async function handler(req, res) {
  // CORS: only the origins in ALLOWED_ORIGINS, checked before anything else.
  const origin = String(req.headers.origin || "").replace(/\/+$/, "");
  if (!origin || !allowedOrigins().includes(origin)) {
    log("origin", false);
    return res.status(403).json({ ok: false, error: "Please use the form on our website." });
  }
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Vary", "Origin");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Max-Age", "600");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST, OPTIONS");
    return res.status(405).json({ ok: false, error: "Method not allowed." });
  }

  const type = String(req.headers["content-type"] || "");
  if (!/application\/json|application\/x-www-form-urlencoded/i.test(type)) return res.status(415).json({ ok: false, error: "Please use the form on our website." });
  if (Number(req.headers["content-length"] || 0) > MAX_BODY_BYTES) return res.status(413).json({ ok: false, error: "That message is too long. Please shorten it and try again." });
  const { body, tooBig } = readBody(req);
  if (tooBig) return res.status(413).json({ ok: false, error: "That message is too long. Please shorten it and try again." });
  if (!body) return res.status(400).json({ ok: false, error: "Please use the form on our website." });

  const ip = clean(req.headers["x-forwarded-for"] || "", 100).split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) return res.status(429).json({ ok: false, error: "Too many requests. Please try again in a few minutes." });

  if (clean(body[HONEYPOT])) { log("honeypot", true); return res.status(200).json({ ok: true }); } // pretend success

  // Only these fields are read. A phone field, if anyone sends one, is never read or forwarded.
  const lead = {
    name: clean(body.name, LIMITS.name),
    email: clean(body.email, LIMITS.email).toLowerCase(),
    townZip: clean(body.town_zip ?? body.townZip ?? body.zip ?? body.town ?? body["town/zip"], LIMITS.townZip),
    service: mapService(clean(body.service, LIMITS.service)),
    message: String(body.message == null ? "" : body.message).trim().slice(0, LIMITS.message),
  };
  if (!lead.name) return res.status(400).json({ ok: false, error: "Please add your name." });
  if (!isEmail(lead.email)) return res.status(400).json({ ok: false, error: "Please check your email address." });

  const env = process.env;
  if (!env.GHL_TOKEN || !env.GHL_LOCATION_ID || !env.GHL_FIELD_LEAD_SOURCE || !env.GHL_FIELD_SERVICE || !env.GHL_PIPELINE_ID || !env.GHL_STAGE_ID) {
    log("config", false);
    return res.status(503).json({ ok: false, error: GENERIC_ERROR });
  }

  // 1. Upsert by email. No tags here (upsert replaces them) and no phone, consent, SMS or DND fields.
  const { city, postalCode } = splitTownZip(lead.townZip);
  const contact = {
    locationId: env.GHL_LOCATION_ID,
    ...splitName(lead.name),
    email: lead.email,
    ...(city ? { city } : {}),
    ...(postalCode ? { postalCode } : {}),
    source: LEAD_SOURCE,
    customFields: [
      { id: env.GHL_FIELD_LEAD_SOURCE, field_value: LEAD_SOURCE },
      { id: env.GHL_FIELD_SERVICE, field_value: lead.service },
      ...trackingFields(body, env),
    ],
  };
  const up = await ghl("POST", "/contacts/upsert", contact);
  const contactId = up.data && up.data.contact && up.data.contact.id;
  if (!up.ok || !contactId) {
    log("contact_upsert", false, { status: up.status });
    return res.status(502).json({ ok: false, error: GENERIC_ERROR });
  }
  log("contact_upsert", true, { status: up.status, isNew: Boolean(up.data.new) });
  const id = encodeURIComponent(contactId);
  const steps = { contact: "ok" };

  // 2. Tag through the add-tags call so existing tags stay. Always runs: client workflows trigger on lead-web-form.
  const tag = await ghl("POST", `/contacts/${id}/tags`, { tags: [TAG] });
  log("add_tag", tag.ok, { status: tag.status });
  steps.tag = tag.ok ? "ok" : "failed";

  // 3. The visitor's message as a contact note.
  if (lead.message) {
    const note = await ghl("POST", `/contacts/${id}/notes`, {
      body: `Website form message:\n\n${lead.message}\n\nService: ${lead.service}${lead.townZip ? `\nTown/ZIP: ${lead.townZip}` : ""}`,
    });
    log("add_note", note.ok, { status: note.status });
    steps.note = note.ok ? "ok" : "failed";
  }

  // 4. Opportunity: only when this contact has no open one in the pipeline.
  const q = new URLSearchParams({ location_id: env.GHL_LOCATION_ID, pipeline_id: env.GHL_PIPELINE_ID, contact_id: contactId, status: "open", limit: "20" });
  const found = await ghl("GET", `/opportunities/search?${q}`);
  if (!found.ok) {
    // Don't create blind: a failed search could mean a duplicate. The contact, tag and note are saved.
    log("opportunity_search", false, { status: found.status });
    steps.opportunity = "failed";
  } else {
    const open = ((found.data && found.data.opportunities) || []).filter((o) => o && o.status === "open" && o.pipelineId === env.GHL_PIPELINE_ID && (!o.contactId || o.contactId === contactId));
    log("opportunity_search", true, { status: found.status, open: open.length });
    if (open.length) {
      steps.opportunity = "existing";
    } else {
      const opp = await ghl("POST", "/opportunities/", {
        locationId: env.GHL_LOCATION_ID,
        pipelineId: env.GHL_PIPELINE_ID,
        pipelineStageId: env.GHL_STAGE_ID,
        contactId,
        name: `${lead.name} – ${lead.service}`,
        status: "open",
      });
      log("opportunity_create", opp.ok, { status: opp.status });
      steps.opportunity = opp.ok ? "created" : "failed";
    }
  }

  // The lead is in GHL once the upsert worked, so the visitor sees success; failed later steps are in the logs.
  return res.status(200).json({ ok: true, steps });
};

module.exports.mapService = mapService;
module.exports.SERVICES = SERVICES;
