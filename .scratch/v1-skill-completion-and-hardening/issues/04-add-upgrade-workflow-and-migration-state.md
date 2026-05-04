## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Add an `/upgrade-workflow` command and extend the artifact validator to emit `migration_required` state instead of silently rejecting stale artifacts.

Two deliverables:

**`/upgrade-workflow` command** — prompt file + agent file (1-layer, no schema). When invoked, the agent scans `.github/tasks/` for all task artifacts, reads each artifact's `schema_version` from its `validated_under` block, compares it against the current schema version, and emits per-artifact status:
- `compatible` — schema version matches, no action needed
- `migration_required` — schema version is older; artifact is missing required fields added since generation; re-run the originating phase command to regenerate
- `regenerate` — schema version is unknown or unreadable; full regeneration required

**Validator `migration_required` state** — extend `validate-artifact` to detect when a known artifact type has a schema version mismatch and emit a structured `migration_required` verdict with: artifact path, current schema version found, expected schema version, and which required fields are missing. Must not silently reject or produce a generic validation error.

## Acceptance criteria

- [ ] `.github/prompts/upgrade-workflow.prompt.md` exists and references the agent via `#file:`
- [ ] `.github/agents/upgrade-workflow.agent.md` exists with correct `tools: [read, search]` and upgrade scan logic
- [ ] Running `/upgrade-workflow` on a tasks directory containing a stale `LegacyExplorationRecord` (missing new monolith fields) emits `migration_required` for that artifact
- [ ] Running `/upgrade-workflow` on a tasks directory with all current-schema artifacts emits `compatible` for each
- [ ] `validate-artifact` emits `migration_required` (not a generic schema validation error) when a known artifact has a schema version mismatch
- [ ] `migration_required` output includes: artifact path, found schema version, expected schema version, list of missing required fields

## Blocked by

[02 — Add VERSION file, CHANGELOG, and INSTALL.md Upgrading section](02-add-versioning-files.md)
