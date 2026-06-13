#!/usr/bin/env bash
# Install gstack — the one Shipwright dependency that can't be vendored.
# Idempotent: skips the clone if gstack is already present.
set -euo pipefail

GSTACK_DIR="${GSTACK_DIR:-$HOME/.claude/skills/gstack}"
REPO="https://github.com/garrytan/gstack.git"

echo "Shipwright :: gstack installer"

command -v git >/dev/null 2>&1 || { echo "ERROR: git is required (https://git-scm.com/)"; exit 1; }
command -v bun >/dev/null 2>&1 || { echo "ERROR: Bun v1.0+ is required (https://bun.sh/)"; exit 1; }

if [ -d "$GSTACK_DIR/.git" ]; then
  echo "gstack already installed at $GSTACK_DIR"
  read -r -p "Pull latest and re-run setup? [y/N] " ans
  case "$ans" in
    [yY]*) git -C "$GSTACK_DIR" pull --ff-only && (cd "$GSTACK_DIR" && ./setup) ;;
    *) echo "Leaving existing install untouched." ;;
  esac
  exit 0
fi

echo "Cloning gstack into $GSTACK_DIR ..."
git clone --single-branch --depth 1 "$REPO" "$GSTACK_DIR"
( cd "$GSTACK_DIR" && ./setup )
echo "gstack installed. See its README for the optional team-mode auto-update step."
