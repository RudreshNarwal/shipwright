#!/usr/bin/env bash
# Bootstrap gstack — the one Provenship dependency that can't be vendored — and everything it needs:
# Bun (if missing), the gstack clone, its ./setup, and Playwright's browser. Idempotent: each step
# is skipped if already satisfied.
#
#   bash install-gstack.sh           # interactive — prompts before installing Bun / the browser
#   bash install-gstack.sh --yes     # non-interactive — installs everything without prompting
#
# Env: GSTACK_DIR (default ~/.claude/skills/gstack), PROVENSHIP_ASSUME_YES=1 (same as --yes).
set -euo pipefail

GSTACK_DIR="${GSTACK_DIR:-$HOME/.claude/skills/gstack}"
REPO="https://github.com/garrytan/gstack.git"

# --yes, PROVENSHIP_ASSUME_YES=1, or a non-interactive shell (e.g. the SessionStart hook) → no prompts.
ASSUME_YES=0
{ [ "${1:-}" = "--yes" ] || [ "${PROVENSHIP_ASSUME_YES:-}" = "1" ] || [ ! -t 0 ]; } && ASSUME_YES=1

confirm() {  # confirm "question" — true in assume-yes mode, else ask
  [ "$ASSUME_YES" = "1" ] && return 0
  read -r -p "$1 [y/N] " ans && case "$ans" in [yY]*) return 0 ;; *) return 1 ;; esac
}

echo "Provenship :: gstack bootstrapper"

command -v git >/dev/null 2>&1 || { echo "ERROR: git is required (https://git-scm.com/)"; exit 1; }

# --- Bun (gstack's runtime) ------------------------------------------------
export PATH="${BUN_INSTALL:-$HOME/.bun}/bin:$PATH"   # in case Bun is installed but not yet on PATH
if ! command -v bun >/dev/null 2>&1; then
  if confirm "Bun (v1.0+) is required and not installed. Install it now?"; then
    echo "Installing Bun ..."
    curl -fsSL https://bun.sh/install | bash
    export PATH="${BUN_INSTALL:-$HOME/.bun}/bin:$PATH"
  fi
fi
command -v bun >/dev/null 2>&1 || { echo "ERROR: Bun is required (https://bun.sh/). Install it and re-run."; exit 1; }

# --- gstack clone + setup --------------------------------------------------
if [ -d "$GSTACK_DIR/.git" ]; then
  echo "gstack already present at $GSTACK_DIR"
  if confirm "Pull latest and re-run setup?"; then
    git -C "$GSTACK_DIR" pull --ff-only && ( cd "$GSTACK_DIR" && ./setup )
  fi
else
  echo "Cloning gstack into $GSTACK_DIR ..."
  git clone --single-branch --depth 1 "$REPO" "$GSTACK_DIR"
  ( cd "$GSTACK_DIR" && ./setup )
fi

# --- Playwright browser (gstack's ./setup usually handles this; ensure it) --
if confirm "Ensure Playwright's Chromium is installed (skip if gstack already did)?"; then
  echo "Ensuring Playwright Chromium ..."
  ( cd "$GSTACK_DIR" && bunx --bun playwright install chromium ) \
    || echo "note: Playwright install step skipped/failed — gstack's setup may already cover the browser."
fi

echo "gstack is ready. Provenship Phases 5-6 (browser + API QA, ship) can now run."
