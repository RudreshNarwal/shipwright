#!/usr/bin/env python3
"""Capture one benchmark run's metrics as a JSON record (printed to stdout).

Runs inside a finished result repo (the agent has written code; run.sh has committed it on top of an
empty baseline). All metrics are EXACT counts except dollar cost, which is a flagged estimate carried
through from cost-table.py. Anything that needs an absent tool degrades to null — it never blocks.

Usage (driven by run.sh):
    python3 measure.py --dir REPO --baseline REF --task T --arm control|treatment --rep N \\
        --lang python --cost-table /path/to/cost-table.py [--transcript X.jsonl] \\
        [--model M] [--run-id ID] [--ts ISO]
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import re
import subprocess
import sys
import sysconfig
from pathlib import Path

_STDLIB_DIR = sysconfig.get_paths().get("stdlib", "")


def is_stdlib(name: str) -> bool:
    """True if `name` is a standard-library module. Uses sys.stdlib_module_names on 3.10+, else falls
    back to locating the module (a missing module is treated as third-party — i.e. an added dep)."""
    if name in sys.builtin_module_names:
        return True
    names = getattr(sys, "stdlib_module_names", None)
    if names is not None:
        return name in names
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    origin = spec.origin or ""
    if origin in ("built-in", "frozen"):
        return True
    if "site-packages" in origin or "dist-packages" in origin:
        return False
    return bool(_STDLIB_DIR) and origin.startswith(_STDLIB_DIR)

# Paths that are not the agent's own solution code — excluded from LOC and file counts.
EXCLUDE_SUBSTR = ("node_modules/", "__pycache__/", ".git/", "dist/", "build/", ".venv/")
EXCLUDE_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
    ".gitignore",
}
# Third-party modules the task itself mandates (so choosing them isn't an over-engineering signal).
DEP_ALLOWLIST = {"pytest"}
TEST_TIMEOUT = 120  # seconds


def git(repo: str, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, check=False
    ).stdout


def excluded(path: str) -> bool:
    return any(s in path for s in EXCLUDE_SUBSTR) or Path(path).name in EXCLUDE_NAMES


def code_metrics(repo: str, baseline: str) -> tuple[int, int]:
    """Lines added and files created between baseline and HEAD, excluding noise paths."""
    loc = 0
    for line in git(repo, "diff", "--numstat", baseline, "HEAD").splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or parts[0] == "-":  # "-" = binary file
            continue
        added, _, path = parts
        if not excluded(path):
            loc += int(added)
    files = sum(
        1
        for line in git(repo, "diff", "--name-status", "--diff-filter=A", baseline, "HEAD").splitlines()
        if "\t" in line and not excluded(line.split("\t", 1)[1])
    )
    return loc, files


def python_deps_added(repo: str) -> int:
    """Distinct third-party modules imported (not stdlib, not a local file, not task-mandated)."""
    root = Path(repo)
    py_files = [p for p in root.rglob("*.py") if not excluded(str(p.relative_to(root)))]
    local = {p.stem for p in py_files}
    third_party: set[str] = set()
    for p in py_files:
        try:
            tree = ast.parse(p.read_text())
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [node.module.split(".")[0]] if (node.module and node.level == 0) else []
            else:
                continue
            for r in roots:
                if r and r not in local and r not in DEP_ALLOWLIST and not is_stdlib(r):
                    third_party.add(r)
    return len(third_party)


def node_deps_added(repo: str) -> int:
    pkg = Path(repo) / "package.json"
    if not pkg.is_file():
        return 0
    try:
        data = json.loads(pkg.read_text())
    except (OSError, ValueError):
        return 0
    return len(data.get("dependencies", {})) + len(data.get("devDependencies", {}))


def complexity_avg(repo: str, lang: str) -> tuple[float | None, str]:
    """Average cyclomatic complexity via radon, if installed; else (None, 'absent')."""
    if lang != "python":
        return None, "absent"
    try:
        out = subprocess.run(
            ["radon", "cc", "-s", "-a", "-j", repo], capture_output=True, text=True, check=False
        ).stdout
        data = json.loads(out)
    except (FileNotFoundError, ValueError):
        return None, "absent"
    scores = [b.get("complexity", 0) for blocks in data.values() for b in blocks]
    return (round(sum(scores) / len(scores), 2), "radon") if scores else (None, "radon")


def tests_pass(repo: str, lang: str) -> bool | None:
    """True/False if a test suite ran; None if no runner or no tests (can't judge)."""
    if lang == "python":
        has_tests = any(
            re.match(r"(test_.*|.*_test)\.py$", p.name) for p in Path(repo).rglob("*.py")
        )
        if not has_tests or importlib.util.find_spec("pytest") is None:
            return None  # no tests, or no runner installed → can't judge (not a failure)
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=repo, capture_output=True, text=True, timeout=TEST_TIMEOUT, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return r.returncode == 0
    return None


def cost_from_table(cost_table: str, transcript: str | None) -> dict:
    """Reuse cost-table.py for EXACT tokens + ESTIMATED dollars. Parses its markdown Total row."""
    blank = {"tokens": None, "cost_usd_estimate": None, "pricing_source": None}
    if not transcript or not Path(cost_table).is_file():
        return blank
    try:
        out = subprocess.run(
            [sys.executable, cost_table, "--transcript", transcript],
            capture_output=True, text=True, timeout=60, check=False,
        ).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return blank
    source = None
    total_line = None
    for line in out.splitlines():
        if line.startswith("> Pricing:"):
            source = line[len("> Pricing:"):].strip().split(".")[0]
        if "**Total**" in line:
            total_line = line
    if not total_line:
        return blank
    nums = re.findall(r"\d+\.\d+|\d+", total_line.replace(",", ""))
    if len(nums) < 5:
        return blank
    return {
        "tokens": {
            "input": int(nums[0]), "output": int(nums[1]),
            "cache_read": int(nums[2]), "cache_write": int(nums[3]),
        },
        "cost_usd_estimate": float(nums[4]),
        "pricing_source": source,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--arm", required=True, choices=["control", "treatment"])
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--lang", default="python")
    ap.add_argument("--cost-table", default="")
    ap.add_argument("--transcript", default="")
    ap.add_argument("--model", default="unknown")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--ts", default="")
    args = ap.parse_args()

    loc, files = code_metrics(args.dir, args.baseline)
    deps = python_deps_added(args.dir) if args.lang == "python" else node_deps_added(args.dir)
    cx, cx_tool = complexity_avg(args.dir, args.lang)
    cost = cost_from_table(args.cost_table, args.transcript or None)

    record = {
        "task": args.task, "arm": args.arm, "rep": args.rep,
        "model": args.model, "run_id": args.run_id, "ts": args.ts,
        "loc_added": loc, "files_created": files, "deps_added": deps,
        "complexity_avg": cx, "complexity_tool": cx_tool,
        "passed": tests_pass(args.dir, args.lang),
        **cost,
    }
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
