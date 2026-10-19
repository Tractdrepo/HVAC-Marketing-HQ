#!/usr/bin/env bash
# Create a PRIVATE per-client site repo from the HMHQ client template repo. DRY RUN by default: it only prints the
# commands. Pass --yes to actually create the repo (Logan approves the repo approach first; see
# /workspace/onboarding/client-repo-recommendation.md).
#
#   client-kit/scripts/new-client-repo.sh <client-slug> [--owner Tractdrepo] [--template Tractdrepo/hvac-client-template] [--yes]
#   e.g. client-kit/scripts/new-client-repo.sh acme-heating-air
#
# What it does (with --yes):
#  1. Checks gh is logged in and the template repo exists and is marked as a template.
#  2. Refuses if <owner>/client-<slug> already exists.
#  3. gh repo create <owner>/client-<slug> --private --template <template> --clone (private, never public).
#  4. In the clone: sets a repo-local git identity, copies clients/_example/client.json to
#     clients/<slug>/client.json with the slug filled in and NOINDEX=true, commits on a branch "setup".
#  5. Prints the next steps (fill client.json from the kickoff, generate, deploy-preview.sh).
# It never adds collaborators, never changes visibility, never touches Vercel or GHL, never handles tokens.
set -euo pipefail

OWNER="Tractdrepo"
TEMPLATE="Tractdrepo/hvac-client-template"
DO=0
POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --yes) DO=1; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) POS+=("$1"); shift ;;
  esac
done
[[ ${#POS[@]} -eq 1 ]] || { echo "usage: $0 <client-slug> [--owner o] [--template o/r] [--yes]" >&2; exit 64; }
SLUG="${POS[0]}"
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]{1,60}$ ]] || { echo "slug: lowercase letters, digits, dashes" >&2; exit 64; }
REPO="$OWNER/client-$SLUG"

run() { if [[ $DO == 1 ]]; then echo "+ $*"; "$@"; else echo "[dry run] $*"; fi; }

gh auth status >/dev/null 2>&1 || { echo "gh is not logged in" >&2; exit 65; }
IS_TEMPLATE="$(gh repo view "$TEMPLATE" --json isTemplate,visibility -q '.isTemplate' 2>/dev/null || echo missing)"
if [[ "$IS_TEMPLATE" != "true" ]]; then
  echo "template repo $TEMPLATE is missing or not marked as a template ($IS_TEMPLATE)." >&2
  [[ $DO == 1 ]] && exit 65
fi
if gh repo view "$REPO" >/dev/null 2>&1; then echo "$REPO already exists; not touching it" >&2; exit 66; fi

run gh repo create "$REPO" --private --template "$TEMPLATE" --clone --description "Client website: $SLUG (private)"
if [[ $DO == 1 ]]; then
  cd "client-$SLUG"
  [[ "$(gh repo view "$REPO" --json visibility -q .visibility)" == "PRIVATE" ]] || { echo "repo is not private! stop and fix by hand" >&2; exit 67; }
  git config user.name "HMHQ Web Developer Bot"
  git config user.email "334315570+Tractdrepo@users.noreply.github.com"
  git checkout -b setup
  mkdir -p "clients/$SLUG/assets"
  python3 - "$SLUG" <<'PY'
import json, sys
slug = sys.argv[1]
cfg = json.load(open("clients/_example/client.json"))
cfg.update({"slug": slug, "NOINDEX": True, "TEST_SITE": False, "CHAT_WIDGET_ID": ""})
cfg.pop("_note", None)
json.dump(cfg, open(f"clients/{slug}/client.json", "w"), indent=2)
PY
  git add "clients/$SLUG" && git commit -qm "Start client.json for $SLUG (NOINDEX on)"
  git push -q -u origin setup
fi
cat <<NEXT

Next steps for $REPO:
 1. Fill clients/$SLUG/client.json from the kickoff (real facts only; city facts only if the client gave them).
 2. Put the client's own logo/photos in clients/$SLUG/assets/.
 3. python3 site-generator/generate.py clients/$SLUG/client.json --out sites/$SLUG
 4. scripts/deploy-preview.sh sites/$SLUG client-$SLUG --create   (protected preview, no Git link)
 5. Env vars go into that Vercel project from the secret store (see ghl-handover-checklist.md). Never in the repo.
NEXT
