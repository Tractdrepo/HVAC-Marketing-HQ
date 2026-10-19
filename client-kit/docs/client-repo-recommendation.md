# Per-client repo: recommendation (needs Logan's decision)
*Mon Oct 19, 2026 (CDT). Nothing has been created.*

**Recommendation:** use one **private template repo** plus **one private repo per client**, made from it.

1. **Template repo** `Tractdrepo/hvac-client-template` (private, "Template repository" box ticked) containing:
   - `site-generator/` (generate.py + tests)
   - `form-lead/` (function, harness, tests)
   - `scripts/` (`deploy-preview.sh`, `new-client-repo.sh`)
   - `clients/_example/client.json`
   - a CI-free `package.json` test script

   It's built once from `client-kit/` after PR #25 is reviewed.
2. **Per client:**
   - `client-kit/scripts/new-client-repo.sh <slug> --yes` creates `Tractdrepo/client-<slug>` (private) from the template and starts a `setup` branch with `client.json` (NOINDEX on).
   - The site deploys from the CLI to the client's own Vercel project with `deploy-preview.sh` (no Git link).
3. **Why:**
   - The live site promises the site files at offboarding: one repo is one clean handover (transfer the repo or zip it).
   - Clients never share code or history.
   - Template fixes reach existing clients by a deliberate merge or copy, not by accident.
4. **Costs:** GitHub private repos are free.
5. **Downside:** template updates have to be pulled into each client repo by hand (or with a small sync script later).
6. **Alternative:** keep all clients in one private monorepo under `clients/<slug>`. Simpler to update, but handover means extracting history, and every client's files sit together.

**Decision needed from Logan:**
- per-client repos (recommended) or monorepo
- the template repo name
- whether repos live under `Tractdrepo` or a separate org

Until he decides, `new-client-repo.sh` stays unrun. It defaults to a dry run.
