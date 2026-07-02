# Changelog

All notable changes to Provenship are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`/autoplan` refinement triggers in Phases 1–2.** A spec that's still under-refined after
  brainstorming is flagged so Plan hardens it via gstack `/autoplan`, and interactive mode now
  proactively offers `/autoplan` (one line) when the plan is thin or carries open decisions — no
  longer only on request. The autonomous path is unchanged (it already auto-runs it).
- **Optional `/office-hours` hook in Phase 1.** When the input is a raw, unvalidated product idea
  (not a defined feature) and gstack is installed, Provenship pressure-tests what's worth building
  via gstack `/office-hours` before brainstorming how. One conditional line, not a new phase —
  Phases 1–4 stay gstack-free on Codex/OpenCode.
- **Multi-harness install adapters (Codex + OpenCode).** Provenship now ships a `.codex-plugin/plugin.json`
  (Codex reuses the same `skills/`) and an `opencode.json` + `.opencode/plugins/provenship.mjs` (a thin
  plugin that runs the gstack preflight on session start). The README gains a Codex/OpenCode install
  section and a **capability matrix**: Phases 1–4 run on both, while gstack browser-QA/ship and
  `cost-table.py` stay Claude-Code-only. Lightweight adapters only — the end-to-end run on Codex/OpenCode
  is unverified, as the matrix states. `scripts/lint.sh` now validates the two new manifests and
  `node --check`s the plugin.
- **One-command gstack bootstrapper + auto-detect.** `scripts/install-gstack.sh` now installs the whole
  chain — **Bun** (if missing), the **gstack** clone + `./setup`, and **Playwright's Chromium** — and
  takes `--yes` for unattended runs. A new `SessionStart` hook (`hooks/hooks.json` →
  `scripts/preflight-gstack.sh`) auto-detects gstack on session start: silent when present, a one-line
  install message when missing, and an opt-in background install when `PROVENSHIP_AUTO_INSTALL_GSTACK=1`
  is set (opt-in by design — it pulls ~1 GB plus a browser, so it isn't silent by default).
- **Branded pipeline diagram.** `assets/flow.svg` now carries the Provenship logo lockup (hull→checkmark
  mark + wordmark + tagline) over the brand-palette flow.
- **Minimal-code build ladder in the Build phase.** Each implementer subagent is now given an explicit
  ladder to run before writing code (does this need to exist → stdlib → native platform feature →
  already installed → one line → only then a minimal solution), with a guardrail never to trade away
  security/accessibility/data-loss safety for brevity. Inspired by
  [ponytail](https://github.com/DietrichGebert/ponytail) (MIT); complements the bundled karpathy rules
  rather than restating them. Credited in the README (inspiration, not vendored).
- **Benchmark harness (`benchmarks/`).** A control-vs-treatment harness that measures the build
  discipline's effect on generated code — same model and tasks, with the discipline injected into the
  treatment arm only. Captures exact LOC/files/deps/tokens (reusing `cost-table.py`) and a flagged
  dollar estimate, reports medians with spread and pass-rates, and enforces an honest publish gate
  (N≥10 across ≥5 tasks, matched pass-rates) before any number may reach the README.
- **README sections** — *How it works*, *Before / after* (narrative, no fabricated metrics), *Numbers*
  (honest placeholder pending real benchmark runs), and an *FAQ* including an opencode / other-tool
  compatibility note (Phases 1–4 likely workable on opencode; gstack and the transcript cost table are
  the blockers).
- **Dynamic per-model cost pricing in `cost-table.py`.** Rates are now looked up per model from
  LiteLLM's community price list (the source `ccusage` uses), fetched once and cached 24h under
  `~/.cache/provenship/`. Any model missing from the live data falls back to the bundled static table;
  `--offline` forces the bundled rates and `--refresh` busts the cache. The report header now states
  which pricing source was used per model (live vs bundled fallback) and reminds that token counts are
  exact while dollar costs are estimates. Removes the stale hand-maintained-only pricing.
- **Phase 5 QA escalation / loop-back.** QA findings bigger than a local fix are now triaged
  (architecture → re-plan, design → re-design, scope → re-scope) and loop back to the right earlier
  phase for the affected slice only. Interactive mode asks for confirmation first; autonomous mode
  loops back automatically, except a product/scope redefinition stops and surfaces.
- **`frontend-design` is now vendored** (Apache-2.0 © Anthropic, pinned commit `ac16ffafcd70`) under
  `provenship:frontend-design`, so UI work needs nothing extra installed. Its license is preserved at
  `licenses/frontend-design.LICENSE`.
- **Brand & visual identity** — SVG logo (hull-that-resolves-into-a-checkmark), light/dark lockups,
  square icon, and README badges.
- Open-source launch files: `SECURITY.md`, `CHANGELOG.md`, and a pull-request template.

### Changed
- **README pipeline diagram is now dark-themed.** `assets/flow.svg` was recolored (same geometry,
  colors only) so it reads on GitHub dark mode, where the light version's slate header/wordmark
  vanished. Badge numbers and the end pill flipped to dark slate for contrast on the brighter
  teal→green gradient (matching `logo-dark.svg`).

## [0.1.0] - 2026-06-13

### Added
- Initial Provenship plugin: the six-phase pipeline (Brainstorm → Plan → Build → Review → QA →
  Finalize+Ship) with a Phase-0 preflight and a single autonomy gate.
- Vendored MIT skills from superpowers (v5.1.0) and andrej-karpathy-skills (v1.0.0), re-namespaced to
  `provenship:`.
- gstack declared as a runtime dependency with `scripts/install-gstack.sh`.
- `cost-table.py` per-stage token/cost attribution, vendoring sync + lint scripts, CI, and docs.

[Unreleased]: https://github.com/RudreshNarwal/provenship/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/RudreshNarwal/provenship/releases/tag/v0.1.0
