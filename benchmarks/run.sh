#!/usr/bin/env bash
# Sweep: each task × arm × rep runs a headless Claude in a throwaway repo, then measure.py records
# one JSON per run. CONTROL is a vanilla agent; TREATMENT appends the minimal-code discipline prompt.
# The injected text is the ONLY difference between arms — same model, same task, same permissions.
#
# Config via env:
#   MODEL=claude-...            pin one model per sweep (recorded in every run; defeats drift)
#   REPS=5                      reps per (task, arm)            (N>=10 needed before publishing)
#   TASKS="01-cli-arg-parse"    space-separated task dirs       (default: all)
#   ARMS="control treatment"    which arms to run               (default: both)
#   PERMISSION_MODE=acceptEdits passed to claude --permission-mode
#   EXTRA_CLAUDE_ARGS=""        e.g. --dangerously-skip-permissions for fully unattended runs
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
COST_TABLE="$REPO_ROOT/skills/shipwright/cost-table.py"
DISCIPLINE="$HERE/discipline-prompt.md"
RAW="$HERE/results/raw"

MODEL="${MODEL:-}"
REPS="${REPS:-5}"
ARMS="${ARMS:-control treatment}"
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"
EXTRA_CLAUDE_ARGS="${EXTRA_CLAUDE_ARGS:-}"

command -v claude >/dev/null 2>&1 || { echo "error: 'claude' CLI not on PATH" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "error: 'git' not on PATH" >&2; exit 1; }
mkdir -p "$RAW"

if [ -z "${TASKS:-}" ]; then
  TASKS="$(cd "$HERE/tasks" && for d in */; do echo "${d%/}"; done)"
fi
[ -n "$MODEL" ] || echo "warning: MODEL unset — runs are recorded as 'unknown'; pin one to compare arms fairly." >&2

for task in $TASKS; do
  spec="$HERE/tasks/$task/spec.md"
  [ -f "$spec" ] || { echo "skip: no spec for $task" >&2; continue; }
  lang="$(grep -i '^## Language' "$spec" | head -1 | sed 's/.*: *//' | tr -d '[:space:]')"
  lang="${lang:-python}"
  prompt="$(cat "$spec")"

  for arm in $ARMS; do
    for rep in $(seq 1 "$REPS"); do
      ts="$(date -u +%Y%m%dT%H%M%SZ)"
      run_id="${task}-${arm}-r${rep}-${ts}"
      tmp="$(mktemp -d)"
      git -C "$tmp" init -q
      git -C "$tmp" commit --allow-empty -qm baseline
      baseline="$(git -C "$tmp" rev-parse HEAD)"

      args=(-p "$prompt" --output-format json --permission-mode "$PERMISSION_MODE" --add-dir "$tmp")
      [ -n "$MODEL" ] && args+=(--model "$MODEL")
      [ "$arm" = "treatment" ] && args+=(--append-system-prompt "$(cat "$DISCIPLINE")")
      # shellcheck disable=SC2086
      ( cd "$tmp" && claude "${args[@]}" $EXTRA_CLAUDE_ARGS >/dev/null 2>&1 ) || \
        echo "warning: claude exited non-zero for $run_id (recording whatever it produced)" >&2

      git -C "$tmp" add -A
      git -C "$tmp" commit -qm result --allow-empty

      sanitized="$(printf '%s' "$tmp" | sed 's/[^a-zA-Z0-9]/-/g')"
      tdir="$HOME/.claude/projects/$sanitized"
      transcript="$(ls -t "$tdir"/*.jsonl 2>/dev/null | head -1 || true)"

      out="$RAW/${run_id}.json"
      python3 "$HERE/measure.py" --dir "$tmp" --baseline "$baseline" \
        --task "$task" --arm "$arm" --rep "$rep" --lang "$lang" \
        --model "${MODEL:-unknown}" --run-id "$run_id" --ts "$ts" \
        --cost-table "$COST_TABLE" ${transcript:+--transcript "$transcript"} > "$out"
      echo "wrote $out"
      rm -rf "$tmp"
    done
  done
done

echo "Done. Aggregate with: python3 $HERE/aggregate.py"
