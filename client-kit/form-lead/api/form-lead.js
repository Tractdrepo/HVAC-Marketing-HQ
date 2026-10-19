// Client website form → GoHighLevel (Vercel serverless function). Part of client-kit; NOT an HMHQ route.
// Copy this folder into a client's site repo so the handler lands at /api/form-lead.
// Takes name, email, town/zip, service and message (no phone), then in the client's GHL sub-account:
// upserts the contact by email, adds the lead-web-form tag, adds the message as a note, and opens an
// opportunity in the pipeline unless the contact already has an open one there.
// Env vars: GHL_TOKEN, GHL_LOCATION_ID, GHL_FIELD_LEAD_SOURCE, GHL_FIELD_SERVICE, GHL_PIPELINE_ID,
// GHL_STAGE_ID, ALLOWED_ORIGINS (comma separated). Optional: GHL_FIELD_UTM_SOURCE, GHL_FIELD_UTM_MEDIUM,
// GHL_FIELD_UTM_CAMPAIGN, GHL_FIELD_UTM_TERM, GHL_FIELD_UTM_CONTENT, GHL_FIELD_GCLID, ALERT_WEBHOOK, SITE_LABEL.
// See README.md and .env.example.

const GHL_BASE = "https://services.leadconnectorhq.com";
const GHL_VERSION = "2021-07-28";
const GHL_TIMEOUT_MS = 5000; // per attempt
// Retries: 429, 5xx and network errors/timeouts, about 3 attempts per call with a short backoff. Retry-After is
// honored but capped. All retry waits and retried attempts in one request share an 8 s budget, so the function
// stays well under Vercel's limit. Other 4xx answers are never retried.
const MAX_ATTEMPTS = 3;
const BACKOFF_MS = [500, 1000];
const RETRY_AFTER_MAX_MS = 3000;
const RETRY_BUDGET_MS = 8000;
const ALERT_TIMEOUT_MS = 3000;
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

// Swappable in tests (fake sleep and clock).
const deps = {
  sleep: (ms) => new Promise((r) => setTimeout(r, ms)),
  now: () => Date.now(),
};

const retryable = (status) => status === 0 || status === 429 || status >= 500;

function retryDelay(attempt, retryAfter) {
  const base = BACKOFF_MS[Math.min(attempt - 1, BACKOFF_MS.length - 1)];
  if (retryAfter == null || retryAfter === "") return base;
  const secs = Number(retryAfter);
  const ms = Number.isFinite(secs) ? secs * 1000 : Date.parse(retryAfter) - deps.now();
  if (!Number.isFinite(ms) || ms < 0) return base;
  return Math.min(Math.max(ms, base), RETRY_AFTER_MAX_MS);
}

// One request to GHL, never retried.
async function ghlOnce(method, path, payload) {
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
  if (!r) return { ok: false, status: 0, data: null, retryAfter: null };
  const data = await r.json().catch(() => null);
  const retryAfter = r.headers && typeof r.headers.get === "function" ? r.headers.get("retry-after") : null;
  return { ok: r.ok, status: r.status, data, retryAfter };
}

// Wait before the next attempt if the request's retry budget allows it. Returns false when it doesn't.
async function backoff(ctx, attempt, retryAfter) {
  const wait = retryDelay(attempt, retryAfter);
  if (deps.now() + wait > ctx.deadline) return false;
  await deps.sleep(wait);
  return true;
}

// A GHL call with retries on 429, 5xx and network errors. Only for calls that are safe to repeat.
async function ghl(ctx, method, path, payload) {
  let r;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    r = await ghlOnce(method, path, payload);
    r.attempts = attempt;
    if (r.ok || !retryable(r.status) || attempt === MAX_ATTEMPTS) return r;
    if (!(await backoff(ctx, attempt, r.retryAfter))) return r;
  }
  return r;
}

// Slack-compatible alert. Carries the site label, the failed steps with status codes, a timestamp, and the
// contact's name and email ONLY: no token, message, UTMs, gclid or error bodies. Never throws.
const slackEscape = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
async function sendAlert(failures, lead) {
  const url = String(process.env.ALERT_WEBHOOK || "").trim();
  if (!url || !failures.length) return;
  const label = clean(process.env.SITE_LABEL || process.env.GHL_LOCATION_ID || "unknown site", 120);
  const text = [
    `:warning: Website form lead step failed (${slackEscape(label)})`,
    ...failures.map((f) => `Step: ${f.step}, status ${f.status || "network error"}`),
    `Time: ${new Date(deps.now()).toISOString()}`,
    `Contact: ${slackEscape(lead.name || "(none)")} <mailto:${slackEscape(lead.email)}|${slackEscape(lead.email)}>`,
  ].join("\n");
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(ALERT_TIMEOUT_MS),
    });
    log("alert", r.ok, { status: r.status });
  } catch {
    log("alert", false, { status: 0 });
  }
}

const OPEN_IN_PIPELINE = (env, contactId) => (o) => o && o.status === "open" && o.pipelineId === env.GHL_PIPELINE_ID && (!o.contactId || o.contactId === contactId);
async function searchOpen(ctx, env, contactId) {
  const q = new URLSearchParams({ location_id: env.GHL_LOCATION_ID, pipeline_id: env.GHL_PIPELINE_ID, contact_id: contactId, status: "open", limit: "20" });
  const r = await ghl(ctx, "GET", `/opportunities/search?${q}`);
  const open = r.ok ? ((r.data && r.data.opportunities) || []).filter(OPEN_IN_PIPELINE(env, contactId)) : [];
  return { ok: r.ok, status: r.status, open };
}

// Create the opportunity. Creating isn't idempotent, so a failed create is retried only after a re-search shows
// it really didn't go through; if the re-search finds one (or can't tell), we stop. Never creates duplicates.
// GHL's error message for the logs, stripped of personal details: no email, no name (the opportunity name contains
// it), no phone-like digit runs, no ids. One line, capped. Never sent in alerts or responses.
const DUP_RECHECKS = 3; // searches after a 400 on create (GHL's opportunity search lags right after a create)
const DUP_RECHECK_MS = [500, 1000, 1500];
function ghlErrorMessage(data, lead) {
  let m = data && (data.message ?? data.error ?? data.msg);
  if (Array.isArray(m)) m = m.join("; ");
  m = String(m == null ? "" : m);
  m = m.replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+/g, "[email]");
  for (const part of [lead.name, ...String(lead.name || "").split(/\s+/)].filter((x) => x && x.length > 1)) {
    m = m.split(part).join("[name]");
    m = m.replace(new RegExp(part.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), "[name]");
  }
  m = m.replace(/\+?\d[\d\s().-]{6,}\d/g, "[number]").replace(/[A-Za-z0-9_-]{16,}/g, "[id]");
  return clean(m, 200);
}

// After a 400 on create: GHL can reject a duplicate (e.g. the sub-account disallows duplicate opportunities) while
// its search still can't see the first deal. Re-search a few times with short waits; an open deal means "existing".
async function recheckAfter400(ctx, env, contactId) {
  for (let i = 0; i < DUP_RECHECKS; i++) {
    const wait = DUP_RECHECK_MS[i] || DUP_RECHECK_MS[DUP_RECHECK_MS.length - 1];
    if (deps.now() + wait > ctx.deadline) break;
    await deps.sleep(wait);
    const again = await searchOpen(ctx, env, contactId);
    log("opportunity_recheck_400", again.ok, { status: again.status, open: again.open.length, attempt: i + 1 });
    if (again.ok && again.open.length) return true;
  }
  return false;
}

async function createOpportunity(ctx, env, contactId, lead) {
  const payload = {
    locationId: env.GHL_LOCATION_ID,
    pipelineId: env.GHL_PIPELINE_ID,
    pipelineStageId: env.GHL_STAGE_ID,
    contactId,
    name: `${lead.name} – ${lead.service}`,
    status: "open",
  };
  let r;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    r = await ghlOnce("POST", "/opportunities/", payload);
    if (r.ok) return { result: "created", status: r.status };
    if (r.status === 400) {
      log("opportunity_create", false, { status: 400, ghlMessage: ghlErrorMessage(r.data, lead) });
      // Reported as "existing" (no alert) only when a re-search really finds the open deal.
      if (await recheckAfter400(ctx, env, contactId)) return { result: "existing", status: 400 };
      return { result: "failed", status: 400, step: "opportunity_create" };
    }
    if (!retryable(r.status) || attempt === MAX_ATTEMPTS) break;
    if (!(await backoff(ctx, attempt, r.retryAfter))) break;
    const again = await searchOpen(ctx, env, contactId);
    log("opportunity_recheck", again.ok, { status: again.status, open: again.open.length });
    if (!again.ok) return { result: "failed", status: r.status, step: "opportunity_create" };
    if (again.open.length) return { result: "created", status: r.status }; // the failed-looking create went through
  }
  return { result: "failed", status: r.status, step: "opportunity_create" };
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
    await sendAlert([{ step: "config (missing GHL env vars)", status: 503 }], lead);
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
  const ctx = { deadline: deps.now() + RETRY_BUDGET_MS };
  const failures = [];
  const up = await ghl(ctx, "POST", "/contacts/upsert", contact); // upsert by email is idempotent, safe to retry
  const contactId = up.data && up.data.contact && up.data.contact.id;
  if (!up.ok || !contactId) {
    log("contact_upsert", false, { status: up.status, attempts: up.attempts });
    await sendAlert([{ step: "contact_upsert (lead NOT saved)", status: up.status }], lead);
    return res.status(502).json({ ok: false, error: GENERIC_ERROR });
  }
  log("contact_upsert", true, { status: up.status, attempts: up.attempts, isNew: Boolean(up.data.new) });
  const id = encodeURIComponent(contactId);
  const steps = { contact: "ok" };

  // 2. Tag through the add-tags call so existing tags stay. Always runs: client workflows trigger on lead-web-form.
  const tag = await ghl(ctx, "POST", `/contacts/${id}/tags`, { tags: [TAG] }); // adding a tag twice is harmless
  log("add_tag", tag.ok, { status: tag.status, attempts: tag.attempts });
  steps.tag = tag.ok ? "ok" : "failed";
  if (!tag.ok) failures.push({ step: "add_tag", status: tag.status });

  // 3. The visitor's message as a contact note.
  if (lead.message) {
    // A retry after a 5xx/timeout that GHL actually processed could leave a duplicate note; acceptable.
    const note = await ghl(ctx, "POST", `/contacts/${id}/notes`, {
      body: `Website form message:\n\n${lead.message}\n\nService: ${lead.service}${lead.townZip ? `\nTown/ZIP: ${lead.townZip}` : ""}`,
    });
    log("add_note", note.ok, { status: note.status, attempts: note.attempts });
    steps.note = note.ok ? "ok" : "failed";
    if (!note.ok) failures.push({ step: "add_note", status: note.status });
  }

  // 4. Opportunity: only when this contact has no open one in the pipeline.
  const found = await searchOpen(ctx, env, contactId);
  if (!found.ok) {
    // Don't create blind: a failed search could mean a duplicate. The contact, tag and note are saved.
    log("opportunity_search", false, { status: found.status });
    steps.opportunity = "failed";
    failures.push({ step: "opportunity_search", status: found.status });
  } else {
    log("opportunity_search", true, { status: found.status, open: found.open.length });
    if (found.open.length) {
      steps.opportunity = "existing";
    } else {
      const opp = await createOpportunity(ctx, env, contactId, lead);
      log("opportunity_create", opp.result !== "failed", { status: opp.status, result: opp.result });
      steps.opportunity = opp.result;
      if (opp.result === "failed") failures.push({ step: opp.step, status: opp.status });
    }
  }

  await sendAlert(failures, lead);
  // The lead is in GHL once the upsert worked, so the visitor sees success; failed later steps are logged and alerted.
  return res.status(200).json({ ok: true, steps });
};

module.exports.mapService = mapService;
module.exports.ghlErrorMessage = ghlErrorMessage;
module.exports.SERVICES = SERVICES;
module.exports.deps = deps;
