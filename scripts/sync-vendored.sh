#!/usr/bin/env bash
# Re-sync the vendored skills from their upstream repos and re-apply the shipwright: namespace.
# Usage: scripts/sync-vendored.sh [SUPERPOWERS_REF] [KARPATHY_REF] [FRONTEND_DESIGN_REF]
#   refs default to the pinned versions below; pass a tag/branch/sha to bump.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LICENSES_DIR="$ROOT/licenses"
SKILLS_DIR="$ROOT/skills"
SP_REF="${1:-v5.1.0}"
KP_REF="${2:-main}"
# frontend-design ships through the claude-plugins-official marketplace (no version field); pin by
# commit. `git clone --branch` rejects a bare SHA, so we clone then `checkout` the ref below.
FD_REF="${3:-ac16ffafcd70}"

SP_REPO="https://github.com/obra/superpowers.git"
KP_REPO="https://github.com/forrestchang/andrej-karpathy-skills.git"
FD_REPO="https://github.com/anthropics/claude-plugins-official.git"

SP_SKILLS=(brainstorming writing-plans test-driven-development subagent-driven-development \
  executing-plans requesting-code-review receiving-code-review systematic-debugging \
  verification-before-completion finishing-a-development-branch using-git-worktrees)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Cloning superpowers @ $SP_REF ..."
git clone --depth 1 --branch "$SP_REF" "$SP_REPO" "$tmp/superpowers"
echo "Cloning karpathy-skills @ $KP_REF ..."
git clone --depth 1 --branch "$KP_REF" "$KP_REPO" "$tmp/karpathy"
echo "Cloning claude-plugins-official @ $FD_REF (for frontend-design) ..."
git clone "$FD_REPO" "$tmp/cpp"
git -C "$tmp/cpp" checkout "$FD_REF" 2>/dev/null || echo "  (ref $FD_REF not found; using default-branch HEAD — re-pin in VENDORED.md)"

# upstream layouts: superpowers/skills/<name>, andrej-karpathy-skills/skills/<name>,
# claude-plugins-public/plugins/frontend-design/{skills/frontend-design,LICENSE}
for s in "${SP_SKILLS[@]}"; do
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -R "$tmp/superpowers/skills/$s" "$SKILLS_DIR/$s"
done
rm -rf "$SKILLS_DIR/karpathy-guidelines"
cp -R "$tmp/karpathy/skills/karpathy-guidelines" "$SKILLS_DIR/karpathy-guidelines"
rm -rf "$SKILLS_DIR/frontend-design"
cp -R "$tmp/cpp/plugins/frontend-design/skills/frontend-design" "$SKILLS_DIR/frontend-design"
# frontend-design is Apache-2.0 — preserve its license text alongside the MIT ones.
cp "$tmp/cpp/plugins/frontend-design/LICENSE" "$LICENSES_DIR/frontend-design.LICENSE"

# Re-namespace every vendored file (NOT the main shipwright skill — it's already correct).
find "$SKILLS_DIR" -type f -not -path "$SKILLS_DIR/shipwright/*" \
  \( -name "*.md" -o -name "*.dot" -o -name "*.ts" -o -name "*.js" -o -name "*.cjs" -o -name "*.sh" -o -name "*.html" \) -print0 \
  | xargs -0 perl -pi -e 's/andrej-karpathy-skills:karpathy-guidelines/shipwright:karpathy-guidelines/g; s/superpowers:/shipwright:/g'

echo "Re-synced. Update the version pins and date in VENDORED.md, then run the linter."
