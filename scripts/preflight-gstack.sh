#!/usr/bin/env bash
# SessionStart preflight: detect gstack and surface its status to Provenship.
# - gstack present            -> stay silent (no context noise).
# - missing                   -> print a one-line, actionable install message (becomes session context).
# - missing + opt-in env set  -> kick off the bootstrapper in the background, once, and say so.
#
# Opt in to background auto-install with:  export PROVENSHIP_AUTO_INSTALL_GSTACK=1
# (Default is detect-and-tell: we don't silently download ~1GB + a browser without consent.)
set -euo pipefail

GSTACK_DIR="${GSTACK_DIR:-$HOME/.claude/skills/gstack}"
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
DATA="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/provenship}"
INSTALLER="$ROOT/scripts/install-gstack.sh"

# Present already? Say nothing.
[ -d "$GSTACK_DIR" ] && exit 0

if [ ! -f "$INSTALLER" ]; then
  echo "Provenship: gstack is not installed (needed for Phases 5-6). Installer not found at $INSTALLER."
  exit 0
fi

if [ "${PROVENSHIP_AUTO_INSTALL_GSTACK:-}" = "1" ]; then
  mkdir -p "$DATA" 2>/dev/null || true
  lock="$DATA/gstack-install.lock"
  log="$DATA/gstack-install.log"
  if [ -f "$lock" ]; then
    echo "Provenship: gstack auto-install is already running in the background (log: $log)."
  else
    : > "$lock" 2>/dev/null || true
    nohup bash -c "bash '$INSTALLER' --yes; rm -f '$lock'" </dev/null >"$log" 2>&1 &
    disown 2>/dev/null || true
    echo "Provenship: gstack not found — auto-installing it in the background (opt-in via PROVENSHIP_AUTO_INSTALL_GSTACK). Progress: $log. Phases 5-6 (browser+API QA, ship) become available once it finishes; if interrupted, re-run: bash \"$INSTALLER\"."
  fi
else
  echo "Provenship: gstack is not installed — needed for Phases 5-6 (browser+API QA, design review, ship). Install it with:  bash \"$INSTALLER\"  (also brings Bun + Playwright). Or set PROVENSHIP_AUTO_INSTALL_GSTACK=1 to auto-install on session start. Phases 1-4 run without it."
fi
exit 0
