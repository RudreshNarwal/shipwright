#!/usr/bin/env python3
"""Per-stage token & cost table for Shipwright Finalize reports.

Reconstructs token usage and cost per workflow stage by reading the project's
Claude Code session transcripts (JSONL) and bucketing each message by the stage
markers written to .claude/finalize-stages.jsonl during the run.

Usage:
    python3 cost-table.py                 # auto-detect transcripts for $PWD
    python3 cost-table.py --transcript X  # explicit transcript .jsonl
    python3 cost-table.py --offline       # skip the network; bundled rates only
    python3 cost-table.py --refresh       # force-refresh the live pricing cache
    python3 cost-table.py --ccusage       # defer to `ccusage` if installed

Output: a markdown table (printed to stdout) to paste into the finalize report.

When stage markers exist, ALL transcripts in the project dir are scanned and
entries from 30 min before the first marker onward are counted — this keeps
resumed/compacted sessions (which write a new .jsonl) in the totals. Without
markers, only the most recent transcript is used.

PRICING is DYNAMIC: per model, rates are looked up from LiteLLM's community price
list (the source `ccusage` also uses), fetched once and cached for 24h under
~/.cache/shipwright/. Any model not in the live data (e.g. a brand-new id) falls
back to the bundled static table below. Token counts are EXACT (straight from the
transcript); dollar costs are best-effort estimates — sanity-check against `/cost`.
The header prints which pricing source was used for each model.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- Live pricing (LiteLLM community price list) ---------------------------
LITELLM_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)
CACHE_PATH = Path.home() / ".cache" / "shipwright" / "model_prices.json"
CACHE_TTL = timedelta(hours=24)
FETCH_TIMEOUT = 10  # seconds

# Bundled fallback. USD per 1,000,000 tokens. First substring match on the model
# id wins. Used offline, or when a model isn't present in the live data.
STATIC_PRICING: list[tuple[str, dict]] = [
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


def _normalize_litellm(data: dict) -> dict[str, dict]:
    """LiteLLM stores USD-per-token; convert to USD-per-1M to match STATIC_PRICING.

    Anthropic's standard cache multipliers (write = 1.25x input, read = 0.10x input)
    fill in any entry that omits explicit cache costs.
    """
    out: dict[str, dict] = {}
    for key, v in data.items():
        if not isinstance(v, dict):
            continue
        ipt, opt = v.get("input_cost_per_token"), v.get("output_cost_per_token")
        if ipt is None or opt is None:
            continue
        inp = ipt * 1_000_000
        cw = v.get("cache_creation_input_token_cost")
        cr = v.get("cache_read_input_token_cost")
        out[key.lower()] = {
            "input": inp,
            "output": opt * 1_000_000,
            "cache_write": cw * 1_000_000 if cw is not None else inp * 1.25,
            "cache_read": cr * 1_000_000 if cr is not None else inp * 0.10,
        }
    return out


def _read_cache() -> tuple[dict | None, timedelta | None]:
    try:
        if CACHE_PATH.is_file():
            mtime = datetime.fromtimestamp(CACHE_PATH.stat().st_mtime, timezone.utc)
            age = datetime.now(timezone.utc) - mtime
            return json.loads(CACHE_PATH.read_text()), age
    except (OSError, ValueError):
        pass
    return None, None


def _fetch_pricing() -> dict:
    req = urllib.request.Request(LITELLM_URL, headers={"User-Agent": "shipwright-cost-table"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:  # noqa: S310 (fixed https url)
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(raw)
    except OSError:
        pass
    return data


def load_live_pricing(offline: bool = False, refresh: bool = False) -> tuple[dict[str, dict], str]:
    """Return (model_id -> rates-per-1M, source label). Empty dict ⇒ static only."""
    if offline:
        return {}, "bundled static table (--offline)"
    cached, age = (None, None) if refresh else _read_cache()
    if cached is not None and age is not None and age < CACHE_TTL:
        hours = int(age.total_seconds() // 3600)
        return _normalize_litellm(cached), f"LiteLLM (cached {hours}h ago)"
    try:
        return _normalize_litellm(_fetch_pricing()), "LiteLLM (fetched just now)"
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as exc:
        if cached is not None:
            return _normalize_litellm(cached), f"LiteLLM (stale cache; fetch failed: {type(exc).__name__})"
        return {}, f"bundled static table (fetch failed: {type(exc).__name__})"


def _canonical(model: str) -> list[str]:
    """Model-id variants to try against the live keys: drop [..] suffixes and provider prefixes."""
    m = (model or "").lower().strip()
    out = [m]
    stripped = re.sub(r"\[.*?\]", "", m)  # e.g. claude-opus-4-8[1m] -> claude-opus-4-8
    if stripped != m:
        out.append(stripped)
    if "/" in stripped:  # e.g. anthropic/claude-... or us.anthropic.claude-...
        out.append(stripped.split("/", 1)[1])
    return out


def _match_live(model: str, live: dict[str, dict]) -> dict | None:
    if not model or not live:
        return None
    cands = _canonical(model)
    for c in cands:  # exact first
        if c in live:
            return live[c]
    best_key = None  # else longest live key that is a substring of the model id
    for c in cands:
        for key in live:
            if key in c and (best_key is None or len(key) > len(best_key)):
                best_key = key
    return live[best_key] if best_key else None


def rates_for(model: str, live: dict[str, dict]) -> tuple[dict, bool]:
    """Return (rates-per-1M, is_live). Live data wins; else bundled table; else default."""
    hit = _match_live(model, live)
    if hit is not None:
        return hit, True
    m = (model or "").lower()
    for pattern, rates in STATIC_PRICING:
        if pattern in m:
            return rates, False
    return DEFAULT_RATES, False


def family_of(model: str) -> str:
    m = (model or "").lower()
    for pattern, _ in STATIC_PRICING:
        if pattern in m:
            return pattern
    cleaned = re.sub(r"\[.*?\]", "", m).split("/")[-1]
    return cleaned or "unknown"


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
    ap.add_argument("--offline", action="store_true", help="skip the network; bundled rates only")
    ap.add_argument("--refresh", action="store_true", help="force-refresh the live pricing cache")
    ap.add_argument("--ccusage", action="store_true", help="defer to ccusage if installed")
    args = ap.parse_args()

    if args.ccusage:
        try:
            subprocess.run(["ccusage"], check=False)
            return
        except FileNotFoundError:
            print("> ccusage not installed; falling back to transcript parsing.\n")

    live, price_src = load_live_pricing(offline=args.offline, refresh=args.refresh)

    markers = load_stage_markers()
    transcripts = find_transcripts(args.transcript, bool(markers))
    window_start = markers[0][0] - PRE_MARKER_GRACE if markers else None
    multi = len(transcripts) > 1

    # stage -> aggregates
    agg: dict[str, dict] = {}
    order: list[str] = [name for _, name in markers] or ["Whole session"]
    priced_live: set[str] = set()
    priced_fallback: set[str] = set()

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
            r, is_live = rates_for(model, live)
            a["input"] += inp
            a["output"] += out
            a["cache_read"] += cr
            a["cache_write"] += cw
            a["cost"] += (inp * r["input"] + out * r["output"]
                          + cr * r["cache_read"] + cw * r["cache_write"]) / 1_000_000
            if model:
                fam = family_of(model)
                a["models"].add(fam)
                (priced_live if is_live else priced_fallback).add(fam)

    if not agg:
        names = ", ".join(t.name for t in transcripts)
        print(f"> No usage data found in {names}.")
        return

    src = f"{len(transcripts)} transcripts" if multi else f"`{transcripts[0].name}`"
    print(f"> Source: {src} · generated {datetime.now(timezone.utc).isoformat()}")
    print(f"> Pricing: {price_src}.", end="")
    if priced_live:
        print(f" Live-priced: {', '.join(sorted(priced_live))}.", end="")
    if priced_fallback:
        print(f" Bundled-rate fallback (verify): {', '.join(sorted(priced_fallback))}.", end="")
    print("\n> Token counts are exact; dollar costs are estimates — sanity-check against `/cost`.\n")
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
