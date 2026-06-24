# Provenship Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or
> superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open-source Rudy's private `/rudys-workflow` as **Provenship** — a self-contained,
installable Claude Code plugin (`github.com/RudreshNarwal/provenship`, MIT).

**Architecture:** A plugin repo with `skills/provenship/` (the ported workflow) plus 12 vendored
MIT skills (11 from superpowers + karpathy-guidelines) with their namespaces rewritten to
`provenship:`. gstack cannot be vendored (1 GB Bun/TS product) → declared dependency, gated by a
Phase-0 preflight + bundled installer. Full launch kit: README, CI namespace-linter, sync script,
CONTRIBUTING, example report.

**Tech Stack:** Markdown skills, JSON plugin manifests, Python 3 (cost-table.py), Bash (scripts),
GitHub Actions (lint CI).

**Vendor closure (verified):** brainstorming, writing-plans, test-driven-development,
subagent-driven-development, executing-plans, requesting-code-review, receiving-code-review,
systematic-debugging, verification-before-completion, finishing-a-development-branch,
using-git-worktrees (transitively referenced), + karpathy-guidelines. Only un-vendored refs left:
`elements-of-style:writing-clearly-and-concisely` (optional, stays) and gstack `/...` +
`frontend-design` (preflight-gated).

**Constraint:** NO changes to the operator repo or to `~/.claude/skills/rudys-workflow/`. All work
in `/Users/rudy/dev/provenship/`.

---

### Task 1: Vendor the 12 skills + rewrite namespaces

**Files:** Create `skills/<name>/**` for all 12 skill dirs.

- [ ] Copy 11 superpowers skill dirs (incl. using-git-worktrees) from the 5.1.0 plugin cache and
      karpathy-guidelines from the 1.0.0 cache into `skills/`.
- [ ] Rewrite refs in every vendored file: `superpowers:` → `provenship:`,
      `andrej-karpathy-skills:karpathy-guidelines` → `provenship:karpathy-guidelines`.
      Leave `elements-of-style:` refs untouched (optional, not vendored).
- [ ] **Verify:** `grep -rE "superpowers:|andrej-karpathy-skills:" skills/` returns nothing; every
      `provenship:<x>` ref resolves to a vendored dir.

### Task 2: Port the main provenship skill

**Files:** Create `skills/provenship/SKILL.md`, `skills/provenship/cost-table.py`.

- [ ] Copy rudys-workflow SKILL.md → frontmatter `name: provenship`; triggers-only description
      (`/provenship`, "run provenship", end-to-end requirement). No workflow summary in description.
- [ ] `superpowers:` / `andrej-karpathy-skills:` refs → `provenship:`.
- [ ] Add **Phase 0 — Preflight**: verify gstack installed (`~/.claude/skills/gstack/` or `/qa`
      resolvable) and `frontend-design` available; if missing, print install (scripts/install-gstack.sh)
      and STOP.
- [ ] Replace `python3 ~/.claude/skills/rudys-workflow/cost-table.py` with a path-agnostic
      instruction (run cost-table.py from this skill's own directory).
- [ ] Copy cost-table.py verbatim (already path-independent — uses `Path.cwd()` for project dir).
- [ ] **Verify:** `grep -ri "rudy" skills/provenship/` returns nothing; `python3 -m py_compile`
      on cost-table.py passes.

### Task 3: Plugin manifests, license, provenance

**Files:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `LICENSE`,
`licenses/superpowers.LICENSE`, `licenses/karpathy-skills.LICENSE`, `VENDORED.md`.

- [ ] plugin.json: name provenship, version 0.1.0, MIT, author RudreshNarwal, homepage/repo URLs.
- [ ] marketplace.json: owner RudreshNarwal, one plugin entry `source: "./"`.
- [ ] LICENSE: MIT, Copyright (c) 2026 Rudresh Narwal.
- [ ] licenses/: preserve upstream MIT notices (Jesse Vincent / forrestchang).
- [ ] VENDORED.md: per-skill table — upstream repo, version, date (2026-06-13), license.
- [ ] **Verify:** `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('.claude-plugin/*.json')]"`.

### Task 4: Scripts

**Files:** `scripts/install-gstack.sh`, `scripts/sync-vendored.sh`.

- [ ] install-gstack.sh: check git+bun; clone gstack to `~/.claude/skills/gstack`; run `./setup`;
      idempotent (skip if present, offer upgrade). `set -euo pipefail`.
- [ ] sync-vendored.sh: clone upstream superpowers + karpathy at a ref, copy the 12 skill dirs,
      re-apply namespace rewrite, refresh VENDORED.md date. Parameterized by ref.
- [ ] **Verify:** `bash -n scripts/*.sh` (syntax) passes.

### Task 5: Launch kit

**Files:** `README.md`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.md`,
`.github/workflows/lint.yml`, `docs/example-report/README.md` (+ illustrative report).

- [ ] README: pitch, 6-phase flow diagram, both install paths (plugin one-liner + copy skills/),
      Requirements (Claude Code, gstack+Bun, frontend-design optional), autonomy-gate pitch,
      attribution (superpowers/gstack/karpathy with links + licenses).
- [ ] lint.yml: fail if `skills/` contains `superpowers:`/`andrej-karpathy-skills:`; assert every
      `provenship:<x>` ref resolves; `py_compile` cost-table.py; validate JSON manifests.
- [ ] CONTRIBUTING + issue templates.
- [ ] example-report: clearly-labeled illustrative finalize report (NOT a fabricated real run);
      README note that a real captured run should replace it before the public launch tweet.
- [ ] **Verify:** flow diagram phase count matches SKILL.md; install commands use RudreshNarwal/provenship.

### Task 6: Verify + commit

- [ ] Run the lint logic locally (namespace grep + ref-resolution + py_compile + JSON parse).
- [ ] Fix any dangling refs.
- [ ] `.gitignore` (node_modules, .DS_Store). Commit everything.
- [ ] **Verify:** clean `git status`, lint green.

## Out of scope
- Modifying operator repo or local rudys-workflow.
- Vendoring/forking gstack.
- A real recorded demo run (placeholder example report ships; real one is a post-build follow-up).
- Pushing to GitHub / creating the remote repo (done after Rudy reviews locally).
