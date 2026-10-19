# client-kit/site-generator

Client website template. One `client.json` in, one static site out. It is **not** the HMHQ marketing site (`tools/build.py`) and shares no output with it. `client-kit/` is in `.vercelignore`, so the HMHQ Vercel project never deploys any of this.

```
python3 client-kit/site-generator/generate.py client-kit/site-generator/clients/practice-hvac-co/client.json
# -> client-kit/sites/practice-hvac-co/   (--out DIR, --assets DIR for images; default assets/ next to client.json)
client-kit/scripts/deploy-preview.sh client-kit/sites/practice-hvac-co practice-hvac-co-test
```

Output: home, services, service areas, one page per city **that has facts**, contact (form), privacy + terms (**DRAFT – needs lawyer review**), 404, `styles.css`, `site.js` (UTM capture, JSON form post, GA4 key events if GA4 is on), `ga.js` (only with GA4), `img/`, `robots.txt`, `vercel.json` (security headers, CSP built from what's enabled, X-Robots-Tag while NOINDEX) and `api/form-lead.js` copied from `client-kit/form-lead`.

## client.json keys (everything optional is left out when empty)
| Key | Meaning |
| --- | --- |
| `slug`, `business_name`, `tagline`, `phone`, `street_address` (blank = service-area business), `city`, `state`, `accent_color` | Basics |
| `hours`, `license` | Footer on every page (TACLA license number is required in Texas) |
| `services[]` | `name`, `blurb`, `form_value` (one of the five GHL `service_needed` options) |
| `service_areas[]` | A town name, or `{ "name": "Hewitt", "facts": ["..."] }`. **A city page is built only when facts are given, and only from those facts, verbatim.** Facts come from the client's kickoff; never invent them |
| `logo` | `{ "src": "file.svg", "alt": "..." }` from `assets/`. Only the client's own logo |
| `photos[]` | `{ "src", "alt", "caption" }` from `assets/`. Only photos the client took or owns |
| `booking_url` | GHL calendar URL ("Book online" buttons) |
| `review_url` | "Leave us a Google review", straight to Google, shown to everyone, no gating. Non-test sites must use a Google host |
| `ga4_id` | `G-…`. Adds gtag + `ga.js` + CSP. Only once the Privacy page covers analytics |
| `call_tracking_script_url` | GHL number-pool script `src` (leadconnectorhq.com / msgsndr.com only) |
| `turnstile_site_key` | Cloudflare Turnstile widget on the form + CSP. Secret goes in Vercel env as `TURNSTILE_SECRET_KEY` |
| `CHAT_WIDGET_ID` | The client's GHL chat widget id. HMHQ's id is refused |
| `NOINDEX` | `true` until Logan approves go-live |
| `TEST_SITE` | Practice sites: red banner, forces NOINDEX, requires a 555-01xx phone |
| `FORM_ENDPOINT` | `/api/form-lead` |

## Guard rails (enforced by `test/site-generator.test.mjs`, part of `npm test`)
- Forms are email-only: no phone input, no SMS opt-in, no checkboxes. Honeypot `company_fax`.
- Copy lint covers all visible text plus alt/title text, including city facts and captions:
  - Blocked: reviews/testimonials/stars, `%` stats, guarantees/promises, "what if we miss", "best", ranking talk, review-gating words.
  - The single allowed review phrase is "Leave us a Google review".
  - Legal pages may mention texting and STOP.
- No `AggregateRating`/review markup in schema.
- The committed `client-kit/sites/practice-hvac-co/` must match a fresh generate.

## Still open
- Lawyer-reviewed legal text (the generated pages are drafts).
- A booking embed (only a link today).
- If GHL's call-tracking snippet is inline code rather than a `src`, the template needs a small change.

See `client-kit/docs/`.
