# CLAUDE.md — Shipwright

Guidance for Claude Code working in this repository.

## What this is

**Shipwright** is an open-source [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
plugin that drives a feature/bugfix end-to-end: brainstorm → plan → build (TDD, subagents) →
review → browser QA (UI **and** real API calls) → evidence-rich finalize (report + screenshots +
per-stage cost table) → ship (PR). It can run interactively or fully autonomously from a single
requirement after one approval gate.

It is an **orchestrator**: each phase invokes another skill and waits for it to finish. The
discipline comes from Karpathy's rules (don't assume, simplicity first, surgical changes,
goal-driven), propagated into every phase and every subagent prompt.

Pitch: *"Hand it a requirement, get back a PR with proof."*

## Origin & relationship to the private skill

Shipwright is the public, open-source build of a private personal skill called **`rudys-workflow`**
that lives at `~/.claude/skills/rudys-workflow/` on the author's machine. **That private skill is the
source of truth for the author's own use and must NOT be modified by work in this repo.** Shipwright
is a renamed, genericized, self-contained copy intended for public distribution.

When porting changes from `rudys-workflow` → here: rename to `shipwright`, strip personal paths
(`~/.claude/skills/rudys-workflow/...`), and rewrite skill namespaces to `shipwright:` (see below).

## Locked decisions (from brainstorming, 2026-06-13)

| Decision | Choice | Why |
|---|---|---|
| Name | `shipwright` | A shipwright builds ships — disciplined building that always ends in shipping. `/shipwright` reads well as a command. |
| Repo | `github.com/RudreshNarwal/shipwright` (personal account) | It's the author's workflow/brand; portable. |
| License | MIT (repo) | Bundled skills are permissive: MIT, plus one Apache-2.0 (`frontend-design`). Apache-2.0 is redistributable inside an MIT repo with its license text preserved — no incompatible copyleft is mixed in. |
| Distribution | Plugin **and** copy-able `skills/` folder | One-command install for most; copy path for the rest. |
| Dependencies | Vendor superpowers + karpathy (MIT) **and frontend-design (Apache-2.0)** — all pure markdown. **Do NOT vendor gstack.** | gstack is a ~1 GB Bun/TypeScript product (compiled `browse` CLI + Chrome extension) — vendoring = forking a live product forever. |
| Scope | Full launch kit (CI, sync script, CONTRIBUTING, demo report) | "Make it famous." |

## Repo layout

```
.claude-plugin/
  plugin.json          # the plugin definition (name, version, MIT, author)
  marketplace.json     # makes `/plugin marketplace add RudreshNarwal/shipwright` work
skills/
  shipwright/          # THE MAIN WORKFLOW — this is the project's own code
    SKILL.md           # the 6-phase pipeline + Phase-0 preflight + autonomy gate
    cost-table.py      # per-stage token/cost attribution from session transcripts
  <11 vendored skills> # pinned upstream copies — DO NOT hand-edit (see below)
scripts/
  install-gstack.sh    # installs the one un-vendorable dependency (idempotent)
  sync-vendored.sh     # re-pulls upstream skills + re-applies the namespace rewrite
  lint.sh              # the self-checks; CI and local both run this
licenses/              # preserved upstream MIT notices (MIT requires this)
VENDORED.md            # provenance: upstream repo, pinned version, date, license per skill
docs/
  specs/               # the approved design spec
  plans/               # the implementation plan
  example-report/      # ILLUSTRATIVE finalize report (fabricated numbers — replace before launch)
.github/
  workflows/lint.yml   # runs scripts/lint.sh on push/PR
  ISSUE_TEMPLATE/
README.md  CONTRIBUTING.md  LICENSE  .gitignore
```

## The vendoring model (most important thing to understand)

Everything under `skills/` **except `skills/shipwright/`** is a pinned, verbatim copy of an upstream
permissively-licensed skill (MIT, or Apache-2.0 for `frontend-design`), with one mechanical
transformation applied: skill cross-references are re-namespaced from
the upstream prefix to `shipwright:` so they resolve to the bundled copies regardless of what else the
user has installed.

- `superpowers:<x>` → `shipwright:<x>`
- `andrej-karpathy-skills:karpathy-guidelines` → `shipwright:karpathy-guidelines`
- `frontend-design` → referenced as `shipwright:frontend-design`; its own SKILL.md has **no** skill
  cross-references, so the rewrite is a no-op on it (the reference rename lives in the main skill).
- `elements-of-style:<x>` → **left untouched** (optional, not vendored; upstream treats it as "if available")
- Bare-word "superpowers" with no colon (e.g. `~/.config/superpowers/worktrees/`,
  `.superpowers/brainstorm/`, `docs/superpowers/specs/`) → **left untouched**; these are directory
  paths, not skill references, and they keep working.

**Vendored skills (13 dirs):**
- From **superpowers** (https://github.com/obra/superpowers, MIT © Jesse Vincent, pinned v5.1.0):
  brainstorming, writing-plans, test-driven-development, subagent-driven-development, executing-plans,
  requesting-code-review, receiving-code-review, systematic-debugging, verification-before-completion,
  finishing-a-development-branch, using-git-worktrees.
- From **andrej-karpathy-skills** (https://github.com/forrestchang/andrej-karpathy-skills, MIT ©
  forrestchang, pinned v1.0.0): karpathy-guidelines.
- From **claude-plugins-official** (https://github.com/anthropics/claude-plugins-official, **Apache-2.0**
  © Anthropic, pinned commit `ac16ffafcd70`): frontend-design. Required only for UI work; its
  Apache-2.0 license is preserved in `licenses/frontend-design.LICENSE`.

`using-git-worktrees` is included because it's transitively referenced by the others; the reference
closure was verified (no dangling `shipwright:` refs).

**gstack is NOT bundled.** It's a declared runtime dependency, checked in the skill's Phase 0 and
installed via `scripts/install-gstack.sh`. Used in Phases 5–6 (`/qa`, `/qa-only`, `/browse`,
`/design-review`, `/autoplan`, `/ship`, `/setup-browser-cookies`).

## Rules for changes

- **Never hand-edit a vendored skill.** Fixes belong upstream; pull them back with
  `scripts/sync-vendored.sh <superpowers-ref> <karpathy-ref> <frontend-design-ref>`, then update the
  version pins + date in `VENDORED.md` and run `scripts/lint.sh`.
- **The workflow itself** is `skills/shipwright/SKILL.md` + `cost-table.py`. That's where pipeline
  changes go.
- `SKILL.md` is a **discipline-enforcing skill**. Its `description:` frontmatter must be
  **triggers-only** — NEVER summarize the workflow there (Claude follows the summary and skips reading
  the skill body). Edits should follow the superpowers writing-skills TDD loop (observe the failing
  behavior, make the minimal change, confirm it holds).
- **Always run `bash scripts/lint.sh` before committing.** It is the same suite CI runs:
  1. no upstream namespaces left in `skills/`
  2. every `shipwright:<x>` reference resolves to a bundled dir
  3. `cost-table.py` compiles
  4. JSON manifests are valid
  5. no personal references ("rudy") in the main skill
- Git: commit messages end with the project's Co-Authored-By trailer. Don't push or create the GitHub
  repo unless asked — the remote does not exist yet and the name hasn't been claimed.

## How the main skill works (quick map)

`skills/shipwright/SKILL.md` defines:
- **Entry map** — start at the right phase if a spec/plan/code already exists (don't redo finished work).
- **Phase 0 — Preflight** — verify gstack installed (superpowers/karpathy/frontend-design are bundled);
  stop with install instructions if gstack is missing.
- **Discipline** — invoke `shipwright:karpathy-guidelines` at start; rules apply to every phase.
- **Autonomy gate** (asked once, after Phase 1) — "run autonomously?" + QA credentials. Yes → zero
  further questions, recommended defaults table, safer-interpretation-logged on ambiguity.
- **6 phases** — Brainstorm, Plan, Build, Review, QA (UI + API via `browse network`), Finalize+Ship.
- **Phase 5 escalation / loop-back** — a QA finding bigger than a local fix is triaged (architecture →
  re-plan, design → re-design, scope → re-scope) and loops back to Phase 2/1 for the affected slice
  only. Interactive: confirm with the user first. Autonomous: automatic, except a product/scope
  redefinition stops and surfaces.
- **Credentials** — env/creds-file → gate answer → self-register a throwaway account (non-prod only).
- **Cost tracking** — write a stage marker to `.claude/finalize-stages.jsonl` at each phase start;
  `cost-table.py` buckets transcript token usage into stage windows and prints a markdown cost table.

## cost-table.py notes

- Path-agnostic: uses `Path.cwd()` to find the project's transcript dir under
  `~/.claude/projects/<sanitized-cwd>/`. Run it from the repo being shipped, not from this repo.
- Pricing table is **best-effort USD per 1M tokens**, first-substring-match wins; keep current (Opus
  4.5+ is far cheaper than legacy Opus — don't let "opus" match-all overcharge newer models). Sanity
  check totals against `/cost` or `--ccusage`.
- When stage markers exist it scans ALL transcripts in the project dir (so resumed/compacted sessions
  count) within a 30-min-pre-first-marker window.

## Known limitations / open items

- **`docs/example-report/` is fabricated/illustrative**, clearly labeled. Replace with a real
  captured run (real screenshots in `assets/`, real `cost-table.py` output) before any public launch.
- **Not pushed to GitHub**; name not yet claimed/verified on GitHub or the plugin marketplaces.
- **Plugin install not yet end-to-end tested** — manifests are schema-valid and match known-good
  installed plugins, but `/plugin marketplace add` against a local clone hasn't been run to confirm
  Claude Code loads `shipwright` + the vendored skills. Closing this is the main pre-launch gap.

## Conventions

- Markdown skills, JSON manifests, Python 3 (`cost-table.py`), Bash (scripts), GitHub Actions (CI).
- Bash scripts use `set -euo pipefail`; the namespace rewrite in `sync-vendored.sh` uses `perl -pi`
  for macOS/Linux portability (BSD `sed -i` differs from GNU).
