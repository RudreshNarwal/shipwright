<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img alt="Shipwright — hand it a requirement, get back a PR with proof" src="assets/logo-light.svg" width="460">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-22C55E.svg"></a>
  <a href="https://github.com/RudreshNarwal/shipwright/actions/workflows/lint.yml"><img alt="CI" src="https://github.com/RudreshNarwal/shipwright/actions/workflows/lint.yml/badge.svg"></a>
  <img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-0EA5A0.svg">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-0F172A.svg">
</p>

Shipwright is a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that drives a
feature or bugfix through a disciplined, end-to-end pipeline — brainstorm, plan, build with TDD,
review, browser QA that checks the UI *and* the real API calls, an evidence-rich finalize report
(screenshots + per-stage cost table), and a shipped pull request. It can run interactively, or
**fully autonomously** from a single requirement after one approval.

It's an orchestrator: each phase invokes a battle-tested skill and waits for it to finish. The
discipline comes from [Andrej Karpathy's rules for LLM coding](https://x.com/karpathy/status/2015883857489522876)
— *don't assume, simplicity first, surgical changes, goal-driven* — propagated into every phase and
every subagent prompt.

---

## The pipeline

```
requirement
    │
    ▼
[0] Preflight ──── verify gstack is installed (superpowers + karpathy + frontend-design are bundled)
    │
    ▼
[1] Brainstorm ─── shipwright:brainstorming → approved spec          ◀─┐
    │              └─▶ Autonomy gate: "run autonomously?" + QA creds   │
    ▼                                                                  │ re-scope
[2] Plan ───────── shipwright:writing-plans (+ /autoplan when auto)  ◀─┤
    │                                                                  │ re-plan / re-design
    ▼                                                                  │
[3] Build ──────── shipwright:subagent-driven-development · TDD · shipwright:frontend-design for UI
    │              karpathy discipline embedded in every subagent prompt
    ▼                                                                  │
[4] Review ─────── shipwright:requesting-code-review + receiving-code-review (+ /review, /codex)
    │                                                                  │
    ▼                                                                  │
[5] QA ─────────── gstack /qa · browse network (API 2xx) · console --errors · /design-review
    │              └─ finding bigger than a local fix? escalate ───────┘
    │                 (interactive: confirm first · autonomous: auto, scope-change stops)
    ▼
[6] Finalize ───── report + screenshots + per-stage cost table → soft gate → gstack /ship → PR
    │
    ▼
   PR with proof
```

Already have a spec or a plan? Shipwright's **entry map** starts you at the right phase instead of
redoing finished work.

## Why it's different

- **API-level QA, not just screenshots.** Phase 5 runs `browse network` after every key flow — a
  pretty UI that silently 4xx/5xx's is a bug, and Shipwright catches it.
- **Evidence, not vibes.** Every run ends with a committed finalize report: health score,
  screenshots, the assumptions it made, and a per-stage token/cost table.
- **Autonomous when you want it.** Answer one question after brainstorming and it runs to a PR with
  zero further prompts, taking the safer interpretation at each fork and logging it.
- **Discipline that survives subagents.** Fresh subagents inherit no context, so the "don't assume"
  rules are injected into each implementer prompt — unstated assumptions are treated as a failed review.

## Install

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) ·
[gstack](https://github.com/garrytan/gstack) (used in Phases 5–6; needs [Bun](https://bun.sh/) v1.0+) ·
[`frontend-design`](https://docs.anthropic.com/en/docs/claude-code) plugin skill (only for UI work).

### Option A — plugin (recommended)

```
/plugin marketplace add RudreshNarwal/shipwright
/plugin install shipwright
```

Then install the one dependency that can't be bundled (gstack) — see
[Installing gstack manually](#installing-gstack-manually) below, or run
`scripts/install-gstack.sh` from a clone of this repo.

### Option B — copy the skills

```bash
git clone https://github.com/RudreshNarwal/shipwright.git
cp -R shipwright/skills/* ~/.claude/skills/
bash shipwright/scripts/install-gstack.sh
```

### Installing gstack manually

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && (cd ~/.claude/skills/gstack && ./setup)
```

Phase 0 checks for these before doing anything and stops with instructions if they're missing.

## Usage

```
/shipwright
```

…or just hand Claude a requirement and say "run this end-to-end with shipwright." After the spec is
approved you'll be asked once whether to continue autonomously and for any QA login credentials
(leave blank and it self-registers a throwaway test account against non-prod targets).

See [`docs/example-report/`](./docs/example-report/) for a template of the report Phase 6 produces.

## What's bundled

Shipwright vendors a pinned, permissively-licensed snapshot of the skills it orchestrates (all MIT,
plus one Apache-2.0 skill — `frontend-design`), so it installs as one self-contained plugin. gstack is
the exception — it's a separate product you install once. Full provenance and versions are in
[`VENDORED.md`](./VENDORED.md).

## Credits

Shipwright stands on the shoulders of four excellent open-source projects:

- **[superpowers](https://github.com/obra/superpowers)** by Jesse Vincent (MIT) — brainstorming,
  planning, TDD, subagent-driven development, code review, debugging, verification.
- **[gstack](https://github.com/garrytan/gstack)** by Garry Tan (MIT) — the browser QA, design
  review, autoplan, and ship tooling.
- **[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)** by forrestchang
  (MIT) — the behavioral guidelines that anchor the discipline.
- **[frontend-design](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design)**
  by Anthropic (Apache-2.0) — the frontend design skill used for UI work.

## License & attribution

Shipwright itself is **MIT © 2026 Rudresh Narwal**.

It bundles, verbatim and version-pinned, skills under two permissive licenses — **MIT** (superpowers,
andrej-karpathy-skills) and **Apache-2.0** (`frontend-design`, © Anthropic). Each upstream's full
license text is preserved in [`licenses/`](./licenses/), and provenance is documented in
[`VENDORED.md`](./VENDORED.md). The Apache-2.0 skill remains under Apache-2.0; bundling it does not
relicense it.

> **Not affiliated with Anthropic.** "Claude" and "Claude Code" are trademarks of Anthropic.
> Shipwright is an independent, community plugin *for* Claude Code — it is not built, owned, or
> endorsed by Anthropic.
