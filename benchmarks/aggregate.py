#!/usr/bin/env python3
"""Aggregate benchmark run JSONs into medians + reduction percentages, with the honest-numbers gate.

Reads benchmarks/results/raw/*.json, groups by (task, arm), reports medians with spread, computes
control-vs-treatment reductions, and writes benchmarks/results/results.md. Numbers from fewer than
PUBLISH_N reps are tagged PRELIMINARY and the publish gate fails — nothing goes to the README headline
until the gate passes.

LOC / files / deps / tokens are EXACT counts. Dollar cost is a flagged estimate (from cost-table.py).
Reductions are computed on MEDIANS (robust to LLM-run variance), never on single runs or means.

Usage:
    python3 aggregate.py                      # uses ./results/raw
    python3 aggregate.py --raw path/to/raw    # explicit
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

PUBLISH_N = 10          # min reps per arm before a number can leave "preliminary"
PUBLISH_MIN_TASKS = 5   # min tasks meeting the bar for the suite to be publishable
PUBLISH_PASS_RATE = 0.8


def med_spread(values: list[float]) -> tuple[float, float, float] | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return statistics.median(nums), min(nums), max(nums)


def total_tokens(rec: dict) -> int | None:
    t = rec.get("tokens")
    return sum(t.values()) if isinstance(t, dict) else None


def reduction(ctrl: float | None, treat: float | None) -> float | None:
    if ctrl is None or treat is None or ctrl == 0:
        return None
    return round((ctrl - treat) / ctrl * 100, 1)


def fmt(stats: tuple[float, float, float] | None) -> str:
    if stats is None:
        return "—"
    med, lo, hi = stats
    med_s = f"{med:.2f}" if isinstance(med, float) and med != int(med) else f"{int(med)}"
    return f"{med_s} [{int(lo)}–{int(hi)}]" if lo == int(lo) and hi == int(hi) else f"{med_s} [{lo:.2f}–{hi:.2f}]"


def pct(v: float | None) -> str:
    return "—" if v is None else f"{v:+.0f}%".replace("+", "") if v >= 0 else f"{v:.0f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument("--raw", default=str(here / "results" / "raw"))
    ap.add_argument("--out", default=str(here / "results" / "results.md"))
    args = ap.parse_args()

    raw_dir = Path(args.raw)
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        print(f"No run JSONs in {raw_dir}. Run ./run.sh first.")
        return

    # (task, arm) -> list of records
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for f in files:
        try:
            rec = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        groups[(rec["task"], rec["arm"])].append(rec)

    tasks = sorted({t for (t, _) in groups})
    model = next(iter(groups.values()))[0].get("model", "unknown") if groups else "unknown"

    rows: list[str] = []
    per_task_reductions: dict[str, list[float]] = {"loc": [], "deps": [], "tokens": []}
    publishable_tasks = 0

    for task in tasks:
        ctrl = [r for r in groups.get((task, "control"), []) if r.get("passed") is not False]
        treat = [r for r in groups.get((task, "treatment"), []) if r.get("passed") is not False]
        n = min(len(ctrl), len(treat))

        loc_c, loc_t = med_spread([r["loc_added"] for r in ctrl]), med_spread([r["loc_added"] for r in treat])
        dep_c, dep_t = med_spread([r["deps_added"] for r in ctrl]), med_spread([r["deps_added"] for r in treat])
        tok_c, tok_t = med_spread([total_tokens(r) for r in ctrl]), med_spread([total_tokens(r) for r in treat])

        loc_red = reduction(loc_c[0] if loc_c else None, loc_t[0] if loc_t else None)
        tok_red = reduction(tok_c[0] if tok_c else None, tok_t[0] if tok_t else None)
        for key, val in (("loc", loc_red), ("tokens", tok_red),
                         ("deps", reduction(dep_c[0] if dep_c else None, dep_t[0] if dep_t else None))):
            if val is not None:
                per_task_reductions[key].append(val)

        pr_c = [r["passed"] for r in groups.get((task, "control"), []) if r.get("passed") is not None]
        pr_t = [r["passed"] for r in groups.get((task, "treatment"), []) if r.get("passed") is not None]
        rate_c = (sum(pr_c) / len(pr_c)) if pr_c else 0.0
        rate_t = (sum(pr_t) / len(pr_t)) if pr_t else 0.0

        tag = "" if n >= PUBLISH_N else f" `PRELIMINARY N={n}`"
        if n >= PUBLISH_N and rate_c >= PUBLISH_PASS_RATE and rate_t >= PUBLISH_PASS_RATE:
            publishable_tasks += 1

        dep_delta = "—"
        if dep_c and dep_t:
            dep_delta = f"{int(dep_c[0])}→{int(dep_t[0])}"
        rows.append(
            f"| {task}{tag} | {fmt(loc_c)} | {fmt(loc_t)} | {pct(loc_red)} | {dep_delta} | "
            f"{pct(tok_red)} | {n} | {sum(pr_c)}/{len(pr_c) or 0} · {sum(pr_t)}/{len(pr_t) or 0} |"
        )

    def overall(key: str) -> str:
        vals = per_task_reductions[key]
        return pct(round(statistics.median(vals), 1)) if vals else "—"

    gate_pass = publishable_tasks >= PUBLISH_MIN_TASKS
    verdict = (
        f"PUBLISHABLE — {publishable_tasks} tasks cleared the gate (N≥{PUBLISH_N}, pass-rate≥{PUBLISH_PASS_RATE})."
        if gate_pass else
        f"PRELIMINARY — only {publishable_tasks}/{PUBLISH_MIN_TASKS} tasks cleared the gate. "
        "Do NOT put these percentages in the README yet."
    )

    md = [
        "# Benchmark results",
        "",
        f"> Model: `{model}` · runs: {len(files)} · tasks: {len(tasks)}",
        "> **LOC, files, deps, and tokens are exact counts; dollar figures are best-effort estimates "
        "(LiteLLM pricing via cost-table.py), not authoritative.** Reductions are computed on medians.",
        "",
        f"**Gate: {verdict}**",
        "",
        "| Task | LOC control | LOC treatment | LOC ↓ | Deps (c→t) | Tokens ↓ | N | Pass c·t |",
        "|---|---|---|---|---|---|---|---|",
        *rows,
        f"| **Overall (median of per-task)** | | | **{overall('loc')}** | | **{overall('tokens')}** | | |",
        "",
        "Median LOC shown as `median [min–max]`. A reduction is `(median_control − median_treatment) / "
        "median_control`. Negative means treatment produced more. Failed runs (tests red) are excluded "
        "from code-volume medians; pass-rate is reported separately so 'less code' is never decoupled "
        "from 'still works'.",
        "",
        "See [`METHODOLOGY.md`](../METHODOLOGY.md) for the experiment design, limitations, and how to "
        "reproduce.",
        "",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md))
    print("\n".join(md))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
