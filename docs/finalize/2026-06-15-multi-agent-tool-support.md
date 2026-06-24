# Finalize Report — Multi-harness install adapters (Codex + OpenCode)

**Branch:** `RudreshNarwal/multi-agent-tool-support` · **Base:** `main` · **Date:** 2026-06-15

## Task-done summary

Make Provenship (previously a Claude-Code-only plugin) **installable on Codex and OpenCode**, scoped
to lightweight install adapters that reuse the existing `skills/` — no skill-body changes — with an
honest capability matrix in the README. Pi/Gemini adapters, IDE rule files, and any port of the
gstack QA/ship phases or `cost-table.py` were explicitly out of scope (confirmed with the user).

### Changes (diff vs `main`)

| File | Change |
|---|---|
| `.codex-plugin/plugin.json` *(new)* | Codex manifest mirroring `.claude-plugin/plugin.json` + `"skills": "./skills/"` + an `interface` block (displayName, capabilities, default prompts, icon). |
| `opencode.json` *(new)* | OpenCode config pointing at the plugin below. |
| `.opencode/plugins/provenship.mjs` *(new)* | Thin OpenCode plugin: on `session.created` runs `scripts/preflight-gstack.sh` and surfaces its output — gstack-preflight parity with the Claude Code SessionStart hook. Injects **no** ruleset (Provenship has none). |
| `README.md` | "Other harnesses — Codex & OpenCode" install section; **capability matrix**; corrected the FAQ that wrongly said Codex lacks a skill+subagent model. |
| `scripts/lint.sh` | JSON-validity check extended to the two new manifests; added a `node --check` for the `.mjs`, guarded to skip when `node` is absent. |
| `CLAUDE.md` | Repo-layout map updated with the three new paths. |

## Test + QA results

- **Lint suite (`bash scripts/lint.sh`): 6/6 PASS.** Includes the two new checks: new manifests are
  valid JSON (check 4) and the OpenCode plugin parses via `node --check` (check 6).
- **Manifest validity:** `.codex-plugin/plugin.json` and `opencode.json` both parse as valid JSON;
  `.codex-plugin/plugin.json`'s `composerIcon`/`logo` reference `./assets/icon.svg`, which exists.
- **Browser QA: N/A.** This repo is a plugin/skills package with no web app or dev server, so the
  workflow's browser phases (`/qa`, `browse network`, `/design-review`) do not apply ("no UI to
  screenshot"). The lint suite + manifest validity is the standing verification for a packaging change.
- **Code review:** a Senior-Code-Reviewer subagent reviewed the full working-tree diff. Verdict:
  *With fixes* — **no Critical issues**. Three Important + one Minor finding, all
  documentation/clarity honesty items, were applied:
  1. Removed a dead `session.start` event clause in the `.mjs` (OpenCode's real event is
     `session.created`); behavior unchanged, correctness/clarity improved.
  2. Softened the README FAQ from "adapters install cleanly" → "are provided but unverified
     end-to-end" (the Codex install path has not been executed).
  3. Corrected `CLAUDE.md` which over-claimed the Codex manifest wires `hooks/` (it wires `skills/`;
     the hook is trusted via Codex's `/hooks`).
  4. Hedged the README claim that OpenCode auto-discovers `skills/` (marked unverified).
  Two minors (stdout `console.log`; relative plugin path) were left as-is — both reviewer-acceptable;
  changing them would mean speculative work against an unverified API (rejected on simplicity grounds).

## Assumptions made during the run

- **Codex manifest schema is best-effort**, modeled on a known-good public example (`ponytail`'s
  `.codex-plugin/plugin.json`). The `interface` field names were not validated against an
  authoritative Codex schema.
- **OpenCode plugin API** (`export default async () => ({ event })`, `session.created`) was modeled on
  current OpenCode docs and the reviewer's verification of the event list, but not executed in a live
  OpenCode instance.
- The remote `git@github.com:RudreshNarwal/provenship.git` exists and accepts PRs (the CLAUDE.md note
  saying "remote does not exist yet" is stale — PRs #1–#3 are already merged).

## Checked thoroughly

The change is a small, surgical packaging addition. Every changed line traces to the requirement;
no `skills/` bodies or vendored skills were touched (`git status` confirms). It was put through code
review (no Critical findings; all Important findings fixed) and the full lint suite passes 6/6 with
the two new manifest checks. The honest limits are documented below and in the README capability
matrix rather than hidden.

### Known limitation / follow-up (not a blocker)

The adapters are **unverified end-to-end** — verifying them requires Codex and OpenCode installed,
which isn't possible in this environment. Documented manual steps to close this:
- **Codex:** `codex plugin marketplace add <clone>` → `/plugins` install → `/hooks` trust the
  SessionStart hook → confirm `provenship` + vendored skills load; confirm `${CLAUDE_PLUGIN_ROOT}`
  resolves in `hooks/hooks.json` (if not, make the hook path portable).
- **OpenCode:** run from a checkout with `opencode.json` present → confirm the plugin loads, the
  gstack preflight prints on session start, and `skills/` are discoverable.

This is inherent to the chosen scope ("lightweight adapters") and is surfaced, not a no-test-harness
exception — the testable surface (JSON validity + JS parse) is covered by lint.

## Per-stage cost table

> Markers were recorded from Phase 4 onward (the brainstorm/plan/build front half ran in plan mode
> before workflow invocation, so it isn't separately bucketed). Best-effort pricing; sanity-check
> against `/cost`.

| Stage | Model | Input | Output | Cache read | Cache write | Cost (USD) |
|---|---|---|---|---|---|---|
| 4. Review | opus-4-8 | 87,591 | 123,715 | 7,269,748 | 379,859 | $9.54 |
| 6. Finalize | opus-4-8 | 2 | 1,520 | 116,570 | 339 | $0.10 |
| **Total** | | **87,593** | **125,235** | **7,386,318** | **380,198** | **$9.64** |
