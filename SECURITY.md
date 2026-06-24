# Security Policy

Provenship is an orchestration skill for Claude Code: it drives coding agents, runs a headless
browser for QA, and can self-register throwaway test accounts. Most of its security surface is about
how it handles **credentials** and what it's allowed to run, so please read the notes below.

## Supported versions

Provenship is pre-1.0. Only the latest release on `main` receives security fixes.

| Version | Supported |
|---|---|
| latest `main` / newest release | ✅ |
| older | ❌ |

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

- Preferred: open a private [GitHub Security Advisory](https://github.com/RudreshNarwal/provenship/security/advisories/new).
- Or email **rudresh@rhobots.ai** with "Provenship security" in the subject.

Include what you found, how to reproduce it, and the impact. Expect an acknowledgement within a few
days. Once a fix ships we'll credit you in the advisory unless you'd rather stay anonymous.

## Good to know when running Provenship

- **Credentials never get committed.** QA credentials live in env vars or the gitignored
  `.claude/finalize-creds.json`; only the finalize report and screenshots are committed, with secrets
  redacted. If you ever see a credential in a report or commit, that's a bug — report it.
- **Self-registration is non-prod only.** Provenship will self-register a test account against
  local/dev/staging targets, **never** production.
- **Autonomy ≠ unrestricted.** Autonomous mode removes *questions to the user*, not harness
  permissions. Pair it with a scoped `.claude/settings.json` allowlist. Treat
  `--dangerously-skip-permissions` as sandbox-only.
- **Vendored skills are pinned.** Bundled skills are verbatim, version-pinned upstream copies (see
  `VENDORED.md`); re-sync only via `scripts/sync-vendored.sh`.
