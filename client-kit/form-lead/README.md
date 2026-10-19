# client-kit/form-lead

A Vercel serverless function for **client** websites: it takes the site's lead form and puts the lead into that client's GoHighLevel sub-account. It is **not** part of the HVAC Marketing HQ site. This folder is in `.vercelignore`, so HMHQ never deploys it, and it is not wired into any site yet.

## What it does

`POST /api/form-lead`, JSON or form-encoded (`application/x-www-form-urlencoded`; a plain HTML form works). Multipart isn't accepted, so send `fetch` bodies as JSON or `URLSearchParams`.

| Field | Notes |
| --- | --- |
| `name` | Required, up to 100 characters. Split into first and last name. |
| `email` | Required and checked. The contact is upserted by this address. |
| `town_zip` | Optional, up to 100 characters (`town`, `zip` or `townZip` also work). A 5-digit ZIP goes to the contact's **Postal Code**; the rest goes to **City**. |
| `service` | Mapped to exactly one of `Repair`, `Tune-Up/Maintenance`, `New System Estimate`, `Indoor Air Quality`, `Other`. Anything unknown becomes `Other`. |
| `message` | Optional, up to 2,000 characters. Saved as a contact **note**. |
| `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` | Optional hidden fields, up to 250 characters each (see the snippet below). Each one goes into its UTM custom field only when the value is present and its `GHL_FIELD_UTM_*` env var is set. |
| `gclid` | Optional hidden field (up to 250 characters). Goes into the **Google Click ID** custom field only when the value is present and `GHL_FIELD_GCLID` is set. |
| `company_fax` | Honeypot. Hide it with CSS and leave it empty. If it's filled in, the function returns `{ ok: true }` and sends nothing. |

There is **no phone field**. If a phone number is sent anyway it is ignored and never forwarded, so don't add a phone input.

Steps, all on GHL API v2 (`https://services.leadconnectorhq.com`, `Version: 2021-07-28`, Bearer token):

1. `POST /contacts/upsert` with `locationId`, first and last name, email, city and postal code, `source: "Website Form"`, and custom fields by ID: lead source = `Website Form`, service = the mapped option, plus any UTMs and the gclid. No tags here, because upsert replaces a contact's tags.
2. `POST /contacts/{id}/tags` with `["lead-web-form"]`, **every time**, right after the upsert. This adds the tag and keeps the existing ones. Client workflows trigger on this tag, and a test enforces it.
3. `POST /contacts/{id}/notes` with the message, if there is one.
4. `GET /opportunities/search?location_id=…&pipeline_id=…&contact_id=…&status=open`. If the contact has no open opportunity in that pipeline, `POST /opportunities/` creates one at `GHL_STAGE_ID`, named `<name> – <service>`, with status `open`.

It never sets either SMS consent field in the template (`contact.sms_consent` or `contact.sms_marketing_consent`; both must stay empty for form leads), any DND field, or any consent or SMS tag. A test fails if any outgoing request carries `sms_consent` or `sms-consent`.

**gclid goes into a custom field, not GHL's built-in one.** On Oct 18, 2026 we tested against the HMHQ sub-account. `POST /contacts/upsert` with the built-in top-level `gclid` returned 201 and echoed it, but `GET /contacts/{id}` and contact search didn't return it afterwards, and `attributionSource.gclid` was dropped too. The built-in field doesn't persist. So the handler puts the gclid only into the "Google Click ID" custom text field (`GHL_FIELD_GCLID`) and never sends a top-level `gclid`. UTMs and gclid go only into the upsert's custom fields: they're kept out of the note, the logs and the response.

### Capturing UTMs and gclid on the client page

Add hidden inputs to the form and fill them from the page URL:

```html
<input type="hidden" name="utm_source"><input type="hidden" name="utm_medium"><input type="hidden" name="utm_campaign">
<input type="hidden" name="utm_term"><input type="hidden" name="utm_content"><input type="hidden" name="gclid">
<script>
  (function () {
    var q = new URLSearchParams(location.search);
    ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"].forEach(function (k) {
      var v = q.get(k) || sessionStorage.getItem(k);
      if (q.get(k)) sessionStorage.setItem(k, v); // keep them if the visitor clicks to another page first
      document.querySelectorAll('input[name="' + k + '"]').forEach(function (el) { if (v) el.value = v; });
    });
  })();
</script>
```

Responses: `{ ok: true, steps }` once the contact is saved. If a later step (tag, note or opportunity) still fails after its retries, it's logged and alerted, but the visitor still sees success because the lead is already in GHL. If something goes wrong before the contact is saved, the visitor gets `{ ok: false, error }` with a friendly generic message (502/503), and an alert goes out. Bad input gets a 400 with a short hint. Logs show only step names, HTTP statuses and attempt counts, never the token or the visitor's details.

### Retries

GHL calls are retried on 429, 5xx and network errors or timeouts, about 3 attempts in all, with a 0.5 s then 1 s backoff. `Retry-After` (in seconds or as an HTTP date) is honored but capped at 3 s. All retry waits in one request share an 8 s budget, and each attempt times out after 5 s. Other 4xx responses are never retried.
- **Upsert by email:** idempotent, so it's retried freely.
- **Add tag:** adding the same tag twice is harmless.
- **Notes:** retried too. A 5xx or timeout that GHL actually processed could leave a duplicate note.
- **Opportunity create:** not idempotent. After a retryable failure, the function first re-searches the pipeline. If an open opportunity now exists, the create went through and nothing more is sent. If the re-search fails, it stops. It never creates a duplicate.

Worst case (GHL hanging on every call), a request takes about 35 s: once the 8 s budget is used up, remaining steps get a single attempt each. On the client project, set `"functions": { "api/form-lead.js": { "maxDuration": 60 } }` in `vercel.json` if its default limit is lower.

### Failure alerts

If `ALERT_WEBHOOK` is set (a Slack incoming webhook, or anything that accepts `{"text": "..."}`), one alert is POSTed per request whenever a step still fails after its retries. That includes the upsert, missing GHL env vars, and the tag, note, opportunity search and opportunity create steps. The alert contains:
- the site label (`SITE_LABEL`, falling back to `GHL_LOCATION_ID`)
- each failed step with its status code
- a timestamp
- the contact's name and email

It **never** contains the token, the message, town/ZIP, service, UTMs, gclid or GHL error bodies. Names are escaped so they can't trigger Slack mentions. The alert has a 3 s timeout, and any failure is caught and logged without the webhook URL, so it never breaks the request. If `ALERT_WEBHOOK` isn't set, no alert is sent.

Other guards: CORS only for origins in `ALLOWED_ORIGINS`, which must match exactly; anything else gets a 403, including requests with no `Origin`. Bodies are capped at 16 KB. There is also a best-effort rate limit of 5 posts per IP per 10 minutes on each server instance.

## Setup for a client

1. **Token.** In the client's GHL **sub-account**, go to Settings > Private Integrations and create a token with the scopes `contacts.write`, `contacts.readonly`, `opportunities.write` and `opportunities.readonly`. Use a sub-account Private Integration token, not an agency token. Store it **only** in the client's Vercel project env as `GHL_TOKEN`. Never put it in the repo, in front-end code or in chat. **Revoke it when the client offboards.**
2. **IDs.** Look up the location ID, the two custom field IDs, and the pipeline and stage IDs in **that client's** sub-account. They differ per client, even when the sub-account was built from our template snapshot. Example values from the template sub-account (for reference only; **not** defaults):

   | Env var | Template example |
   | --- | --- |
   | `GHL_FIELD_LEAD_SOURCE` (lead_source) | `O8DT4l1o1uzmGOZOBTGr` |
   | `GHL_FIELD_SERVICE` (service_needed) | `clbwxn9oeyklbcgVc52c` |
   | `GHL_PIPELINE_ID` (HVAC Jobs) | `9Jhg2OTnAG2hMMpNwCB8` |
   | `GHL_STAGE_ID` (New Lead) | `00f8a97d-fe6d-43ab-9567-7c5085202ad5` |
   | `GHL_FIELD_UTM_SOURCE` (utm_source) | `U5c2qIBfB9TfgVLzyFwx` |
   | `GHL_FIELD_UTM_MEDIUM` (utm_medium) | `wFM2FrQRYNzm0BcJ8YTh` |
   | `GHL_FIELD_UTM_CAMPAIGN` (utm_campaign) | `In40jdfCTpodq0Ln13th` |
   | `GHL_FIELD_UTM_TERM` (utm_term) | `bu2vsSSsTBEHZ0CFpXHM` |
   | `GHL_FIELD_UTM_CONTENT` (utm_content) | `ZWg5GLUdnO8JCnHqoRL4` |
   | `GHL_FIELD_GCLID` (Google Click ID, `contact.contactgoogle_click_id`) | `61gsANzfN6CcUf7hrYMa` |

   The UTM and gclid env vars are optional, and any that aren't set are skipped.

   The service field's options must be spelled exactly `Repair`, `Tune-Up/Maintenance`, `New System Estimate`, `Indoor Air Quality` and `Other`.
3. **Env.** Optionally create a Slack incoming webhook for the team's alerts channel and set it as `ALERT_WEBHOOK`, along with a readable `SITE_LABEL`. Copy `.env.example` into Vercel (Production and Preview) with the real values, and set `ALLOWED_ORIGINS` to the client's site origins, e.g. `https://www.client.com,https://client.com`.
4. **Deploy.** Copy `api/form-lead.js` into the client site's `api/` folder (on Vercel it serves at `/api/form-lead`). Point the form at it and add the hidden `company_fax` input.
5. **Test.** Submit a test lead and check that the contact, tag, note and opportunity show up, and that the Vercel function logs show `"ok":true` for every step.

## Tests

`node --test client-kit/form-lead/test/` from the repo root (it also runs as part of `npm test`). `fetch` is stubbed, so the tests make no GHL calls.

## Live check against GHL (`scripts/live-check.mjs`)

Runs the real handler in-process against a real sub-account, then reads GHL back and checks: contact exists by email, tag `lead-web-form`, lead_source = "Website Form", service_needed = the service sent, an open opportunity in `GHL_PIPELINE_ID` at `GHL_STAGE_ID`, no `sms-consent` tag, and BOTH consent fields empty: SMS Consent (`GHL_FIELD_SMS_CONSENT`) and SMS Marketing Consent (`GHL_FIELD_SMS_MARKETING_CONSENT`), both harness-only and optional (WARN when unset). `--twice` also checks dedupe. It sends `phone` and `sms_consent` in the payload on purpose, to prove they are dropped. Without `--live` it only reports which env vars are missing. Load env from a secret store (`op run ...` or `node --env-file=<file outside the repo>`); never paste the token on the command line. Delete the test contact afterwards with Logan's OK.

**Learned in the first live run (Oct 19, 2026, HVAC Client Template sub-account):**
- The form-lead token (contacts + opportunities only) **can't read custom fields** or conversations. All field ids (lead_source, service_needed, the 5 UTMs, Google Click ID, both consent fields) must come from the GHL handoff for each sub-account. The harness WARNs "NOT CHECKED" for messages when the token gets 401.
- GHL's **opportunity search lags** right after a create. A resubmit seconds later found 0 open deals, the create returned 400, and only GHL's own duplicate rejection kept it to one deal (the step is reported `failed`, which would raise an alert if `ALERT_WEBHOOK` is set). Still exactly one deal, but the function's search-first dedupe isn't the thing that held.
- GHL adds an **"Opportunity created" activity** to the contact's conversation (direction `outbound`, `TYPE_ACTIVITY_OPPORTUNITY`). It's a timeline entry, not a message; the harness ignores activity types.
