# Changelog

All notable changes to Shipwright are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Dynamic per-model cost pricing in `cost-table.py`.** Rates are now looked up per model from
  LiteLLM's community price list (the source `ccusage` uses), fetched once and cached 24h under
  `~/.cache/shipwright/`. Any model missing from the live data falls back to the bundled static table;
  `--offline` forces the bundled rates and `--refresh` busts the cache. The report header now states
  which pricing source was used per model (live vs bundled fallback) and reminds that token counts are
  exact while dollar costs are estimates. Removes the stale hand-maintained-only pricing.
- **Phase 5 QA escalation / loop-back.** QA findings bigger than a local fix are now triaged
  (architecture → re-plan, design → re-design, scope → re-scope) and loop back to the right earlier
  phase for the affected slice only. Interactive mode asks for confirmation first; autonomous mode
  loops back automatically, except a product/scope redefinition stops and surfaces.
- **`frontend-design` is now vendored** (Apache-2.0 © Anthropic, pinned commit `ac16ffafcd70`) under
  `shipwright:frontend-design`, so UI work needs nothing extra installed. Its license is preserved at
  `licenses/frontend-design.LICENSE`.
- **Brand & visual identity** — SVG logo (hull-that-resolves-into-a-checkmark), light/dark lockups,
  square icon, and README badges.
- Open-source launch files: `SECURITY.md`, `CHANGELOG.md`, and a pull-request template.

## [0.1.0] - 2026-06-13

### Added
- Initial Shipwright plugin: the six-phase pipeline (Brainstorm → Plan → Build → Review → QA →
  Finalize+Ship) with a Phase-0 preflight and a single autonomy gate.
- Vendored MIT skills from superpowers (v5.1.0) and andrej-karpathy-skills (v1.0.0), re-namespaced to
  `shipwright:`.
- gstack declared as a runtime dependency with `scripts/install-gstack.sh`.
- `cost-table.py` per-stage token/cost attribution, vendoring sync + lint scripts, CI, and docs.

[Unreleased]: https://github.com/RudreshNarwal/shipwright/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/RudreshNarwal/shipwright/releases/tag/v0.1.0
