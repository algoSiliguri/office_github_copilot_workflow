# Changelog

All schema changes, new required fields, and breaking changes are documented here.
Format: `## [version] — YYYY-MM-DD`. New versions prepended at top. Old entries never edited.

---

## [1.0.0] — 2026-05-04

### Baseline release

**Agent tool declarations**
- Fixed invalid `tools: [codebase]` in all four agent files. `codebase` is not a recognized tool name and was silently ignored, leaving all agents with unrestricted tool access.
- Correct mappings: `grill`, `write-plan`, `legacy-explore` → `[read, search]`; `execute-plan` → `[read, edit, search, execute]`

**New support skills (1-layer)**
- `/diagnose` — disciplined bug investigation loop
- `/tdd` — red-green-refactor loop grounded in repo test runner
- `/safe-refactor` — bounded refactor planning with blast-radius analysis
- `/zoom-out` — lightweight codebase orientation, no artifact, no gate
- `/grill-with-docs` — doc-grounded grill variant, degrades to `/grill` when no docs exist

**`LegacyExplorationRecord` schema — breaking change**
- Added 5 new required fields: `blast_radius`, `test_surface_quality`, `has_generated_code`, `has_stored_procedures`, `planning_constraints`
- **Migration:** existing `LegacyExplorationRecord` artifacts from before this version will be flagged `migration_required` by `validate-artifact`. Re-run `/legacy-explore` for any affected task to regenerate.

**Protocol surface wiring**
- `verification-gate.md` → wired to `/verify` and `/quick-task` agents
- `stage-review.md` → wired to `/review` agent
- `phase-checkpoint.md` → wired to `/execute-plan` agent
- `retrieval-decision.md` → wired to `/write-plan` agent

**Versioning infrastructure**
- Added `VERSION` file at `.github/VERSION`
- Added this `CHANGELOG.md`
- Added `## Upgrading` section to `INSTALL.md`
- Added `/upgrade-workflow` command
- `validate-artifact` now emits `migration_required` state on schema version mismatch instead of hard failure
