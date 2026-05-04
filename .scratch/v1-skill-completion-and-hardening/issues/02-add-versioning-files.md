## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add the human-readable versioning infrastructure that lets teams know which bundle version they are running and what changed between upgrades.

Three deliverables:
1. `VERSION` file at `.github/` root — single semver line (e.g. `1.0.0`)
2. `CHANGELOG.md` at `.github/` root — append-only, one section per version listing schema changes, new required fields, and breaking changes with migration notes
3. An Upgrading section added to `.github/docs/INSTALL.md` — steps: check CHANGELOG → run CLI validators → handle `migration_required` artifacts → regenerate affected phases if needed

The `CHANGELOG.md` entry for `1.0.0` should document all schema fields added in this hardening work as the baseline.

## Acceptance criteria

- [ ] `VERSION` file exists at `.github/VERSION`, contains a valid semver string
- [ ] `CHANGELOG.md` exists at `.github/CHANGELOG.md`, has a `## [1.0.0]` section
- [ ] `CHANGELOG.md` section lists the 5 new `LegacyExplorationRecord` fields added in this work
- [ ] `INSTALL.md` contains an `## Upgrading` section with the four-step upgrade path
- [ ] `CHANGELOG.md` format is append-only (new versions prepended at top, old entries never edited)

## Blocked by

None — can start immediately.
