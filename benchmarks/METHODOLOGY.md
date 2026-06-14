# Benchmark methodology

How Shipwright measures the effect of its minimal-code build discipline without fabricating numbers.

## The claim we make — and the one we don't

**We make:** on a suite of discipline-sensitive coding tasks, on a single pinned model, injecting the
build ladder + simplicity rules reduces the lines of code and dependencies an agent produces, by the
medians reported in `results/results.md`, while holding the task's pass-rate.

**We do NOT make:** a universal "X% less code on all coding" claim. The suite is deliberately chosen
where the discipline bites (places a vanilla agent tends to add a dependency or a single-use
abstraction). Per-task numbers are always shown so no single task carries the headline.

## Experiment design

- **Independent variable:** the text appended to the system prompt (`discipline-prompt.md`), present
  for TREATMENT only. Everything else is held constant — same model, same task spec, same permissions,
  same harness.
- **Isolation:** every `(task, arm, rep)` runs in a fresh `mktemp` git repo with an empty baseline
  commit. This gives a clean `git diff` for generated code, and — because `cost-table.py` keys
  transcripts by sanitized working directory — a uniquely isolated transcript per run, read back for
  exact tokens and estimated cost.
- **Repetitions:** LLM output is non-deterministic, so each (task, arm) is run `REPS` times (default 5;
  **N ≥ 10 required to publish**) and reported as `median [min–max]`. Medians, not means, so one
  runaway run can't dominate.
- **Model pinning:** one `--model` per sweep, stamped into every run record. Arms are interleaved
  within a single sweep on one model, so model drift can't move one arm relative to the other.

## Metrics and exact tools

| Metric | How | Exactness |
|---|---|---|
| Lines added | `git diff --numstat baseline HEAD`, excluding lockfiles / `node_modules` / build dirs | exact |
| Files created | `git diff --name-status --diff-filter=A` | exact |
| Dependencies added | third-party imports (Python: not in `sys.stdlib_module_names`, not local, minus task-mandated like `pytest`) / `package.json` entries (Node) | exact |
| Cyclomatic complexity | `radon` if installed, else `null` (`complexity_tool: absent`) | optional |
| Tokens (in/out/cache) | `cost-table.py --transcript <run jsonl>` | exact |
| Cost (USD) | same call (LiteLLM live pricing) | **estimate, flagged** |
| Tests pass? | `pytest` on the agent-written tests | true / false / null |

## Aggregation and reductions

- Per `(task, arm)`: median + min/max across reps, over runs where tests did not fail.
- `reduction% = (median_control − median_treatment) / median_control`. Negative = treatment produced
  more. Overall = median of per-task reductions (not a pooled re-median, which would over-weight the
  most verbose task).
- Pass-rate per arm is reported next to every row.

## Publish gate

A number may appear in the project README only when **all** hold (enforced by `aggregate.py`):

1. **N ≥ 10** reps per arm,
2. on **≥ 5** task categories,
3. with **pass-rate ≥ 0.8** in both arms for those tasks,
4. on a **single pinned model**, dated.

Until then, the README "Numbers" section shows no percentages — only that the harness exists and the
numbers are pending. This mirrors the repo rule that the example finalize report is a labeled
placeholder until a real run replaces it.

## Limitations (read before quoting anything)

- **Non-determinism** — single runs are meaningless; mitigated by N ≥ 10 + medians + reported spread.
- **Task-suite bias** — categories were chosen where the discipline helps; this inflates reductions
  relative to a random task distribution. Stated, not hidden.
- **Control-arm fairness** — the control is a genuine, capable agent (same model/permissions); the only
  delta is the appended text. Identical `Done when` + pass-rate gating prevents "treatment did less".
- **Small absolute LOC** — tiny tasks make percentages swingy; absolute medians are shown beside them.
- **Dollar softness** — costs are LiteLLM-derived estimates (cost-table.py's own caveat); kept as a
  footnote, never a headline.
- **Language coverage** — the current suite is Python; Node/UI tasks are future work.

## Reproduce

```bash
MODEL=claude-... REPS=10 bash benchmarks/run.sh
python3 benchmarks/aggregate.py
```

Raw per-run JSONs land in `results/raw/` (the committed source of truth); `results/results.md` is
regenerated from them.
