# Cloudflare Turnstile for a client site (free)
*Mon Oct 19, 2026 (CDT).*

**Cost:** free. Cloudflare's plans page (https://developers.cloudflare.com/turnstile/plans/, updated Aug 14, 2026) says the Free plan has unlimited challenges, every widget type, up to **20 widgets per account** and **10 hostnames per widget**. Turnstile doesn't need any other Cloudflare service, and the client's DNS doesn't have to be on Cloudflare.
**Limit to plan for:** 20 widgets per account. Past about 20 clients, use a second free account (or one widget with several client hostnames, up to 10).

**Testing (no account needed):** Cloudflare's dummy keys (https://developers.cloudflare.com/turnstile/troubleshooting/testing/):
- Site key `1x00000000000000000000AA` always passes and `2x00000000000000000000AB` always fails.
- Secret `1x0000000000000000000000000000000AA` always passes, `2x0000000000000000000000000000000AA` always fails and `3x0000000000000000000000000000000AA` returns "token already spent".
- The practice site uses the always-pass site key.
- `node client-kit/form-lead/scripts/turnstile-dummy-check.mjs` checks the secrets against the real Cloudflare endpoint.

## Steps for Logan (about 5 minutes per client)
1. Go to https://dash.cloudflare.com and log in, or sign up for a free account. HMHQ's own site already uses Turnstile, so use the account that holds HMHQ's widget.
2. Open **Turnstile** in the dashboard (type "Turnstile" in the dashboard search if it isn't in the left menu), then click **Add widget**.
3. **Widget name:** the client's business name + "website".
4. **Hostnames:** add the client's domain, e.g. `acmeheating.com` and `www.acmeheating.com`. Don't add `vercel.app`; previews keep using the test keys.
5. **Widget mode:** Managed. **Pre-clearance:** No.
6. Click **Create**.
7. Copy the **Site key** (public) and send it to the Web Developer. It goes into the client's `client.json` as `turnstile_site_key`.
8. Copy the **Secret key** straight into the secret store, then into the client's Vercel project: Settings → Environment Variables → `TURNSTILE_SECRET_KEY` (Production). **Never** paste it in chat or email.
9. Tell the Web Developer it's done. They regenerate the site and run a form test.
