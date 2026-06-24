# Provenship — Open-Source Design Spec

**Date:** 2026-06-13 · **Author:** Rudresh Narwal (with Claude) · **Status:** Approved

## Goal

Open-source Rudy's private `/rudys-workflow` skill as **Provenship** — a self-contained,
installable Claude Code plugin that drives a feature/bugfix end-to-end:
brainstorm → plan → build (TDD, subagents) → review → browser QA (UI + API) →
evidence-rich finalize (report, screenshots, per-stage cost table) → ship (PR).

The pitch: *"Hand it a requirement, get back a PR with proof."*

## Locked decisions

| Decision | Choice |
|---|---|
| Name | `provenship` (a provenship builds ships — disciplined building that always ends in shipping) |
| Repo | `github.com/RudreshNarwal/provenship` (personal account) |
| License | MIT |
| Distribution | Both: Claude Code plugin (one-command install) AND copy-able `skills/` folder |
| Dependencies | Vendor superpowers (MIT, Jesse Vincent) + karpathy-guidelines (MIT, forrestchang). gstack CANNOT be vendored (1 GB Bun/TypeScript product with compiled `browse` CLI) → declared dependency with Phase-0 preflight + bundled installer script |
| Scope | Approach 3: full launch kit (CI, sync script, CONTRIBUTING, demo report) |
| Local setup | `~/.claude/skills/rudys-workflow/` stays untouched under its old name |

## Repo layout

```
provenship/
├── .claude-plugin/
│   ├── plugin.json              # name: provenship, MIT, author RudreshNarwal
│   └── marketplace.json         # enables /plugin marketplace add RudreshNarwal/provenship
├── skills/
│   ├── provenship/
│   │   ├── SKILL.md             # the main workflow (ported from rudys-workflow)
│   │   └── cost-table.py
│   ├── brainstorming/           # ┐
│   ├── writing-plans/           # │
│   ├── test-driven-development/ # │
│   ├── subagent-driven-development/  # │ 10 superpowers skills,
│   ├── executing-plans/         # │ vendored + re-namespaced
│   ├── requesting-code-review/  # │
│   ├── receiving-code-review/   # │
│   ├── systematic-debugging/    # │
│   ├── verification-before-completion/ # │
│   ├── finishing-a-development-branch/ # ┘
│   └── karpathy-guidelines/     # vendored from andrej-karpathy-skills
├── scripts/
│   ├── install-gstack.sh        # installs the one un-vendorable dependency
│   └── sync-vendored.sh         # re-copy upstream skills + rewrite namespaces
├── licenses/
│   ├── superpowers.LICENSE      # upstream MIT notices (MIT requires preservation)
│   └── karpathy-skills.LICENSE
├── VENDORED.md                  # provenance: upstream repo, version, date, license per skill
├── docs/
│   ├── example-report/          # REAL finalize report + screenshots + cost table (demo)
│   ├── specs/                   # this file
│   └── plans/                   # implementation plan
├── README.md                    # pitch, flow diagram, install (both paths), attribution
├── LICENSE                      # MIT, Copyright (c) 2026 Rudresh Narwal
├── CONTRIBUTING.md
└── .github/
    ├── ISSUE_TEMPLATE/ (bug_report.md, feature_request.md)
    └── workflows/lint.yml       # cross-reference linter + python syntax check
```

## Components

### 1. Main skill (`skills/provenship/SKILL.md`)

Port of `~/.claude/skills/rudys-workflow/SKILL.md` with these changes ONLY (behavior
identical — same 6 phases, autonomy gate, credentials flow, cost tracking):

- Frontmatter `name: provenship`; description triggers updated (`/provenship`,
  "run provenship", plus the end-to-end requirement trigger). Description stays
  triggers-only — never summarize the workflow in it (CSO rule).
- All `superpowers:<skill>` references → `provenship:<skill>` (vendored copies).
- `andrej-karpathy-skills:karpathy-guidelines` → `provenship:karpathy-guidelines`.
- gstack references unchanged (`/qa`, `/browse`, `/autoplan`, `/ship`, …) but gated
  by a new **Phase 0 — Preflight** section: verify gstack is installed
  (`~/.claude/skills/gstack/` exists or `/qa` resolvable); if missing, print
  `scripts/install-gstack.sh` / upstream install instructions and STOP.
  `frontend-design` gets the same preflight check (Anthropic plugin skill, not vendorable).
- `python3 ~/.claude/skills/rudys-workflow/cost-table.py` → run `cost-table.py`
  from this skill's base directory (skills receive their base dir at invocation).
- No other personal references remain (grep for `rudy` must return nothing).

### 2. Vendored skills

- Source of truth for v1: the locally installed copies (superpowers 5.1.0 plugin cache,
  karpathy-skills 1.0.0 plugin cache). VENDORED.md records upstream GitHub repos for
  future syncs.
- Copy each skill directory WHOLE (supporting files like `visual-companion.md` included).
- Rewrite internal cross-references: `superpowers:X` → `provenship:X`.
  References to skills we do NOT vendor (e.g. optional `elements-of-style:…`) stay as-is —
  they are "if available" optional in upstream text.
- Frontmatter `name:` fields stay as upstream (plugin namespace supplies the prefix).

### 3. Cross-reference / namespace policy

- Plugin install (primary path): skills resolve as `provenship:<name>` — unambiguous even
  if the user also has real superpowers installed. No collision: provenship always invokes
  its own namespace; vendored copies are pinned snapshots (documented in VENDORED.md).
- Copy install (secondary path): bare-name resolution applies; if the user has superpowers
  installed, bare names may resolve to their own copies — acceptable (functionally
  equivalent skills). Documented in README.
- CI linter (`.github/workflows/lint.yml`) fails the build if any file under `skills/`
  still contains `superpowers:` or `andrej-karpathy-skills:` references, and runs
  `python3 -m py_compile` on cost-table.py.

### 4. Scripts

- `scripts/install-gstack.sh`: checks for git + Bun, clones/updates gstack into
  `~/.claude/skills/gstack` per upstream instructions, runs its setup. Idempotent.
- `scripts/sync-vendored.sh`: clones upstream superpowers + karpathy-skills repos at a
  given ref, copies the 11 skill dirs in, re-applies the namespace rewrite, refreshes
  VENDORED.md dates. Used for future upstream refreshes; not needed at install time.

### 5. Launch kit

- **README.md** (the marketing asset): one-paragraph pitch; 6-phase flow diagram (ASCII or
  mermaid); install path A (`/plugin marketplace add RudreshNarwal/provenship` →
  `/plugin install provenship`) and path B (clone + copy `skills/` into `~/.claude/skills/`);
  Requirements (Claude Code, gstack + its Bun requirement, frontend-design plugin optional);
  the autonomy-gate pitch; link to the example report; attribution section crediting
  superpowers (Jesse Vincent), gstack (Garry Tan), karpathy-guidelines (forrestchang) with repo links.
- **docs/example-report/**: a real finalize report produced by running the workflow on a
  small sample feature — health score, screenshots, per-stage cost table. Secrets redacted.
- CONTRIBUTING.md + two issue templates.

## Testing (Iron Law — no skill ships untested)

1. Fresh-subagent compliance tests on the ported SKILL.md (same method used for
   rudys-workflow): entry-map scenarios, Phase-0 preflight behavior with gstack
   missing/present, namespace resolution of vendored sub-skills, autonomy gate.
2. CI linter green (no dangling upstream namespaces).
3. Clean-machine install test: add the repo as a local marketplace, install the plugin,
   confirm `provenship` + vendored skills appear and `/provenship` triggers.
4. `cost-table.py` smoke test against a synthetic transcript (existing test approach).

## Out of scope

- Renaming or modifying the local `~/.claude/skills/rudys-workflow/` (explicitly excluded).
- Vendoring or forking gstack.
- Demo GIF/video (nice-to-have after launch; placeholder section in README).
- Auto-update mechanism for vendored skills (manual `sync-vendored.sh` is enough).
