---
name: provenship
description: Use when the user invokes /provenship, says "run provenship", "ship this end-to-end", or "run my pipeline", or hands over a feature/bugfix requirement to be driven end-to-end without further supervision.
---

# Provenship

## Overview

An end-to-end development pipeline that orchestrates existing skills in a fixed order, closing with
an evidence-rich Finalize (report + screenshots + per-stage cost table + credentials gate) and a ship.

**Run the phases in order.** Each phase delegates to another skill — *invoke that skill*, let it
finish, then move on. Do not paraphrase a phase instead of invoking its skill. Skip a phase's
*content* only when it genuinely doesn't apply, never the order.

## When to use

- `/provenship`, "run provenship", "ship this end-to-end", "run my pipeline".
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

Provenship bundles its superpowers, karpathy, and frontend-design sub-skills (vendored under
`provenship:`), but the browser-QA and ship phases call **gstack**, which is a separate product and
cannot be bundled. Before starting, verify the external dependency:

- **gstack** — required for Phases 5–6 (`/qa`, `/qa-only`, `/browse`, `/design-review`, `/autoplan`,
  `/ship`, `/setup-browser-cookies`; optional-use: `/office-hours` in Phase 1). A SessionStart hook (`hooks/hooks.json` →
  `scripts/preflight-gstack.sh`) already auto-detects it at session start and, when missing, prints the
  install command (or background-installs it if `PROVENSHIP_AUTO_INSTALL_GSTACK=1`). Re-check here
  (e.g. `~/.claude/skills/gstack/` exists, or `/qa` resolves); still missing → tell the user to run
  `scripts/install-gstack.sh` (it bootstraps Bun + gstack + Playwright) and STOP until it's installed.
- **frontend-design** — required only for `web/` / UI work, and it's now **bundled** (vendored under
  `provenship:frontend-design`), so there is nothing to install for UI work.

If the dependency is genuinely unavailable and cannot be installed (e.g. no network in a sandbox),
say so plainly and stop — do not silently skip QA or ship.

## Discipline — applies to every phase

**INVOKE `provenship:karpathy-guidelines` at workflow start** (whatever the entry point) so the full
rules are in context — the summary below is a reminder, not a substitute.

- **Don't assume.** State assumptions explicitly. Multiple interpretations → present them, never pick
  silently. Unclear → stop, name what's confusing, ask. Autonomous runs: batch ALL questions in
  Phase 1; record any remaining assumptions in the finalize report.
- **Simplicity first.** Minimum code that solves the problem. Nothing speculative.
- **Surgical changes.** Touch only what the task requires. Mention unrelated issues; don't fix them.
- **Goal-driven.** Every phase ends with its Verify check — apply
  `provenship:verification-before-completion` (show evidence, never claim done without it). Don't
  advance until it passes.
- **Bugs get root-caused.** Any test failure or bug you can't explain at a glance (in Build or QA) →
  `provenship:systematic-debugging`. No guess-fixes.

## Autonomy gate (asked once, right after Phase 1)

When the spec is approved, ask one batched question with two parts:

1. **"Run the rest autonomously?"**
2. **"QA login credentials?"** — three ways to authenticate the app under test, if QA will hit
   authenticated pages: (a) email + password + display name, (b) **import cookies from your real
   browser** → runs gstack `/setup-browser-cookies`, or (c) leave blank → a test account is
   self-registered (see Credentials).

- **No** → interactive mode: each sub-skill's natural checkpoints apply, as usual.
- **Yes** → autonomous mode: zero questions to the user from here to the end of the run — including
  the close-out, which ships **and** merges without confirmation. The only stops are the hard ones
  below (missing credentials that can't be resolved, a failed soft gate, a product/scope flaw) —
  i.e. only when input is genuinely required or something is off. At every decision point, take the
  recommended default:

| Decision point | Autonomous default |
|---|---|
| Plan review (P2) | `/autoplan`; accept its recommended options at its final gate |
| Build mode (P3) | subagent-driven; `executing-plans` if ≤3 sequential tasks |
| Mid-run ambiguity | safer interpretation, logged in the finalize report |
| Second opinions (P4) | skip `/codex`; `requesting-code-review` stays mandatory |
| QA local bug (P5) | fix all in place; defer only with a logged reason |
| QA architecture/design re-plan (P5, same scope) | auto loop-back via `/autoplan`, re-build the affected slice, re-QA; logged in the report |
| QA product/scope flaw (P5) | **STOP and surface** — never silently re-scope (see Phase 5 triage) |
| Missing QA credentials | env / creds file / gate answer; else self-register a test account (non-prod only); signup impossible → STOP and report |
| Soft gate fails (P6) | STOP and report — never ship failures autonomously |
| Close-out (P6) | `/ship` → PR, then `/land-and-deploy` — merge into the base branch this work was branched from (`dev`/`develop`/`main`/`master` — name it) and verify the deploy, **without confirmation**. Stop only if `/ship`, CI, or the deploy fails (something is off). |

Autonomous mode removes *questions to the user*, not harness permissions — pair it with a scoped
`.claude/settings.json` allowlist (see Running automatically) or tool prompts will still interrupt.

## Phases (run in order)

**Before each phase's work, record a stage marker** (see Cost tracking).

1. **Brainstorm** — requirement is a raw, unvalidated product idea (not yet a defined feature) and
   gstack is installed → run gstack `/office-hours` first (startup or builder mode) to pressure-test
   what's worth building; skip it when the requirement is already defined. Then invoke
   `provenship:brainstorming`. Ask everything needed up-front, in one
   batch. *Verify:* spec written at `docs/superpowers/specs/YYYY-MM-DD-<topic>.md` (or the repo's
   convention) and approved. If the approved spec still feels under-refined — open design decisions,
   fuzzy edges — don't carry it forward raw: flag it so Phase 2 runs `/autoplan` to harden the plan
   (interactive mode included). Then ask the **Autonomy gate** question (below).
2. **Plan** — invoke `provenship:writing-plans` to produce the plan file, then review the plan:
   autonomous mode → gstack `/autoplan` (runs the CEO/design/eng/DX review lenses over the plan
   with auto-decisions and hardens it; accept its recommendations at its final gate); interactive
   mode → the user reviews, invoking `/autoplan` or individual `/plan-*-review` skills on request —
   but when the plan needs hardening (thin, many open decisions, or flagged shaky from Phase 1),
   offer `/autoplan` in one line and run it. *Verify:* plan file exists with independently
   executable tasks.
3. **Build** — invoke `provenship:subagent-driven-development` for ALL implementation (tiny plan of
   2–3 sequential tasks → `provenship:executing-plans` in-session instead). Within it:
   - Every task follows `provenship:test-driven-development`. Repo has no test runner → bootstrap a
     minimal one for the new code (e.g. pytest for Django, vitest for Vue; smoke-level is enough).
     Only if setup would dwarf the feature itself, record an explicit no-harness exception that
     Finalize must surface.
   - Frontend tasks (components, pages, styling, `web/`) also invoke `provenship:frontend-design`.
   - **Every subagent prompt MUST embed the karpathy discipline** — fresh subagents don't inherit
     this context. Tell each implementer: state your assumptions in your report; if the task is
     ambiguous, return the question instead of guessing; minimum code; touch only what the task
     names. Treat a subagent report with unstated assumptions as a failed spec review.
     - **Run the build ladder BEFORE writing code** (give each implementer this checklist; stop at
       the first rung that answers the task): (1) **Does this need to exist at all?** — if not,
       don't build it. (2) **Is it in the stdlib?** (3) **Is it a native platform feature?** (4) **Is
       it already installed** — an existing dependency or repo util? (5) **Can it be one line?**
       (6) **Only then** write the minimal working solution. Never trade away security,
       accessibility, or data-loss safety to climb a rung — those are not optional.
   *Verify:* all plan tasks complete, tests green.
4. **Review** — invoke `provenship:requesting-code-review`; act on findings via
   `provenship:receiving-code-review`. Optionally gstack `/review` or `/codex` for a second
   opinion. *Verify:* blocking findings fixed.
5. **QA — browser, UI AND API** — invoke gstack `/qa` (test-and-fix loop) against the running dev
   server. Mandatory on top of `/qa` defaults:
   - **API verification:** after each key flow (any user action expected to trigger a request —
     submit, save, load, delete), run `browse network` — confirm the expected XHR/fetch calls fired
     and returned 2xx. A clean-looking UI with missing or failing calls is a bug.
   - `browse console --errors` after every interaction.
   - Frontend work → also invoke gstack `/design-review` (visual/theme consistency vs the app's design system).
   - Resolve credentials here (see Credentials).
   *Verify:* health score recorded; every finding fixed, escalated (below), or explicitly deferred
   with reason.
6. **Finalize + Ship** — run Enhanced Finalize below.

### Phase 5 — Triage & escalation (when a finding is bigger than a local fix)

`/qa` and `/design-review` fix things *in place*. But some findings mean an earlier phase was wrong —
the code is doing what the plan said, and the plan (or the spec) is the problem. Don't band-aid those.
Triage **every** QA finding into one class and take its route:

| Class | Route |
|---|---|
| **Local bug (FE or BE)** — fixable within the current plan/scope | Fix in place via `/qa` loop. Cosmetic visual → `/design-review` in-place fix. (Current behavior.) |
| **Architecture / eng flaw** — fixing it means changing the plan, not just the code | **Loop back to Phase 2** for the affected slice: `provenship:writing-plans` + `/plan-eng-review` (or `/autoplan`), then re-Build (3) → re-Review (4) → re-QA (5) **that slice only**. |
| **Design / UX flaw beyond cosmetic** — the interaction model or layout is fundamentally off | **Loop back to Phase 2** via `/plan-design-review`, then re-Build the affected UI. (Distinct from the in-place `/design-review`.) |
| **Product / scope flaw** — QA shows we built the wrong thing, or the spec itself is wrong | **Loop back to Phase 1** to re-scope via `/plan-ceo-review`. This is a scope change. |

**Who decides — the human-intervention model:**

- **Interactive mode:** any finding that exceeds a local fix → **STOP and ask the user before fixing
  or looping back.** Present the finding, the evidence (the `browse network` / `console --errors`
  capture), and the recommended route. Let them choose: fix-and-loop-back / defer / abandon.
- **Autonomous mode:** automatic — architecture and design re-plans (same scope) loop back through
  `/autoplan` and re-build the affected slice with zero questions. The **one** exception: a genuine
  **product / scope redefinition STOPs and surfaces** to the user (you cannot silently change what the
  product *is* — same spirit as the Phase 6 soft gate and the "don't assume" rule).

**Loop-back discipline:**

- **Surgical** — re-plan / re-build / re-QA only the affected slice, never the whole feature.
- **Bounded** — the *same* finding escalating a second time → STOP regardless of mode, and surface it.
- **Logged** — each loop-back appends a fresh cost-stage marker (e.g.
  `{"stage": "2. Plan (re-entry: QA escalation)", ...}`) to `.claude/finalize-stages.jsonl`, and the
  finalize report records: finding → route taken → what changed.

**REQUIRED SUB-SKILLS:** `provenship:brainstorming`, `provenship:writing-plans`,
`provenship:test-driven-development`, `provenship:subagent-driven-development`,
`provenship:requesting-code-review`, `provenship:receiving-code-review`,
`provenship:executing-plans`, `provenship:systematic-debugging`,
`provenship:verification-before-completion`, `provenship:finishing-a-development-branch`,
`provenship:karpathy-guidelines`, `provenship:frontend-design`, and gstack `/qa`, `/qa-only`,
`/browse`, `/design-review`, `/autoplan`, `/ship`, `/land-and-deploy`, `/setup-browser-cookies`
(optional: `/office-hours`).

## Phase 6 — Enhanced Finalize

Goal: durable proof the branch was checked thoroughly, then ship.

1. **Summary & feature list** — build a task-done summary from `git diff` / commits vs the base branch,
   and **enumerate the discrete features/slices** that were built (from the approved spec/plan). This
   list drives the screenshots and the per-feature report sections below.
2. **Evidence — one screenshot per feature** — invoke gstack `/qa-only` (report-only; Phase 5 already
   fixed bugs) and `/browse` to capture **at least one screenshot per feature**, each demonstrating
   that feature working — 2 features → 2 shots, 5 features → 5 shots — saved to
   `docs/finalize/assets/<branch-slug>/<feature-slug>.png`, plus one `browse network` capture of the core
   flow (proof the API layer was checked). A feature with several flows may have more than one shot;
   never fewer than one per feature. **`<branch-slug>` is the branch name with `/` replaced by `-`**
   (e.g. `feat/login` → `feat-login`) — a raw `/` would nest the report into a subdir and break the
   relative image links. Use the same `<branch-slug>` in the report filename and image links below.
   - Non-web repo / no app URL → skip browser steps, run the detected unit-test runner, and capture the
     feature's CLI/test output instead; note "no UI to screenshot" where genuinely nothing is visual.
3. **Report** — write `docs/finalize/YYYY-MM-DD-<branch-slug>.md` (same `<branch-slug>` as above —
   the report and its `assets/<branch-slug>/` dir must stay siblings under `docs/finalize/`, else the
   relative image links break) with: the **query** (the original
   requirement, verbatim); a one-paragraph overall solution summary; then **one block per feature** —
   *Query* (what was asked for this slice) · *Solution* (what was built) · *Screenshot* (the embedded
   proof image for that feature, as a relative link `assets/<branch-slug>/<feature-slug>.png` — NOT an
   absolute path) · *File changes* (the files touched for it). Follow
   with: test + QA results (health score, pass/fail, issues, any Phase-5 escalations); assumptions made
   during the run; any no-harness exception; a "checked thoroughly" statement backed by the evidence;
   and the per-stage cost table (below). Lead numeric claims with token counts (exact); dollars are
   estimates.
4. **Soft gate** — tests failed, QA health low, or a no-harness exception exists → surface it
   prominently and require the user's explicit confirmation before shipping. Override allowed. Clean → proceed.
5. **Commit & open the PR** — commit the report + screenshots to the branch (NEVER credentials),
   then invoke gstack `/ship` (merge base, tests, version/changelog when present, push, PR). This
   creates the PR; it does **not** merge to main.
6. **Merge into the base branch** this work was branched from. Resolve that base first (the PR's base
   / `/ship`'s detected base — e.g. `dev`, `develop`, `main`, `master`); if the repo's only long-lived
   branch is `main` (or `master`), that is the base. Never merge into a branch other than the one the
   feature was created from. Then merge via gstack `/land-and-deploy` (merge PR into `<base>`, wait for
   CI/deploy, verify production health); for a local merge or no remote, use
   `provenship:finishing-a-development-branch`.
   - **Interactive mode:** present the finalize report + PR link and ask an explicit **"Merge to
     `<base>` now?"**. Yes → merge; No → stop, leave the PR open, report it as awaiting manual merge.
   - **Autonomous mode:** merge automatically — no confirmation. Stop only if a hard gate already
     tripped (failed soft gate, unresolved credentials, product/scope flaw) or `/ship`, CI, or the
     deploy fails.
   `/ship` owns the PR step and `/land-and-deploy` owns the merge step — never hand the same step to
   both, and don't also run `finishing-a-development-branch` when `/land-and-deploy` is doing the merge.

## Credentials (resolve at the Autonomy gate)

Needed when QA must test authenticated pages. Resolution order:

1. Env vars or the gitignored `.claude/finalize-creds.json` → use silently.
2. What the user provided at the Autonomy gate (email + password + display name). Offer to save
   it to `.claude/finalize-creds.json` for next time.
3. User chose **import cookies** at the gate → run gstack `/setup-browser-cookies` to import the
   logged-in session from their real browser, then run QA against that session. (Interactive only —
   the picker needs the user; not available in autonomous mode.)
4. Nothing provided → **self-register a test account**: sign up through the app's register flow
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
  `claude -p "Run /provenship from the plan in <file>"`. Use `--dangerously-skip-permissions`
  only as a last resort in a sandboxed/throwaway environment. Wrap with `/loop` or `/schedule` to recur.

## Common mistakes

- Summarizing the workflow instead of invoking each sub-skill — invoke them; don't paraphrase.
- Skipping Phase 0 preflight, then hitting a wall at Phase 5 because gstack isn't installed.
- Redoing a phase whose artifact already exists (see Entry map) — enter at the right phase.
- Silently picking one interpretation of an ambiguous requirement — present options or ask.
- UI-only QA: screenshots look fine while the API returns 4xx/5xx — `browse network` is mandatory.
- Band-aiding a symptom in QA when the finding means the plan was wrong — triage it and escalate
  (Phase 5 triage table), don't patch around a broken plan.
- Re-running the WHOLE pipeline on a loop-back instead of just the affected slice — escalation is surgical.
- Forgetting a stage marker → the cost table loses that phase.
- Running `/qa` (fix loop) in Finalize instead of `/qa-only` → Finalize must not mutate code.
- Running both `/ship` and `finishing-a-development-branch`, or handing the merge to both
  `/land-and-deploy` and `finishing-a-development-branch` → `/ship` opens the PR, one merger closes it.
- Committing credentials → never; only the report + screenshots get committed.
- Skipping the soft-gate confirmation when QA failed or tests were absent → always surface before shipping.
- Asking the user questions mid-run in autonomous mode — the only valid stops are missing
  credentials that can't be resolved, a failed soft gate, and a product/scope flaw. Autonomous
  mode ships and merges at close-out without asking.
- Merging without the final yes/no gate, or merging into a branch other than the one the work was
  branched from → always ask first, and name the actual base branch in the question.
- Dispatching implementer subagents without the karpathy rules — or the build ladder
  (stdlib / platform / existing-dep / one-line checks before writing) — in their prompt; subagents
  assume silently and over-build unless told otherwise.
- Shipping over a failed soft gate in autonomous mode → STOP and report instead.
- Self-registering a test account against a production URL → local/dev/staging only.
