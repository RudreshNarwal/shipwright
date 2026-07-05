---
name: update
description: Update Provenship's dependencies to latest — vendored skills (superpowers/karpathy/frontend-design), gstack, and Playwright Chromium. Use when the user invokes /provenship:update, says "update provenship", "update the skills", or "update everything".
---

# Update Provenship

Pull the latest of everything Provenship depends on, then verify.

## Steps

1. Resolve the plugin root: use `${CLAUDE_PLUGIN_ROOT}` if set, otherwise resolve it
   relative to this skill — it is two directories up (`skills/update/` → repo root).

2. Run the three bundled scripts in order, chained so a failure stops the run:

   ```bash
   ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
   "$ROOT"/scripts/sync-vendored.sh main main HEAD \
     && "$ROOT"/scripts/install-gstack.sh --yes \
     && "$ROOT"/scripts/lint.sh
   ```

   - `sync-vendored.sh main main HEAD` — latest superpowers, karpathy, frontend-design
   - `install-gstack.sh --yes` — pulls latest gstack, re-runs its `./setup`, ensures
     Playwright Chromium (idempotent, non-interactive)
   - `lint.sh` — the required post-sync self-checks

3. Remind the user to bump the version pins + date in `VENDORED.md` — `sync-vendored.sh`
   prints this too; it is intentionally not automated.
