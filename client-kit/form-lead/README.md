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
| `company_fax` | Honeypot. Hide it with CSS and leave it empty. If it's filled in, the function returns `{ ok: true }` and sends nothing. |

There is **no phone field**. If a phone number is sent anyway it is ignored and never forwarded, so don't add a phone input.

Steps, all on GHL API v2 (`https://services.leadconnectorhq.com`, `Version: 2021-07-28`, Bearer token):

1. `POST /contacts/upsert` with `locationId`, first and last name, email, city and postal code, `source: "Website Form"`, and custom fields by ID: lead source = `Website Form`, service = the mapped option. No tags here, because upsert replaces a contact's tags.
2. `POST /contacts/{id}/tags` with `["lead-web-form"]`. This adds the tag and keeps the existing ones.
3. `POST /contacts/{id}/notes` with the message, if there is one.
4. `GET /opportunities/search?location_id=…&pipeline_id=…&contact_id=…&status=open`. If the contact has no open opportunity in that pipeline, `POST /opportunities/` creates one at `GHL_STAGE_ID`, named `<name> – <service>`, with status `open`.

It never sets any SMS consent field (`sms_consent`), any DND field, or any consent or SMS tag. A test fails if any outgoing request carries `sms_consent` or `sms-consent`. UTM fields aren't sent yet (see the `TODO(utm)` in the handler).

Responses: `{ ok: true, steps }` once the contact is saved. Steps after that (tag, note, opportunity) are logged when they fail, but the visitor still sees success because the lead is already in GHL. If something goes wrong before the contact is saved, the visitor gets `{ ok: false, error }` with a friendly generic message (502/503). Bad input gets a 400 with a short hint. Logs show only step names and HTTP statuses, never the token or the visitor's details.

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

   The service field's options must be spelled exactly `Repair`, `Tune-Up/Maintenance`, `New System Estimate`, `Indoor Air Quality` and `Other`.
3. **Env.** Copy `.env.example` into Vercel (Production and Preview) with the real values, and set `ALLOWED_ORIGINS` to the client's site origins, e.g. `https://www.client.com,https://client.com`.
4. **Deploy.** Copy `api/form-lead.js` into the client site's `api/` folder (on Vercel it serves at `/api/form-lead`). Point the form at it and add the hidden `company_fax` input.
5. **Test.** Submit a test lead and check that the contact, tag, note and opportunity show up, and that the Vercel function logs show `"ok":true` for every step.

## Tests

`node --test client-kit/form-lead/test/` from the repo root (it also runs as part of `npm test`). `fetch` is stubbed, so the tests make no GHL calls.
