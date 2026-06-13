---
name: shipwright
description: Use when the user invokes /shipwright, says "run shipwright", "ship this end-to-end", or "run my pipeline", or hands over a feature/bugfix requirement to be driven end-to-end without further supervision.
---

# Shipwright

## Overview

An end-to-end development pipeline that orchestrates existing skills in a fixed order, closing with
an evidence-rich Finalize (report + screenshots + per-stage cost table + credentials gate) and a ship.

**Run the phases in order.** Each phase delegates to another skill — *invoke that skill*, let it
finish, then move on. Do not paraphrase a phase instead of invoking its skill. Skip a phase's
*content* only when it genuinely doesn't apply, never the order.

## When to use

- `/shipwright`, "run shipwright", "ship this end-to-end", "run my pipeline".
- Any non-trivial feature or bugfix you want driven through the full disciplined sequence.
- Skip for trivial one-liners or pure questions.

## Entry map

Don't redo phases whose output already exists. Artifacts in repo conventions (e.g. `.context/plans/`,
`docs/superpowers/specs/`) count.

| User already has | Enter at |
|---|---|
| Just a requirement | Phase 1 |
| Approved spec / design doc | Phase 2 |
| Implementation plan | Phase 3 |
| Finished code needing checks | Phase 4 |

## Phase 0 — Preflight (run once, before anything)

Shipwright bundles its superpowers and karpathy sub-skills (vendored under `shipwright:`), but the
browser-QA and ship phases call **gstack**, which is a separate product and cannot be bundled.
Before starting, verify the external dependencies:

- **gstack** — required for Phases 5–6 (`/qa`, `/qa-only`, `/browse`, `/design-review`, `/autoplan`,
  `/ship`, `/setup-browser-cookies`). Check it's installed (e.g. `~/.claude/skills/gstack/` exists,
  or `/qa` resolves). Missing → tell the user to run `scripts/install-gstack.sh` from this repo (or
  the one-liner in the README) and STOP until it's installed.
- **frontend-design** — required only if the work touches `web/` / UI. It's an Anthropic plugin
  skill, not bundled. Missing and the task is frontend → tell the user to install it and STOP;
  backend-only task → continue.

If the dependency is genuinely unavailable and cannot be installed (e.g. no network in a sandbox),
say so plainly and stop — do not silently skip QA or ship.

## Discipline — applies to every phase

**INVOKE `shipwright:karpathy-guidelines` at workflow start** (whatever the entry point) so the full
rules are in context — the summary below is a reminder, not a substitute.

- **Don't assume.** State assumptions explicitly. Multiple interpretations → present them, never pick
  silently. Unclear → stop, name what's confusing, ask. Autonomous runs: batch ALL questions in
  Phase 1; record any remaining assumptions in the finalize report.
- **Simplicity first.** Minimum code that solves the problem. Nothing speculative.
- **Surgical changes.** Touch only what the task requires. Mention unrelated issues; don't fix them.
- **Goal-driven.** Every phase ends with its Verify check — apply
  `shipwright:verification-before-completion` (show evidence, never claim done without it). Don't
  advance until it passes.
- **Bugs get root-caused.** Any test failure or bug you can't explain at a glance (in Build or QA) →
  `shipwright:systematic-debugging`. No guess-fixes.

## Autonomy gate (asked once, right after Phase 1)

When the spec is approved, ask one batched question with two parts:

1. **"Run the rest autonomously?"**
2. **"QA login credentials?"** — email + password + display name for the app under test, if QA
   will hit authenticated pages. Leave blank → a test account will be self-registered (see
   Credentials).

- **No** → interactive mode: each sub-skill's natural checkpoints apply, as usual.
- **Yes** → autonomous mode: zero further questions to the user until the run ends. At every
  decision point, take the recommended default:

| Decision point | Autonomous default |
|---|---|
| Plan review (P2) | `/autoplan`; accept its recommended options at its final gate |
| Build mode (P3) | subagent-driven; `executing-plans` if ≤3 sequential tasks |
| Mid-run ambiguity | safer interpretation, logged in the finalize report |
| Second opinions (P4) | skip `/codex`; `requesting-code-review` stays mandatory |
| QA bugs (P5) | fix all; defer only with a logged reason |
| Missing QA credentials | env / creds file / gate answer; else self-register a test account (non-prod only); signup impossible → STOP and report |
| Soft gate fails (P6) | STOP and report — never ship failures autonomously |
| Close-out (P6) | `/ship` → PR (never merge the main branch directly) |

Autonomous mode removes *questions to the user*, not harness permissions — pair it with a scoped
`.claude/settings.json` allowlist (see Running automatically) or tool prompts will still interrupt.

## Phases (run in order)

**Before each phase's work, record a stage marker** (see Cost tracking).

1. **Brainstorm** — invoke `shipwright:brainstorming`. Ask everything needed up-front, in one
   batch. *Verify:* spec written at `docs/superpowers/specs/YYYY-MM-DD-<topic>.md` (or the repo's
   convention) and approved. Then ask the **Autonomy gate** question (below).
2. **Plan** — invoke `shipwright:writing-plans` to produce the plan file, then review the plan:
   autonomous mode → gstack `/autoplan` (runs the CEO/design/eng/DX review lenses over the plan
   with auto-decisions and hardens it; accept its recommendations at its final gate); interactive
   mode → the user reviews, invoking `/autoplan` or individual `/plan-*-review` skills only on
   request. *Verify:* plan file exists with independently executable tasks.
3. **Build** — invoke `shipwright:subagent-driven-development` for ALL implementation (tiny plan of
   2–3 sequential tasks → `shipwright:executing-plans` in-session instead). Within it:
   - Every task follows `shipwright:test-driven-development`. Repo has no test runner → bootstrap a
     minimal one for the new code (e.g. pytest for Django, vitest for Vue; smoke-level is enough).
     Only if setup would dwarf the feature itself, record an explicit no-harness exception that
     Finalize must surface.
   - Frontend tasks (components, pages, styling, `web/`) also invoke `frontend-design`.
   - **Every subagent prompt MUST embed the karpathy discipline** — fresh subagents don't inherit
     this context. Tell each implementer: state your assumptions in your report; if the task is
     ambiguous, return the question instead of guessing; minimum code; touch only what the task
     names. Treat a subagent report with unstated assumptions as a failed spec review.
   *Verify:* all plan tasks complete, tests green.
4. **Review** — invoke `shipwright:requesting-code-review`; act on findings via
   `shipwright:receiving-code-review`. Optionally gstack `/review` or `/codex` for a second
   opinion. *Verify:* blocking findings fixed.
5. **QA — browser, UI AND API** — invoke gstack `/qa` (test-and-fix loop) against the running dev
   server. Mandatory on top of `/qa` defaults:
   - **API verification:** after each key flow (any user action expected to trigger a request —
     submit, save, load, delete), run `browse network` — confirm the expected XHR/fetch calls fired
     and returned 2xx. A clean-looking UI with missing or failing calls is a bug.
   - `browse console --errors` after every interaction.
   - Frontend work → also invoke gstack `/design-review` (visual/theme consistency vs the app's design system).
   - Resolve credentials here (see Credentials).
   *Verify:* health score recorded; every bug fixed or explicitly deferred with reason.
6. **Finalize + Ship** — run Enhanced Finalize below.

**REQUIRED SUB-SKILLS:** `shipwright:brainstorming`, `shipwright:writing-plans`,
`shipwright:test-driven-development`, `shipwright:subagent-driven-development`,
`shipwright:requesting-code-review`, `shipwright:receiving-code-review`,
`shipwright:executing-plans`, `shipwright:systematic-debugging`,
`shipwright:verification-before-completion`, `shipwright:finishing-a-development-branch`,
`shipwright:karpathy-guidelines`, `frontend-design`, and gstack `/qa`, `/qa-only`,
`/browse`, `/design-review`, `/autoplan`, `/ship`, `/setup-browser-cookies`.

## Phase 6 — Enhanced Finalize

Goal: durable proof the branch was checked thoroughly, then ship.

1. **Summary** — build a task-done summary from `git diff` / commits vs the base branch.
2. **Evidence** — invoke gstack `/qa-only` (report-only; phase 5 already fixed bugs) and `/browse` to
   capture screenshots of key pages/flows into `docs/finalize/assets/<branch>/`, plus one
   `browse network` capture of the core flow (proof the API layer was checked).
   - Non-web repo / no app URL → skip browser steps, run the detected unit-test runner, note "no UI to screenshot."
3. **Report** — write `docs/finalize/YYYY-MM-DD-<branch>.md` containing: task-done summary; test + QA
   results (health score, pass/fail, issues); embedded screenshots (relative links); assumptions made
   during the run; any no-harness exception; a "checked thoroughly" statement backed by the evidence;
   and the per-stage cost table (below).
4. **Soft gate** — tests failed, QA health low, or a no-harness exception exists → surface it
   prominently and require the user's explicit confirmation before shipping. Override allowed. Clean → proceed.
5. **Commit** the report + screenshots to the branch (NEVER credentials), then **ship**: invoke
   gstack `/ship` (merge base, tests, version/changelog when present, push, PR). If the user instead
   wants a local merge or to discard the branch, invoke `shipwright:finishing-a-development-branch`.
   Never run both — they both want to own the PR step.

## Credentials (resolve at the Autonomy gate)

Needed when QA must test authenticated pages. Resolution order:

1. Env vars or the gitignored `.claude/finalize-creds.json` → use silently.
2. What the user provided at the Autonomy gate (email + password + display name). Offer to save
   it to `.claude/finalize-creds.json` for next time.
3. Nothing provided → **self-register a test account**: sign up through the app's register flow
   (or its auth API) with a generated display name, email, and strong password; save the creds to
   `.claude/finalize-creds.json`; then log in and run QA with it.
   - Self-register ONLY against local/dev/staging targets — NEVER against production.
   - Signup disabled, or email verification you cannot complete → interactive: ask the user (or
     gstack `/setup-browser-cookies`); autonomous: STOP and report.

- Ensure `.claude/finalize-creds.json` and `.claude/finalize-stages.jsonl` are in `.gitignore`.
- NEVER write credentials into the report, logs, or git. Redact secrets.

## Cost tracking (per-stage token & price table)

No per-phase cost API exists, so attribute it from session transcripts:

1. At the **start of each phase**, append a line to `.claude/finalize-stages.jsonl`:
   `{"stage": "<n. name>", "ts": "<ISO8601 now>"}` (one JSON object per line).
2. At Finalize, run `cost-table.py` from this skill's own directory (the same folder as this
   SKILL.md), e.g. `python3 "$(dirname "$0")"/cost-table.py` or just point Python at the
   `cost-table.py` next to this file. It scans the project's session transcripts under
   `~/.claude/projects/<project>/` (all sessions since the first marker — resumed/compacted
   sessions included), buckets usage into stage windows, applies the pricing table, and prints a
   markdown table to paste into the report.
3. Pricing is **best-effort** — keep the rates in the script current, or pass `--ccusage` if
   installed. Sanity-check the total against `/cost`.

## Running automatically

- **Interactive (default):** follow each sub-skill's natural checkpoints.
- **Headless back-half** (after a plan exists): run with a scoped `.claude/settings.json` allowlist:
  `claude -p "Run /shipwright from the plan in <file>"`. Use `--dangerously-skip-permissions`
  only as a last resort in a sandboxed/throwaway environment. Wrap with `/loop` or `/schedule` to recur.

## Common mistakes

- Summarizing the workflow instead of invoking each sub-skill — invoke them; don't paraphrase.
- Skipping Phase 0 preflight, then hitting a wall at Phase 5 because gstack isn't installed.
- Redoing a phase whose artifact already exists (see Entry map) — enter at the right phase.
- Silently picking one interpretation of an ambiguous requirement — present options or ask.
- UI-only QA: screenshots look fine while the API returns 4xx/5xx — `browse network` is mandatory.
- Forgetting a stage marker → the cost table loses that phase.
- Running `/qa` (fix loop) in Finalize instead of `/qa-only` → Finalize must not mutate code.
- Running both `/ship` and `finishing-a-development-branch` → pick one.
- Committing credentials → never; only the report + screenshots get committed.
- Skipping the soft-gate confirmation when QA failed or tests were absent → always surface before shipping.
- Asking the user questions mid-run in autonomous mode — the only valid stops are missing
  credentials and a failed soft gate.
- Dispatching implementer subagents without the karpathy rules in their prompt — subagents
  assume silently unless told to surface assumptions.
- Shipping over a failed soft gate in autonomous mode → STOP and report instead.
- Self-registering a test account against a production URL → local/dev/staging only.
