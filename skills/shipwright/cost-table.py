#!/usr/bin/env python3
"""Per-stage token & cost table for Shipwright Finalize reports.

Reconstructs token usage and cost per workflow stage by reading the project's
Claude Code session transcripts (JSONL) and bucketing each message by the stage
markers written to .claude/finalize-stages.jsonl during the run.

Usage:
    python3 cost-table.py                 # auto-detect transcripts for $PWD
    python3 cost-table.py --transcript X  # explicit transcript .jsonl
    python3 cost-table.py --ccusage       # defer to `ccusage` if installed

Output: a markdown table (printed to stdout) to paste into the finalize report.

When stage markers exist, ALL transcripts in the project dir are scanned and
entries from 30 min before the first marker onward are counted — this keeps
resumed/compacted sessions (which write a new .jsonl) in the totals. Without
markers, only the most recent transcript is used.

NOTE: pricing is BEST-EFFORT. Rates below are USD per 1M tokens and must be kept
current; long-context (>200k) tiers may cost more. Sanity-check against `/cost`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# USD per 1,000,000 tokens. Ordered: first substring match on the model id wins.
# Keep current — newer Opus (4.5+) is much cheaper than legacy Opus.
PRICING: list[tuple[str, dict]] = [
    ("opus-4-8-fast", {"input": 10.0, "output": 50.0, "cache_write": 12.50, "cache_read": 1.00}),
    ("opus-4-8", {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50}),
    ("opus-4-5", {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50}),
    ("opus-4-6", {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50}),
    ("opus-4-7", {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50}),
    ("opus",     {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50}),
    ("sonnet",   {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30}),
    ("haiku",    {"input": 1.0,  "output": 5.0,  "cache_write": 1.25,  "cache_read": 0.10}),
]
DEFAULT_RATES = {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30}
PRE_MARKER_GRACE = timedelta(minutes=30)


def rates_for(model: str) -> dict:
    m = (model or "").lower()
    for pattern, rates in PRICING:
        if pattern in m:
            return rates
    return DEFAULT_RATES


def family_of(model: str) -> str:
    m = (model or "").lower()
    for pattern, _ in PRICING:
        if pattern in m:
            return pattern
    return "unknown"


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def project_dir() -> Path:
    sanitized = re.sub(r"[^a-zA-Z0-9]", "-", str(Path.cwd()))
    return Path.home() / ".claude" / "projects" / sanitized


def find_transcripts(explicit: str | None, have_markers: bool) -> list[Path]:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            sys.exit(f"transcript not found: {p}")
        return [p]
    proj_dir = project_dir()
    if not proj_dir.is_dir():
        sys.exit(f"no transcript dir for this project: {proj_dir}")
    jsonls = sorted(proj_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime)
    if not jsonls:
        sys.exit(f"no .jsonl transcripts in {proj_dir}")
    # Markers define a time window, so resumed sessions (new .jsonl per resume)
    # can all be scanned safely. Without markers, fall back to the current session.
    return jsonls if have_markers else [jsonls[-1]]


def load_stage_markers() -> list[tuple[datetime, str]]:
    """Read .claude/finalize-stages.jsonl (one {stage, ts} object per line)."""
    base = Path.cwd() / ".claude"
    path = base / "finalize-stages.jsonl"
    if not path.is_file():  # legacy name from older runs
        path = base / "finalize-stages.json"
    markers: list[tuple[datetime, str]] = []
    if not path.is_file():
        return markers
    for line in path.read_text().splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        try:
            obj = json.loads(line)
            ts = parse_ts(obj.get("ts"))
            if ts:
                markers.append((ts, str(obj.get("stage", "?"))))
        except json.JSONDecodeError:
            continue
    markers.sort(key=lambda m: m[0])
    return markers


def stage_for(ts: datetime | None, markers: list[tuple[datetime, str]]) -> str:
    if not markers:
        return "Whole session"
    if ts is None:
        return markers[0][1]
    current = markers[0][1]
    for marker_ts, name in markers:
        if ts >= marker_ts:
            current = name
        else:
            break
    return current


def extract_usage(entry: dict) -> tuple[str, dict] | None:
    msg = entry.get("message")
    if not isinstance(msg, dict):
        return None
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return None
    return msg.get("model", ""), usage


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--transcript", help="explicit transcript .jsonl path")
    ap.add_argument("--ccusage", action="store_true", help="defer to ccusage if installed")
    args = ap.parse_args()

    if args.ccusage:
        try:
            subprocess.run(["ccusage"], check=False)
            return
        except FileNotFoundError:
            print("> ccusage not installed; falling back to transcript parsing.\n")

    markers = load_stage_markers()
    transcripts = find_transcripts(args.transcript, bool(markers))
    window_start = markers[0][0] - PRE_MARKER_GRACE if markers else None
    multi = len(transcripts) > 1

    # stage -> aggregates
    agg: dict[str, dict] = {}
    order: list[str] = [name for _, name in markers] or ["Whole session"]

    for transcript in transcripts:
        for raw in transcript.read_text().splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            got = extract_usage(entry)
            if not got:
                continue
            model, usage = got
            ts = parse_ts(entry.get("timestamp"))
            if window_start is not None:
                # Timestamp-less entries can't be placed in the window; in
                # multi-transcript mode they'd attribute stray sessions to
                # stage 1, so drop them there.
                if ts is None and multi:
                    continue
                if ts is not None and ts < window_start:
                    continue
            stage = stage_for(ts, markers)
            if stage not in order:
                order.append(stage)
            a = agg.setdefault(stage, {
                "input": 0, "output": 0, "cache_read": 0, "cache_write": 0,
                "cost": 0.0, "models": set(),
            })
            inp = usage.get("input_tokens", 0) or 0
            out = usage.get("output_tokens", 0) or 0
            cr = usage.get("cache_read_input_tokens", 0) or 0
            cw = usage.get("cache_creation_input_tokens", 0) or 0
            r = rates_for(model)
            a["input"] += inp
            a["output"] += out
            a["cache_read"] += cr
            a["cache_write"] += cw
            a["cost"] += (inp * r["input"] + out * r["output"]
                          + cr * r["cache_read"] + cw * r["cache_write"]) / 1_000_000
            if model:
                a["models"].add(family_of(model))

    if not agg:
        names = ", ".join(t.name for t in transcripts)
        print(f"> No usage data found in {names}.")
        return

    src = f"{len(transcripts)} transcripts" if multi else f"`{transcripts[0].name}`"
    print(f"> Source: {src} · generated {datetime.now(timezone.utc).isoformat()}\n")
    print("| Stage | Model | Input | Output | Cache read | Cache write | Cost (USD) |")
    print("|---|---|---|---|---|---|---|")
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "cost": 0.0}
    seen = set()
    for stage in order:
        if stage in seen or stage not in agg:
            continue
        seen.add(stage)
        a = agg[stage]
        models = ", ".join(sorted(a["models"])) or "-"
        print(f"| {stage} | {models} | {a['input']:,} | {a['output']:,} | "
              f"{a['cache_read']:,} | {a['cache_write']:,} | ${a['cost']:.2f} |")
        for k in ("input", "output", "cache_read", "cache_write", "cost"):
            totals[k] += a[k]
    print(f"| **Total** | | **{totals['input']:,}** | **{totals['output']:,}** | "
          f"**{totals['cache_read']:,}** | **{totals['cache_write']:,}** | "
          f"**${totals['cost']:.2f}** |")


if __name__ == "__main__":
    main()
