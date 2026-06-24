# Provenship benchmarks

A control-vs-treatment harness that measures the effect of Provenship's **minimal-code build
discipline** (the ponytail-style decision ladder + Karpathy's simplicity rules) on the code an agent
produces — honestly, with no fabricated numbers.

- **CONTROL** — a vanilla headless agent solves a task.
- **TREATMENT** — the *same* model solves the *same* task, with `discipline-prompt.md` appended to its
  system prompt. That injected text is the only difference between arms.

We measure lines of code, files, dependencies added, tokens, and (estimated) dollars per run, across a
fixed task suite, many reps, and report **medians with spread** — never single-shot numbers.

## Run it

```bash
# Pin one model per sweep so arms are compared fairly. Default REPS=5 (preliminary).
MODEL=claude-... REPS=10 bash benchmarks/run.sh
python3 benchmarks/aggregate.py        # writes results/results.md and prints the table + gate verdict
```

Smoke test (fast, proves the wiring without a full sweep):

```bash
MODEL=claude-... REPS=2 TASKS="04-data-transform" bash benchmarks/run.sh
python3 benchmarks/aggregate.py
```

Each run executes in a throwaway `mktemp` repo, so generated code is measured cleanly and each run gets
its own isolated Claude transcript (which `cost-table.py` reads for exact tokens / estimated cost).

## The honesty rules (non-negotiable)

- **LOC, files, deps, and tokens are exact counts. Dollars are a flagged estimate** (LiteLLM pricing
  via `cost-table.py`), never authoritative.
- Reductions are computed on **medians**, with N and spread shown.
- Any number with **N < 10** per arm is tagged `PRELIMINARY` and is barred from the README headline.
- **Pass-rate is reported alongside** every result; failed runs are excluded from code-volume medians
  so "less code" is never confused with "did less".
- Nothing reaches the README "Numbers" section until the publish gate passes (see `METHODOLOGY.md`).

## Files

| File | Role |
|---|---|
| `run.sh` | sweeps tasks × arms × reps; drives headless Claude; calls `measure.py` |
| `measure.py` | one run → one JSON record (git LOC/files/deps, complexity if available, tests, tokens/cost) |
| `aggregate.py` | all run JSONs → medians, reductions, pass-rates, `results/results.md`, gate verdict |
| `discipline-prompt.md` | the TREATMENT-only injected text (the build ladder + simplicity rules) |
| `tasks/*/spec.md` | the task suite (one self-contained spec per task) |
| `results/raw/*.json` | per-run records — the committed source of truth |
| `METHODOLOGY.md` | experiment design, the claim's scope, limitations, reproduction |
