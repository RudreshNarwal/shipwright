# Vendored skills — provenance

Shipwright bundles a pinned snapshot of several permissively-licensed skills so it installs as one
self-contained plugin — all MIT, plus one Apache-2.0 (`frontend-design`). Each skill below was copied
verbatim from its upstream source on **2026-06-13**, then had its internal skill references
re-namespaced from the upstream prefix to `shipwright:` (so they resolve to the bundled copies
regardless of what else you have installed). No logic was changed.

Upstream license texts are preserved in [`licenses/`](./licenses/). Re-sync a newer upstream
version with [`scripts/sync-vendored.sh`](./scripts/sync-vendored.sh).

## superpowers — MIT © 2025 Jesse Vincent

- Source: https://github.com/obra/superpowers
- Version pinned: **5.1.0**
- License: MIT (`licenses/superpowers.LICENSE`)
- Skills vendored: `brainstorming`, `writing-plans`, `test-driven-development`,
  `subagent-driven-development`, `executing-plans`, `requesting-code-review`,
  `receiving-code-review`, `systematic-debugging`, `verification-before-completion`,
  `finishing-a-development-branch`, `using-git-worktrees`

## andrej-karpathy-skills — MIT © forrestchang

- Source: https://github.com/forrestchang/andrej-karpathy-skills
- Version pinned: **1.0.0**
- License: MIT (`licenses/karpathy-skills.LICENSE`)
- Skills vendored: `karpathy-guidelines`

## gstack — NOT vendored (runtime dependency)

- Source: https://github.com/garrytan/gstack — MIT © 2026 Garry Tan — version 1.33.2.0 at time of writing
- gstack is a ~1 GB Bun/TypeScript product with a compiled `browse` CLI and a Chrome extension;
  it cannot be sensibly bundled. Shipwright declares it as a dependency, checks for it in Phase 0,
  and ships `scripts/install-gstack.sh` to install it. Used in Phases 5–6
  (`/qa`, `/qa-only`, `/browse`, `/design-review`, `/autoplan`, `/ship`, `/setup-browser-cookies`).

## frontend-design — Apache-2.0 © Anthropic

- Source: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design
  (distributed via the `claude-plugins-official` marketplace)
- Version pinned: commit **`ac16ffafcd70`** (no version field is published; date-pinned 2026-06-13)
- License: **Apache-2.0** (`licenses/frontend-design.LICENSE`) — the one non-MIT bundled skill;
  Apache-2.0 is permissive and redistributable inside this MIT repo with its license text preserved.
  No `NOTICE` file exists upstream. Copied verbatim with no namespace references and no changes
  (so there is nothing to state under Apache-2.0 §4).
- Skills vendored: `frontend-design` (referenced as `shipwright:frontend-design`). Required only for
  frontend/UI work.
