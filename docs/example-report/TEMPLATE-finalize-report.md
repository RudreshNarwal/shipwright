# Finalize report — TEMPLATE

> 📋 **This is a template, not a captured run.** It shows the *shape* of the report Shipwright's
> Phase 6 writes to `docs/finalize/YYYY-MM-DD-<branch>.md`. Every value is a `<placeholder>` —
> nothing here is invented or measured. A real run fills these in from actual tests, gstack `/qa`,
> one screenshot **per feature**, and `cost-table.py`.

## Query

> `<the original requirement, verbatim — what the user asked for>`

## Solution (overview)

<One paragraph: what was built across all features, the approach, and N files changed, +A / −B vs
`main`.>

---

## Features

> One block per feature built. The number of screenshots equals the number of features:
> 2 features → 2 screenshots, 5 features → 5 screenshots.

### Feature 1 — `<feature name>`

- **Query:** `<what was asked for this slice>`
- **Solution:** `<what was built, briefly>`
- **Screenshot:**

  ![<feature 1 working>](assets/<branch>/<feature-1-slug>.png)

- **File changes:** `<path/a.ts>`, `<path/b.vue>` (+`<a>` / −`<b>`)

### Feature 2 — `<feature name>`

- **Query:** `<what was asked for this slice>`
- **Solution:** `<what was built, briefly>`
- **Screenshot:**

  ![<feature 2 working>](assets/<branch>/<feature-2-slug>.png)

- **File changes:** `<path/c.py>` (+`<a>` / −`<b>`)

<!-- …repeat one block per feature… -->

---

## Test & QA results

| Suite | Result |
|---|---|
| `<backend runner, e.g. pytest>` | `<n passed / n failed>` |
| `<frontend runner, e.g. vitest>` | `<n passed / n failed>` |

- **Health score:** `<score>/10` (gstack `/qa`, `<Quick|Standard|Exhaustive>` tier)
- **API verification (`browse network`):** `<METHOD /path>` → `<status>`; … (expected calls fired, 2xx).
- **Console:** `<none, or the errors found>`.
- **Phase-5 escalations:** `<any loop-backs: finding → route taken → outcome, or "none">`

## Assumptions logged during the run

- `<each ambiguity and the safer interpretation taken — surfaced, not guessed silently>`
- `<anything ruled out of scope and recorded as a follow-up>`

## Checked thoroughly

<Evidence-backed statement: plan tasks complete, tests green, each feature exercised in a real
browser, API 2xx on the happy path and 4xx on bad input.>

## Per-stage cost table

> From `cost-table.py`. Token counts are exact (straight from the transcripts); dollar costs are
> best-effort estimates from live per-model pricing — sanity-check against `/cost`. Headers below are
> the real columns; a real run fills the values.

| Stage | Model | Input | Output | Cache read | Cache write | Cost (USD) |
|---|---|---|---|---|---|---|
| 1. Brainstorm | … | … | … | … | … | … |
| 2. Plan | … | … | … | … | … | … |
| 3. Build | … | … | … | … | … | … |
| 4. Review | … | … | … | … | … | … |
| 5. QA | … | … | … | … | … | … |
| 6. Finalize | … | … | … | … | … | … |
| **Total** | | … | … | … | … | … |
