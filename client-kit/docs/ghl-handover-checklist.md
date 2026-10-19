# GHL → Web Developer handover + client go-live checklist
*Mon Oct 19, 2026 (CDT). One copy per client. Short on purpose. Field ids differ per sub-account, even when it was installed from the snapshot.*

## A. GHL Specialist hands over (per client sub-account)
The form-lead token **can't read custom fields or conversations**, so every id below must be handed over. Get them by API or a read-only connector (`get-custom-fields`, model=contact).

1. **Location id** (sub-account) → `GHL_LOCATION_ID`
2. **Pipeline id**, HVAC Jobs → `GHL_PIPELINE_ID`
3. **Stage id**, New Lead → `GHL_STAGE_ID`
4. **Field id** `contact.lead_source` → `GHL_FIELD_LEAD_SOURCE` (option "Website Form" must exist)
5. **Field id** `contact.service_needed` → `GHL_FIELD_SERVICE` (options exactly: Repair, Tune-Up/Maintenance, New System Estimate, Indoor Air Quality, Other)
6. **Field ids** `contact.utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content` → `GHL_FIELD_UTM_SOURCE` … `GHL_FIELD_UTM_CONTENT`
7. **Field id** Google Click ID `contact.contactgoogle_click_id` → `GHL_FIELD_GCLID`
8. **Field id** `contact.sms_consent` → `GHL_FIELD_SMS_CONSENT` (test harness only; must stay **empty** for form leads)
9. **Field id** `contact.sms_marketing_consent` → `GHL_FIELD_SMS_MARKETING_CONSENT` (test harness only; must stay **empty** for form leads)
10. **Chat widget id** → `CHAT_WIDGET_ID` in client.json. It must be the client's widget, never HMHQ's `6ad452…`.
11. **Exact consent wording** of the widget's two unchecked boxes (transactional, promotional), naming the client's legal business name. Paste it into the client's Privacy page.
12. **Booking calendar URL** (GHL calendar) → `booking_url` in client.json
13. **Google review link** (one copy, same as the GHL custom value) → `review_url` in client.json
14. **Call-tracking script URL** (number pool "Normal Snippet" `src`), if the plan has it → `call_tracking_script_url`
15. **Duplicate-opportunity setting** for the sub-account (allowed or not). The form-lead dedupe relies on GHL rejecting duplicates when its search lags.
16. **Private Integration token** (scopes: contacts.write, contacts.readonly, opportunities.write, opportunities.readonly).
    - Logan creates it in the client's sub-account.
    - It goes **straight into the secret store, then into the client's Vercel project env** as `GHL_TOKEN`.
    - Never in chat, email, the repo, a file or the Control Room. Rotate it every 90 days and revoke it at offboarding.

## B. Web Developer sets (client's own Vercel project, Preview + Production env)
1. From the secret store, never pasted in chat: `GHL_TOKEN`, `TURNSTILE_SECRET_KEY`, `ALERT_WEBHOOK` (optional).
2. Ids from section A: `GHL_LOCATION_ID`, `GHL_PIPELINE_ID`, `GHL_STAGE_ID`, `GHL_FIELD_*`.
3. `ALLOWED_ORIGINS`: the exact origin(s) the form runs on, e.g. the preview origin now, the real `https://www.` + apex at launch.
4. `SITE_LABEL`, e.g. "Acme Heating (acme.com)".
5. Run `live-check.mjs --live --twice` with Logan's own email (env loaded from the secret store), then do C.

## C. Per-client "nothing was sent" check (after every live form test)
Read-only. Uses the HighLevel connector. The form-lead token can't read conversations, and that's by design.
1. Note the contact id the harness printed.
2. HighLevel connector → `search-conversation` with `contactId=<id>` on that location.
3. For each conversation: `get-messages` with its `conversationId`.
4. **PASS** only if every entry is a GHL activity (`messageType` starting `TYPE_ACTIVITY…`, e.g. "Opportunity created"). Any `TYPE_SMS`, `TYPE_EMAIL`, `TYPE_CALL` or other real outbound message = **FAIL**. Stop, and tell Logan and the GHL Specialist.
5. Write the conversation ids and the result in the client's run log. Add every record the test created (contact, opportunity, notes) to Logan's delete list. Delete nothing without his OK.

## D. Go-live checklist (🚦 Logan's approval is the gate; do these in order)
1. **Copy and design approved by the client** in writing. Copy check passes (generator lint + human read: no invented facts, stats, reviews, guarantees or "what if we miss").
2. **Privacy and Terms**: the lawyer-reviewed versions replace the generated "DRAFT – needs lawyer review" pages, and they name the client and the widget's consent wording.
3. **CSP**: regenerate with the final config (widget, Turnstile, GA4, call tracking). Open every page and the form, and check the browser console shows no blocked scripts.
4. **Turnstile**: real site key in client.json and `TURNSTILE_SECRET_KEY` in Production env. The test keys must be gone.
5. **ALLOWED_ORIGINS** = the final `https://www.<domain>` and `https://<domain>` only. Remove preview origins.
6. **Live form test** (B5 + C) passes on the final domain.
7. **Logan approves go-live.** Write down the date and time.
8. **NOINDEX flip**: set `NOINDEX: false` (and `TEST_SITE: false`) in client.json, then regenerate. robots meta, X-Robots-Tag and the `Disallow: /` robots.txt all go away together. Check it with a curl.
9. **Protection change**: Vercel Authentication stays ON. Standard Protection doesn't cover custom domains, so the custom domain is public and every `*.vercel.app` URL stays protected. Don't turn protection off.
10. **Domain**: add the client's domain to **their** project (never HMHQ's), set the DNS (dev doc Step 3), confirm SSL, and confirm http/https/apex/www all end at `https://www.`.
11. **Production deploy**: the first and only `--prod` happens after steps 1–10, by hand, with Logan's OK.
12. Submit the sitemap in Search Console. Write down the launch date (billing starts) and tell the GHL Specialist.
