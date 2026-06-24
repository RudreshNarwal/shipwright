#!/usr/bin/env bash
# Provenship self-checks — run locally and in CI. Exits non-zero on any failure.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

echo "==> 1. No upstream namespaces left in skills/"
if grep -rEn "superpowers:|andrej-karpathy-skills:" "$ROOT/skills" >/tmp/sw_upstream 2>/dev/null; then
  echo "FAIL: upstream namespace refs remain:"; cat /tmp/sw_upstream; fail=1
else
  echo "OK"
fi

echo "==> 2. Every provenship:<skill> reference resolves to a bundled skill dir"
missing=0
for ref in $(grep -rhoE "provenship:[a-z-]+" "$ROOT/skills" | sort -u); do
  name="${ref#provenship:}"
  if [ ! -d "$ROOT/skills/$name" ]; then
    echo "FAIL: dangling reference $ref (no skills/$name/)"; missing=1; fail=1
  fi
done
[ "$missing" -eq 0 ] && echo "OK"

echo "==> 3. cost-table.py compiles"
if python3 -m py_compile "$ROOT/skills/provenship/cost-table.py" 2>/tmp/sw_py; then
  echo "OK"
else
  echo "FAIL:"; cat /tmp/sw_py; fail=1
fi

echo "==> 4. JSON manifests are valid"
if python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('$ROOT/.claude-plugin/*.json') + glob.glob('$ROOT/.codex-plugin/*.json') + ['$ROOT/opencode.json']]" 2>/tmp/sw_json; then
  echo "OK"
else
  echo "FAIL:"; cat /tmp/sw_json; fail=1
fi

echo "==> 5. Main skill has no personal references"
if grep -rin "rudy" "$ROOT/skills/provenship" >/tmp/sw_rudy 2>/dev/null; then
  echo "FAIL: personal references remain:"; cat /tmp/sw_rudy; fail=1
else
  echo "OK"
fi

echo "==> 6. OpenCode plugin parses (skipped if node absent)"
if command -v node >/dev/null 2>&1; then
  if node --check "$ROOT/.opencode/plugins/provenship.mjs" 2>/tmp/sw_mjs; then
    echo "OK"
  else
    echo "FAIL:"; cat /tmp/sw_mjs; fail=1
  fi
else
  echo "SKIP (node not found)"
fi

if [ "$fail" -ne 0 ]; then echo; echo "LINT FAILED"; exit 1; fi
echo; echo "ALL CHECKS PASSED"
