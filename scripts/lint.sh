#!/usr/bin/env bash
# Shipwright self-checks — run locally and in CI. Exits non-zero on any failure.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

echo "==> 1. No upstream namespaces left in skills/"
if grep -rEn "superpowers:|andrej-karpathy-skills:" "$ROOT/skills" >/tmp/sw_upstream 2>/dev/null; then
  echo "FAIL: upstream namespace refs remain:"; cat /tmp/sw_upstream; fail=1
else
  echo "OK"
fi

echo "==> 2. Every shipwright:<skill> reference resolves to a bundled skill dir"
missing=0
for ref in $(grep -rhoE "shipwright:[a-z-]+" "$ROOT/skills" | sort -u); do
  name="${ref#shipwright:}"
  if [ ! -d "$ROOT/skills/$name" ]; then
    echo "FAIL: dangling reference $ref (no skills/$name/)"; missing=1; fail=1
  fi
done
[ "$missing" -eq 0 ] && echo "OK"

echo "==> 3. cost-table.py compiles"
if python3 -m py_compile "$ROOT/skills/shipwright/cost-table.py" 2>/tmp/sw_py; then
  echo "OK"
else
  echo "FAIL:"; cat /tmp/sw_py; fail=1
fi

echo "==> 4. JSON manifests are valid"
if python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('$ROOT/.claude-plugin/*.json')]" 2>/tmp/sw_json; then
  echo "OK"
else
  echo "FAIL:"; cat /tmp/sw_json; fail=1
fi

echo "==> 5. Main skill has no personal references"
if grep -rin "rudy" "$ROOT/skills/shipwright" >/tmp/sw_rudy 2>/dev/null; then
  echo "FAIL: personal references remain:"; cat /tmp/sw_rudy; fail=1
else
  echo "OK"
fi

if [ "$fail" -ne 0 ]; then echo; echo "LINT FAILED"; exit 1; fi
echo; echo "ALL CHECKS PASSED"
