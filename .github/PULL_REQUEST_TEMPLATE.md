<!-- Thanks for contributing to Shipwright! Keep PRs surgical and focused (Karpathy rules apply here too). -->

## What & why

<!-- What does this change, and what problem does it solve? -->

## Checklist

- [ ] Ran `bash scripts/lint.sh` and it passes (the same suite CI runs).
- [ ] I did **not** hand-edit a vendored skill (anything under `skills/` except `skills/shipwright/`).
      Vendored fixes belong upstream — pull them back with `scripts/sync-vendored.sh` and update `VENDORED.md`.
- [ ] If I changed a vendored skill's pin, I updated the version + date in `VENDORED.md` and preserved
      the upstream license in `licenses/`.
- [ ] If I edited `skills/shipwright/SKILL.md`, its `description:` frontmatter is still **triggers-only**
      (no workflow summary leaked in).
- [ ] Docs updated where relevant (`README.md`, `CLAUDE.md`, `CHANGELOG.md`).

## Notes for reviewers

<!-- Anything to flag: assumptions made, follow-ups deferred, areas needing a closer look. -->
