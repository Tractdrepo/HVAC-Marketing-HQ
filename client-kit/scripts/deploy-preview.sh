#!/usr/bin/env bash
# Deploy a client site folder as a PROTECTED Vercel PREVIEW, with no Git link, and verify nothing is public.
# Free (Hobby) features only. Never adds a domain, never touches other projects.
#
#   client-kit/scripts/deploy-preview.sh <site-dir> <project-name> [--scope <team-slug>] [--create]
#   e.g. client-kit/scripts/deploy-preview.sh client-kit/sites/practice-hvac-co practice-hvac-co-test
#
# Needs: the Vercel CLI logged in on this machine (npx vercel@latest whoami), python3, curl.
# Why the blank page: a project with no production deployment sends the next CLI deploy to production (even with
# --target/--environment preview; seen Oct 18 and Oct 21, 2026), and the production *.vercel.app alias is public
# under Standard Protection. So production only ever holds a deliberate blank noindex page.
# Steps:
#  1. Look up the project (or create it with --create). Refuse if it has a Git repo connected or a custom domain.
#  a. Vercel Authentication must be ON. A project this run just created gets Standard Protection turned on first;
#     otherwise protection off = ABORT, nothing deployed.
#  b. If the project has no production deployment, deploy a BLANK placeholder as production first: one index.html
#     ("Nothing here", robots noindex meta), robots.txt Disallow: /, X-Robots-Tag noindex in vercel.json, tagged
#     with deployment meta hmhq_blank=1. No client or sample content.
#  c. Deploy the real build with --environment preview (meta hmhq_kind=preview). No `vercel link`: uses
#     VERCEL_ORG_ID/VERCEL_PROJECT_ID, so no .vercel folder and no Git auto-connect.
#  d. URLs are read from the CLI's stdout AND stderr; the preview URL is https://<project>-<hash>-<team>.vercel.app.
#  e. The new deployment's target must be preview; the production aliases must point at the blank deployment and
#     serve only the blank page (no title or text from the site, no PLACEHOLDER/TEST SITE); the preview URL must
#     answer 401 or a 302 to the Vercel login when logged out. A 302 only counts when its Location is vercel.com/login,
#     vercel.com/sso*, vercel.com/sso-api or the host's /_vercel/sso flow; any other redirect fails.
#  f. On ANY failure: remove every production deployment that isn't the blank placeholder, remove the new preview
#     if it isn't protected, and exit non-zero. No retries.
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
    -h|--help) sed -n '2,29p' "$0"; exit 0 ;;
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
  # Only Vercel's own login/SSO counts: vercel.com/login, vercel.com/sso*, vercel.com/sso-api, or this host's /_vercel/sso
  elif [[ "$loc" =~ ^https://vercel\.com/(login|sso-api|sso)([/?#]|$) || "$loc" =~ ^(https://[a-z0-9.-]+\.vercel\.app)?/_vercel/sso([/?#]|$) ]]; then echo "$code login"
  else echo "$code other"; fi
}


# --- failure handling (f) ---
PREVIEW_ID=""; PREVIEW_OK=0; DONE=0
is_blank() { [[ "$(api "/v13/deployments/$1" | jget meta.hmhq_blank)" == "1" ]]; }
prod_ids() {
  [[ -n "${PID:-}" ]] || return 0
  api "/v6/deployments?projectId=$PID&target=production&limit=100" | python3 -c "import json,sys
try: print(' '.join(d['uid'] for d in json.load(sys.stdin).get('deployments',[])))
except Exception: pass"
}
cleanup() {
  local rc=$? id
  [[ $DONE == 1 ]] && return
  [[ $rc -ne 0 ]] || return
  log "FAILURE (exit $rc): cleaning up"
  for id in $(prod_ids); do
    if is_blank "$id"; then log "keeping blank placeholder $id"
    else "${VC[@]}" rm "$id" --yes --scope "$SCOPE" >/dev/null 2>&1 && log "removed non-blank production deployment $id" || log "COULD NOT remove production deployment $id: remove it by hand NOW"; fi
  done
  if [[ -n "$PREVIEW_ID" && $PREVIEW_OK == 0 ]]; then "${VC[@]}" rm "$PREVIEW_ID" --yes --scope "$SCOPE" >/dev/null 2>&1 && log "removed unverified preview $PREVIEW_ID" || true; fi
  for a in "${ALIASES[@]:-}"; do [[ -n "$a" ]] && log "after cleanup: logged-out $a -> $(probe "$a/")"; done
}
ALIASES=()
trap cleanup EXIT
die() { echo "STOP: $*" >&2; exit "${2:-70}"; }

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

# a. Protection must be on before anything is deployed
SSO="$(printf '%s' "$PJ" | jget ssoProtection.deploymentType)"
if [[ -z "$SSO" && $CREATED == 1 ]]; then
  log "new project: turning on Vercel Authentication (Standard Protection, free) before the first deploy"
  TMP="$(mktemp)"; echo '{"ssoProtection":{"deploymentType":"all_except_custom_domains"}}' > "$TMP"
  api "/v9/projects/$PID" -X PATCH --input "$TMP" >/dev/null; rm -f "$TMP"
  SSO="$(api "/v9/projects/$PID" | jget ssoProtection.deploymentType)"
fi
[[ -n "$SSO" ]] || die "Vercel Authentication is OFF on $PROJECT. Turn it on and rerun; nothing was deployed." 67
log "Vercel Authentication: ON ($SSO)"
ALIASES=("https://$PROJECT.vercel.app" "https://$PROJECT-$SCOPE.vercel.app")

# Runs vercel deploy in $1 with extra args; prints the CLI's stdout+stderr (no secrets in it).
vdeploy() { local dir="$1"; shift; (cd "$dir" && VERCEL_ORG_ID="$ORG" VERCEL_PROJECT_ID="$PID" "${VC[@]}" deploy --yes "$@" 2>&1) || true; }
dpl_url() { grep -oE "https://$PROJECT-[a-z0-9]{7,}(-$SCOPE)?\.vercel\.app" | head -1 || true; }

# b. Production holds only a blank placeholder
BLANK_ID=""
for id in $(prod_ids); do
  if is_blank "$id"; then BLANK_ID="$id"; else die "production deployment $id is not the blank placeholder (pre-launch projects must not have one)" 71; fi
done
if [[ -z "$BLANK_ID" ]]; then
  BLANK_DIR="$(mktemp -d)"
  cat > "$BLANK_DIR/index.html" <<'HTML'
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Nothing here</title></head><body><p>Nothing here</p><!-- hmhq-blank-placeholder --></body></html>
HTML
  printf 'User-agent: *\nDisallow: /\n' > "$BLANK_DIR/robots.txt"
  echo '{"headers":[{"source":"/(.*)","headers":[{"key":"X-Robots-Tag","value":"noindex, nofollow"}]}]}' > "$BLANK_DIR/vercel.json"
  log "no production deployment: deploying the blank noindex placeholder to production"
  OUT="$(vdeploy "$BLANK_DIR" --environment production --meta hmhq_blank=1)"
  rm -rf "$BLANK_DIR"
  BURL="$(printf '%s\n' "$OUT" | dpl_url)"
  [[ -n "$BURL" ]] || die "blank placeholder deploy gave no URL" 68
  BLANK_ID="$(api "/v13/deployments/${BURL#https://}" | jget id)"
  [[ -n "$BLANK_ID" ]] && is_blank "$BLANK_ID" || die "could not confirm the blank placeholder deployment" 68
  log "blank placeholder: $BLANK_ID"
fi
SITE_TITLE="$(python3 -c "import re,sys,html;t=re.search(r'<title>(.*?)</title>',open(sys.argv[1]).read(),re.S);print(html.unescape(t.group(1)).split(' | ')[-1].strip() if t else '')" "$SITE_DIR/index.html")"
check_prod_aliases() {
  local a body code dep
  for a in "${ALIASES[@]}"; do
    body="$(curl -s --max-time 20 -w '\n%{http_code}' "$a/" || true)"; code="${body##*$'\n'}"; body="${body%$'\n'*}"
    if [[ "$code" == 404 || "$code" == 401 ]]; then log "logged-out $a -> $code (no content)"; continue; fi
    if [[ "$code" == 302 || "$code" == 307 ]]; then
      [[ "$(probe "$a/")" == *" login" ]] || die "$a redirects somewhere other than the Vercel login/SSO" 69
      log "logged-out $a -> $code to the Vercel login/SSO (protected, no content)"; continue
    fi
    [[ "$code" == 200 ]] || die "$a answered $code logged out (expected the blank page or 404)" 69
    [[ "$body" == *hmhq-blank-placeholder* && "$body" == *'content="noindex,nofollow"'* ]] || die "$a serves something other than the blank placeholder" 69
    [[ -z "$SITE_TITLE" || "$body" != *"$SITE_TITLE"* ]] && [[ "$body" != *PLACEHOLDER* && "$body" != *"TEST SITE"* ]] || die "$a shows site content" 69
    curl -s -o /dev/null -D - --max-time 20 "$a/" | tr -d '\r' | grep -qi '^x-robots-tag: noindex' || die "$a has no X-Robots-Tag noindex" 69
    dep="$(api "/v4/aliases/${a#https://}" | jget deploymentId)"
    [[ -z "$dep" || "$dep" == "$BLANK_ID" ]] || die "$a points at $dep, not the blank placeholder" 69
    log "logged-out $a -> 200 blank noindex placeholder only"
  done
}
check_prod_aliases

# c-d. Real build as a preview
OUT="$(vdeploy "$SITE_DIR" --environment preview --meta hmhq_kind=preview)"
URL="$(printf '%s\n' "$OUT" | dpl_url)"
[[ -n "$URL" ]] || { printf '%s\n' "$OUT" | grep -iE "error|warn" | head -5 >&2; die "preview deploy gave no deployment URL" 68; }
DJ="$(api "/v13/deployments/${URL#https://}")"
PREVIEW_ID="$(printf '%s' "$DJ" | jget id)"; TARGET="$(printf '%s' "$DJ" | jget target)"
log "deployed $URL (id ${PREVIEW_ID:-?}, target: ${TARGET:-preview})"
[[ -n "$PREVIEW_ID" ]] || die "could not look up the new deployment" 68
# e. Target, production aliases, preview protection
[[ "$TARGET" != "production" ]] || die "the build landed on production" 69
check_prod_aliases
R="$(probe "$URL/")"; log "logged-out $URL/ -> $R"
c="${R%% *}"; k="${R##* }"
[[ "$c" == 401 || ( "$c" == 302 && "$k" == login ) ]] || die "PREVIEW IS NOT PROTECTED: $URL answered $R" 70
PREVIEW_OK=1
for p in /contact /services /api/form-lead; do log "logged-out $URL$p -> $(probe "$URL$p")"; done
for id in $(prod_ids); do is_blank "$id" || die "non-blank production deployment $id appeared" 69; done
log "production deployments: $(prod_ids | wc -w) (blank placeholder only)"
[[ ! -d "$SITE_DIR/.vercel" ]] || log "note: $SITE_DIR/.vercel exists (it's gitignored)"
DONE=1
log "OK: preview is protected, target is preview, production serves only the blank noindex page."
echo "PREVIEW_URL=$URL"
