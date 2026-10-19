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
#  2. Make sure Vercel Authentication (Standard Protection, free) is on; turn it on if it's off.
#  3. Deploy a preview from <site-dir> using VERCEL_ORG_ID/VERCEL_PROJECT_ID (no `vercel link`, so no .vercel
#     folder and no Git auto-connect).
#  4. Logged-out curl of <project>.vercel.app and <project>-<team>.vercel.app right after. Anything but
#     404 / 401 / 403 / 302-to-Vercel-login counts as PUBLIC: remove that alias, delete the deployment it pointed
#     to, and redeploy as a preview (once). (A new project's FIRST CLI deploy can land as production and get the
#     public <project>.vercel.app alias; seen Oct 18, 2026.)
#  5. Logged-out curl of the preview URL must be 401/403/302-to-login, or the script exits non-zero.
# The CLI keeps its own token; this script never reads, prints or passes one.
set -euo pipefail

SCOPE="williamtaylor1204-2866s-projects"
CREATE=0
POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    --create) CREATE=1; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
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
api() { "${VC[@]}" api "$@" --scope "$SCOPE" --raw 2>/dev/null; }
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
is_blocked() { local c="${1%% *}" k="${1##* }"; [[ "$c" == 401 || "$c" == 403 || ( "$c" == 302 && "$k" == login ) ]]; }
is_safe_alias() { local c="${1%% *}"; [[ "$c" == 404 ]] || is_blocked "$1"; }

# 1. Project
log "whoami: $("${VC[@]}" whoami 2>/dev/null | tail -1)  scope: $SCOPE"
PJ="$(api "/v9/projects/$PROJECT")"
PID="$(printf '%s' "$PJ" | jget id)"
if [[ -z "$PID" ]]; then
  [[ $CREATE == 1 ]] || { echo "project $PROJECT not found in $SCOPE (pass --create to make it)" >&2; exit 65; }
  log "creating project $PROJECT"
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

# 2. Protection
SSO="$(printf '%s' "$PJ" | jget ssoProtection.deploymentType)"
if [[ -z "$SSO" ]]; then
  log "Vercel Authentication is OFF; turning on Standard Protection (free)"
  TMP="$(mktemp)"; echo '{"ssoProtection":{"deploymentType":"all_except_custom_domains"}}' > "$TMP"
  api "/v9/projects/$PID" -X PATCH --input "$TMP" >/dev/null; rm -f "$TMP"
  SSO="$(api "/v9/projects/$PID" | jget ssoProtection.deploymentType)"
fi
[[ -n "$SSO" ]] || { echo "could not turn on Vercel Authentication" >&2; exit 67; }
log "Vercel Authentication: ON ($SSO)"

deploy() {
  local out url
  out="$(cd "$SITE_DIR" && VERCEL_ORG_ID="$ORG" VERCEL_PROJECT_ID="$PID" "${VC[@]}" deploy --yes 2>/dev/null)"
  url="$(printf '%s\n' "$out" | grep -oE 'https://[a-z0-9-]+\.vercel\.app' | tail -1)"
  [[ -n "$url" ]] || { echo "deploy failed (no URL)" >&2; exit 68; }
  echo "$url"
}

ALIASES=("https://$PROJECT.vercel.app" "https://$PROJECT-$SCOPE.vercel.app")
check_aliases() {  # prints the first public alias, or nothing
  local a r
  for a in "${ALIASES[@]}"; do
    r="$(probe "$a/")"; log "logged-out $a -> $r" >&2
    is_safe_alias "$r" || { echo "$a"; return; }
  done
}

# 3-4. Deploy, then check the production-style aliases right away
for round in 1 2; do
  URL="$(deploy)"; [[ -n "$URL" ]] || exit 68
  TARGET="$(api "/v13/deployments/${URL#https://}" | jget target)"
  log "deployed $URL (target: ${TARGET:-preview})"
  PUBLIC="$(check_aliases)"
  [[ -z "$PUBLIC" ]] && break
  log "PUBLIC: $PUBLIC answers logged out. Removing it."
  HOST="${PUBLIC#https://}"
  DID="$(api "/v13/deployments/$HOST" | jget id)"
  "${VC[@]}" alias rm "$HOST" --yes --scope "$SCOPE" >/dev/null 2>&1 || true
  [[ -n "$DID" ]] && "${VC[@]}" rm "$DID" --yes --scope "$SCOPE" >/dev/null 2>&1 && log "removed alias $HOST and deployment $DID"
  if [[ "$(api "/v13/deployments/${URL#https://}" | jget readyState)" == "" ]]; then
    log "the new deployment was the public one and is deleted; redeploying as a preview"
  fi
  [[ $round == 2 ]] && { echo "still public after cleanup; stop and check the project by hand" >&2; exit 69; }
done

# make sure the final URL still exists (it may have been the deleted one)
if [[ -z "$(api "/v13/deployments/${URL#https://}" | jget id)" ]]; then URL="$(deploy)"; [[ -n "$URL" ]] || exit 68; log "redeployed $URL"; fi

# 5. Preview must be blocked logged out
R="$(probe "$URL/")"; log "logged-out $URL/ -> $R"
is_blocked "$R" || { echo "PREVIEW IS NOT PROTECTED: $URL answered $R" >&2; exit 70; }
for p in /contact /api/form-lead; do log "logged-out $URL$p -> $(probe "$URL$p")"; done
[[ ! -d "$SITE_DIR/.vercel" ]] || log "note: $SITE_DIR/.vercel exists (it's gitignored)"
log "OK: preview is protected and no public alias answers."
echo "PREVIEW_URL=$URL"
