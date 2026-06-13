# Contributing to Shipwright

Thanks for your interest! Shipwright is a small, focused project — an orchestration skill plus a
pinned set of vendored sub-skills.

## Ground rules

- **Don't hand-edit vendored skills.** Everything under `skills/` *except* `skills/shipwright/` is a
  pinned upstream copy. Fixes to those belong upstream (superpowers / andrej-karpathy-skills); pull
  them back in with `scripts/sync-vendored.sh`.
- **The workflow itself** lives in `skills/shipwright/SKILL.md` and `skills/shipwright/cost-table.py`.
  That's the place for pipeline changes.
- **Run the checks before opening a PR:** `bash scripts/lint.sh` (the same checks CI runs).

## Changing the workflow skill

`SKILL.md` is a discipline-enforcing skill — treat edits like the [superpowers writing-skills
TDD loop](https://github.com/obra/superpowers): describe the failing behavior you observed, make the
minimal change, and confirm it holds. Keep the `description` frontmatter to *triggers only* — never
summarize the workflow there (Claude will follow the summary instead of reading the skill).

## Bumping a vendored dependency

```bash
scripts/sync-vendored.sh <superpowers-ref> <karpathy-ref>
# then update the version pins + date in VENDORED.md and run scripts/lint.sh
```

## Reporting bugs / requesting features

Use the issue templates. Tell us which phase, and whether you installed via plugin or copied skills.
