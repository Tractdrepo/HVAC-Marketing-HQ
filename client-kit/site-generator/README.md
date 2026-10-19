# client-kit/site-generator

Minimal static site generator for **client** websites. One `client.json` in, one static site out. It is **not** the HMHQ marketing site (`tools/build.py`) and shares no output with it. `client-kit/` is in `.vercelignore`, so the HMHQ Vercel project never deploys any of this.

```
python3 client-kit/site-generator/generate.py client-kit/site-generator/clients/practice-hvac-co/client.json
# -> client-kit/sites/practice-hvac-co/  (or --out DIR)
```

Output: `index`, `services`, `service-areas`, `contact`, `privacy`, `404` pages, `styles.css`, `site.js` (UTM capture + JSON form post), `robots.txt`, `vercel.json` (security headers, CSP, X-Robots-Tag while NOINDEX), and `api/form-lead.js` copied from `client-kit/form-lead`.

## client.json keys
| Key | Meaning |
| --- | --- |
| `slug` | Output folder name |
| `business_name`, `tagline`, `phone`, `street_address` (blank = service-area business), `city`, `state`, `license`, `hours`, `accent_color` | Shown on every page / in schema |
| `services[]` | `name`, `blurb`, `form_value` (one of the five GHL `service_needed` options) |
| `service_areas[]` | Towns listed on the site and in schema `areaServed` |
| `NOINDEX` | `true` until Logan approves go-live. Adds robots meta, X-Robots-Tag and `Disallow: /` |
| `TEST_SITE` | Practice sites: red "TEST SITE – not a real business" banner, forces NOINDEX, requires a 555-01xx phone |
| `CHAT_WIDGET_ID` | The client's GHL chat widget id. Empty = loader skipped and no GHL domains in CSP. HMHQ's id is refused |
| `FORM_ENDPOINT` | Where the lead form posts (`/api/form-lead`) |

## Guard rails (enforced by `test/site-generator.test.mjs`, part of `npm test`)
- Forms are email-only: no phone input, no SMS opt-in, no checkboxes. Honeypot `company_fax`.
- Copy lint fails the build on reviews/testimonials/stars, `%` stats, guarantees/promises, "what if we miss", "best", ranking talk.
- No `AggregateRating`/review markup in schema.
- The committed `client-kit/sites/practice-hvac-co/` must match a fresh generate.

## Not done yet (template gaps)
Turnstile on the form (form-lead has honeypot + rate limit only), GA4, call-tracking snippet, booking link/embed, real privacy/terms template, per-city pages, images/logo.
