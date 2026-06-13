#!/usr/bin/env bash
# Re-sync the vendored skills from their upstream repos and re-apply the shipwright: namespace.
# Usage: scripts/sync-vendored.sh [SUPERPOWERS_REF] [KARPATHY_REF]
#   refs default to the pinned versions below; pass a tag/branch/sha to bump.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
SP_REF="${1:-v5.1.0}"
KP_REF="${2:-main}"

SP_REPO="https://github.com/obra/superpowers.git"
KP_REPO="https://github.com/forrestchang/andrej-karpathy-skills.git"

SP_SKILLS=(brainstorming writing-plans test-driven-development subagent-driven-development \
  executing-plans requesting-code-review receiving-code-review systematic-debugging \
  verification-before-completion finishing-a-development-branch using-git-worktrees)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Cloning superpowers @ $SP_REF ..."
git clone --depth 1 --branch "$SP_REF" "$SP_REPO" "$tmp/superpowers"
echo "Cloning karpathy-skills @ $KP_REF ..."
git clone --depth 1 --branch "$KP_REF" "$KP_REPO" "$tmp/karpathy"

# upstream layouts: superpowers/skills/<name>, andrej-karpathy-skills/skills/<name>
for s in "${SP_SKILLS[@]}"; do
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -R "$tmp/superpowers/skills/$s" "$SKILLS_DIR/$s"
done
rm -rf "$SKILLS_DIR/karpathy-guidelines"
cp -R "$tmp/karpathy/skills/karpathy-guidelines" "$SKILLS_DIR/karpathy-guidelines"

# Re-namespace every vendored file (NOT the main shipwright skill — it's already correct).
find "$SKILLS_DIR" -type f -not -path "$SKILLS_DIR/shipwright/*" \
  \( -name "*.md" -o -name "*.dot" -o -name "*.ts" -o -name "*.js" -o -name "*.cjs" -o -name "*.sh" -o -name "*.html" \) -print0 \
  | xargs -0 perl -pi -e 's/andrej-karpathy-skills:karpathy-guidelines/shipwright:karpathy-guidelines/g; s/superpowers:/shipwright:/g'

echo "Re-synced. Update the version pins and date in VENDORED.md, then run the linter."
