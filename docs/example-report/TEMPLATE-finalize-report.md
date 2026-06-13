# Finalize report — TEMPLATE

> 📋 **This is a template, not a captured run.** It shows the *shape* of the report Shipwright's
> Phase 6 writes to `docs/finalize/YYYY-MM-DD-<branch>.md`. Every metric below is a `<placeholder>`
> — nothing here is invented or measured. A real run fills these in from actual tests, gstack `/qa`,
> screenshots, and `cost-table.py`.

## Task-done summary

<One paragraph built from `git diff` / commits vs the base branch: what was added or changed, which
files, and the +/- line count. e.g. "Added X to Y — a new `<endpoint>` plus a `<Component>` wired
into `<page>`. N files changed, +A / −B vs `main`.">

## Assumptions logged during the run

- <Each ambiguity hit during the run and the safer interpretation taken — surfaced here, not guessed
  silently.>
- <Anything explicitly ruled out of scope and recorded as a follow-up rather than built.>

## Test results

| Suite | Result |
|---|---|
| `<backend runner, e.g. pytest>` | `<n passed / n failed>` |
| `<frontend runner, e.g. vitest>` | `<n passed / n failed>` |

## QA — UI and API

- **Health score:** `<score>/10` (gstack `/qa`, `<Quick|Standard|Exhaustive>` tier)
- **API verification (`browse network`):** `<METHOD /path>` → `<status>`; … — confirm the expected
  calls fired and returned 2xx. A clean-looking UI with missing or failing calls is a bug.
- **Console:** `<none, or the errors found>` across the key interactions.
- **Design review:** `<pass/fail + notes>` (frontend work only).
- **Escalations (Phase 5 triage):** `<any loop-backs: finding → route taken → outcome, or "none">`

Screenshots: `<assets/...png>`, captured into `docs/finalize/assets/<branch>/`.

## Checked thoroughly

<A short, evidence-backed statement that the branch was exercised end-to-end — plan tasks complete,
tests green, the flow run in a real browser, the API returning 2xx on the happy path and 4xx on bad
input.>

## Per-stage cost table

> Paste the output of `cost-table.py` here. It buckets session-transcript usage into stage windows
> and prints this table — the columns below are the real headers; a real run fills the values.

| Stage | Model | Input | Output | Cache read | Cache write | Cost (USD) |
|---|---|---|---|---|---|---|
| 1. Brainstorm | … | … | … | … | … | … |
| 2. Plan | … | … | … | … | … | … |
| 3. Build | … | … | … | … | … | … |
| 4. Review | … | … | … | … | … | … |
| 5. QA | … | … | … | … | … | … |
| 6. Finalize | … | … | … | … | … | … |
| **Total** | | … | … | … | … | … |
