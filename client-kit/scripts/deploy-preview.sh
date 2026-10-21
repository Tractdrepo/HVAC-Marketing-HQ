#!/usr/bin/env bash
# Deploy a client site folder as a PROTECTED Vercel PREVIEW, with no Git link, and verify nothing is public.
# Free (Hobby) features only. Never deploys --prod, never adds a domain, never touches other projects.
#
#   client-kit/scripts/deploy-preview.sh <site-dir> <project-name> [--scope <team-slug>] [--create]
#   e.g. client-kit/scripts/deploy-preview.sh client-kit/sites/practice-hvac-co practice-hvac-co-test
#
# Needs: the Vercel CLI logged in on this machine (npx vercel@latest whoami), python3, curl.
# Steps:
#  1. Look up the project (or create it with --create). Refuse if it has a Git repo connected or a custom domain.
#  2. Vercel Authentication must be ON before anything is deployed. A project this run just created gets Standard
#     Protection (free) turned on first; an existing project with protection off makes the script ABORT.
#  3. Deploy with `vercel deploy --target preview` (always an explicit preview target; never --prod, never no
#     target) using VERCEL_ORG_ID/VERCEL_PROJECT_ID (no `vercel link`, no .vercel folder, no Git auto-connect).
#     The deployment URL (https://<project>-<hash>-<team>.vercel.app) is parsed from the CLI's stdout, never the
#     production alias.
#  4. Check the deployment's target through the API, and that the production aliases (<project>.vercel.app and
#     <project>-<team>.vercel.app) answer 404 or 401 logged out. If the target is production or an alias answers
#     anything else (e.g. 200), the new deployment is removed at once and the script stops (no retry).
#  5. Logged-out curl of the preview URL must be 401 or a 302 to the Vercel login, else the deployment is removed
#     and the script stops. It also reports the project's production deployment count (should be 0 pre-launch).
# The CLI keeps its own token; this script never reads, prints or passes one.
set -euo pipefail

SCOPE="williamtaylor1204-2866s-projects"
CREATE=0
CREATED=0
POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    --create) CREATE=1; shift ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 2 ]] || { echo "usage: $0 <site-dir> <project-name> [--scope team] [--create]" >&2; exit 64; }
SITE_DIR="$(cd "${POS[0]}" && pwd)"
PROJECT="${POS[1]}"
[[ "$PROJECT" =~ ^[a-z0-9-]+$ ]] || { echo "project name must be lowercase letters, digits, dashes" >&2; exit 64; }
[[ -f "$SITE_DIR/vercel.json" && -f "$SITE_DIR/index.html" ]] || { echo "$SITE_DIR doesn't look like a generated site" >&2; exit 64; }
[[ "$PROJECT" != "hvac-marketing-hq" ]] || { echo "refusing to touch the HMHQ project" >&2; exit 64; }

VC=(npx --yes vercel@latest)
# vercel api exits non-zero on 404 (e.g. a project that does not exist yet); under set -e that killed --create.
api() { "${VC[@]}" api "$@" --scope "$SCOPE" --raw 2>/dev/null || true; }
jget() { python3 -c "import json,sys
try: d=json.load(sys.stdin)
except Exception: d={}
v=d
for k in sys.argv[1].split('.'):
    v=(v or {}).get(k) if isinstance(v,dict) else None
print('' if v is None else (json.dumps(v) if isinstance(v,(dict,list)) else v))" "$1"; }
log() { printf '[%s] %s\n' "$(date '+%H:%M:%S %Z')" "$*"; }

# Logged-out status of a URL: prints "CODE LOCATION_KIND" (LOCATION_KIND = login|other|-).
probe() {
  local h code loc
  h="$(curl -s -o /dev/null -D - --max-time 20 "$1" || true)"
  code="$(printf '%s' "$h" | awk 'toupper($1) ~ /^HTTP/ {c=$2} END {print c+0}')"
  loc="$(printf '%s' "$h" | tr -d '\r' | awk 'tolower($1)=="location:" {print $2}' | tail -1)"
  if [[ -z "$loc" ]]; then echo "$code -"
  elif [[ "$loc" =~ ^https://vercel\.com/(sso-api|login) ]]; then echo "$code login"
  else echo "$code other"; fi
}

# 1. Project
log "whoami: $("${VC[@]}" whoami 2>/dev/null | tail -1)  scope: $SCOPE"
PJ="$(api "/v9/projects/$PROJECT")"
PID="$(printf '%s' "$PJ" | jget id)"
if [[ -z "$PID" ]]; then
  [[ $CREATE == 1 ]] || { echo "project $PROJECT not found in $SCOPE (pass --create to make it)" >&2; exit 65; }
  log "creating project $PROJECT"
  CREATED=1
  "${VC[@]}" project add "$PROJECT" --scope "$SCOPE" >/dev/null 2>&1
  PJ="$(api "/v9/projects/$PROJECT")"; PID="$(printf '%s' "$PJ" | jget id)"
  [[ -n "$PID" ]] || { echo "project create failed" >&2; exit 65; }
fi
ORG="$(printf '%s' "$PJ" | jget accountId)"
[[ -z "$(printf '%s' "$PJ" | jget link)" ]] || { echo "$PROJECT has a Git repo connected; this script is for CLI-only projects" >&2; exit 66; }
CUSTOM="$(api "/v9/projects/$PID/domains" | python3 -c "import json,sys
d=json.load(sys.stdin); print(' '.join(x['name'] for x in d.get('domains',[]) if not x['name'].endswith('.vercel.app')))" 2>/dev/null || true)"
[[ -z "$CUSTOM" ]] || { echo "$PROJECT has custom domain(s): $CUSTOM. Pre-launch projects must not." >&2; exit 66; }
log "project $PROJECT ($PID), no Git link, no custom domain"

# 2. Protection must be on before anything is deployed
SSO="$(printf '%s' "$PJ" | jget ssoProtection.deploymentType)"
if [[ -z "$SSO" && $CREATED == 1 ]]; then
  log "new project: turning on Vercel Authentication (Standard Protection, free) before the first deploy"
  TMP="$(mktemp)"; echo '{"ssoProtection":{"deploymentType":"all_except_custom_domains"}}' > "$TMP"
  api "/v9/projects/$PID" -X PATCH --input "$TMP" >/dev/null; rm -f "$TMP"
  SSO="$(api "/v9/projects/$PID" | jget ssoProtection.deploymentType)"
fi
[[ -n "$SSO" ]] || { echo "ABORT: Vercel Authentication is OFF on $PROJECT. Turn it on (Settings > Deployment Protection) and rerun; nothing was deployed." >&2; exit 67; }
log "Vercel Authentication: ON ($SSO)"

DEPLOY_LOG="$(mktemp)"
deploy_preview() {  # prints the deployment URL parsed from the CLI's stdout
  local out url
  out="$(cd "$SITE_DIR" && VERCEL_ORG_ID="$ORG" VERCEL_PROJECT_ID="$PID" "${VC[@]}" deploy --target preview --yes 2>>"$DEPLOY_LOG")" || true
  url="$(printf '%s\n' "$out" | grep -oE "https://$PROJECT-[a-z0-9]+-$SCOPE\.vercel\.app" | tail -1 || true)"
  [[ -n "$url" ]] || url="$(printf '%s\n' "$out" | grep -oE "https://$PROJECT-[a-z0-9]{7,}-[a-z0-9-]+\.vercel\.app" | tail -1 || true)"
  echo "$url"
}
remove_deployment() {  # $1 = deployment id or host
  "${VC[@]}" rm "$1" --yes --scope "$SCOPE" >/dev/null 2>&1 && log "removed deployment $1" || log "COULD NOT remove deployment $1: remove it by hand now"
}
prod_count() {
  api "/v6/deployments?projectId=$PID&target=production&limit=50" | python3 -c "import json,sys
try: print(len(json.load(sys.stdin).get('deployments',[])))
except Exception: print('?')"
}
ALIASES=("https://$PROJECT.vercel.app" "https://$PROJECT-$SCOPE.vercel.app")

# 3. Deploy (one attempt, explicit preview target)
URL="$(deploy_preview)"
[[ -n "$URL" ]] || { echo "deploy failed: no deployment URL on stdout (CLI messages in $DEPLOY_LOG)" >&2; exit 68; }
for a in "${ALIASES[@]}"; do [[ "$URL" != "$a" ]] || { echo "parsed URL is a production alias ($URL); stopping" >&2; exit 68; }; done
DJ="$(api "/v13/deployments/${URL#https://}")"
DID="$(printf '%s' "$DJ" | jget id)"
TARGET="$(printf '%s' "$DJ" | jget target)"
log "deployed $URL (id ${DID:-?}, target: ${TARGET:-preview})"
[[ -n "$DID" ]] || { echo "could not look up the new deployment; check the project by hand" >&2; exit 68; }

# 4. Target and production aliases
FAIL=""
[[ "$TARGET" != "production" ]] || FAIL="deployment target is production"
for a in "${ALIASES[@]}"; do
  r="$(probe "$a/")"; log "logged-out $a -> $r"
  c="${r%% *}"; [[ "$c" == 404 || "$c" == 401 ]] || FAIL="${FAIL:+$FAIL; }$a answered $r logged out"
done
if [[ -n "$FAIL" ]]; then
  log "UNSAFE: $FAIL. Removing the new deployment now."
  remove_deployment "$DID"
  [[ "$TARGET" == "production" ]] && for a in "${ALIASES[@]}"; do "${VC[@]}" alias rm "${a#https://}" --yes --scope "$SCOPE" >/dev/null 2>&1 || true; done
  for a in "${ALIASES[@]}"; do log "after cleanup: logged-out $a -> $(probe "$a/")"; done
  echo "STOPPED: $FAIL. Nothing was retried; check the project by hand." >&2
  exit 69
fi

# 5. Preview must be blocked logged out (401 or 302 to the Vercel login)
R="$(probe "$URL/")"; log "logged-out $URL/ -> $R"
c="${R%% *}"; k="${R##* }"
if ! [[ "$c" == 401 || ( "$c" == 302 && "$k" == login ) ]]; then
  remove_deployment "$DID"
  echo "PREVIEW IS NOT PROTECTED: $URL answered $R; deployment removed" >&2
  exit 70
fi
for p in /contact /api/form-lead; do log "logged-out $URL$p -> $(probe "$URL$p")"; done
log "production deployments on $PROJECT: $(prod_count)"
[[ ! -d "$SITE_DIR/.vercel" ]] || log "note: $SITE_DIR/.vercel exists (it's gitignored)"
rm -f "$DEPLOY_LOG"
log "OK: preview is protected, target is preview, and no production alias serves content."
echo "PREVIEW_URL=$URL"
