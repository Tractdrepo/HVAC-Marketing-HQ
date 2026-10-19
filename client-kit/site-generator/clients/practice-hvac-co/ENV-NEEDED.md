# Practice HVAC Co (TEST): env vars for api/form-lead.js

Set these ONLY in the practice client's own Vercel project (Settings > Environment Variables, Preview + Production) or a secret manager. Never in chat, code, commits or this file. Status: **none set yet**, waiting on the GHL Specialist.

## Required by the function (it returns 503 if any are missing)
| Var | Comes from | Status |
| --- | --- | --- |
| `GHL_TOKEN` | Private Integration token in the **practice** sub-account (scopes contacts.write, contacts.readonly, opportunities.write, opportunities.readonly). Logan pastes it straight into the secret store | waiting |
| `GHL_LOCATION_ID` | Practice sub-account location id | waiting |
| `GHL_FIELD_LEAD_SOURCE` | Field id of `contact.lead_source` in that sub-account | waiting |
| `GHL_FIELD_SERVICE` | Field id of `contact.service_needed` | waiting |
| `GHL_PIPELINE_ID` | HVAC Jobs pipeline id in that sub-account | waiting |
| `GHL_STAGE_ID` | New Lead stage id in that pipeline | waiting |
| `ALLOWED_ORIGINS` | The practice preview origin(s), exact, comma-separated (known once a preview URL exists) | waiting on deploy |

## Optional (skipped when unset)
`GHL_FIELD_UTM_SOURCE`, `GHL_FIELD_UTM_MEDIUM`, `GHL_FIELD_UTM_CAMPAIGN`, `GHL_FIELD_UTM_TERM`, `GHL_FIELD_UTM_CONTENT`, `GHL_FIELD_GCLID`, `ALERT_WEBHOOK` (secret), `SITE_LABEL` (e.g. `Practice HVAC Co (TEST)`).

## Harness only (scripts/live-check.mjs; not used by the function)
`GHL_FIELD_SMS_CONSENT`: field id of `contact.sms_consent`, so the harness can prove it stays empty.

## Running the live check once the env exists
```
# from a secret store, e.g. 1Password CLI (no secrets on disk or in shell history):
op run --env-file=practice.op.env -- node client-kit/form-lead/scripts/live-check.mjs --live --twice --email <Logan's own email>
# or, after the Vercel project exists:  vercel env pull /tmp/practice.env  (chmod 600, delete after)
node --env-file=/tmp/practice.env client-kit/form-lead/scripts/live-check.mjs --live --twice --email <Logan's own email>
```
