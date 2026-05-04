## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Extend `LegacyExplorationRecord` schema with five structured monolith-safety fields. These fields make risk machine-readable for downstream `/write-plan` consumption. Generic `findings[]` and `risks[]` string arrays are insufficient — a plan agent reading `has_generated_code: true` acts differently than one scanning prose for the phrase "generated files present."

New required fields:

```yaml
blast_radius:
  affected_files: integer
  affected_modules: integer
  caller_count: integer
  confidence: low | medium | high

test_surface_quality: low | medium | high

has_generated_code: boolean

has_stored_procedures: boolean

planning_constraints:
  - string   # e.g. "slow build — full rebuild required on module change"
```

All five fields are required. Values may be `"unknown"` with `confidence: low` where automated detection is inconclusive. Silent omission is not acceptable — unknown must be stated explicitly.

Update `validate-artifact` and `validate-manifest` to recognize the new schema version. Bump `schema_version` in the schema file. Add a migration note to `CHANGELOG.md`.

## Acceptance criteria

- [ ] `legacy-explore.schema.json` contains all five new fields as required properties
- [ ] `blast_radius` is a required object with `affected_files`, `affected_modules`, `caller_count`, `confidence` sub-fields
- [ ] `test_surface_quality` accepts only `low | medium | high`
- [ ] `has_generated_code` and `has_stored_procedures` are boolean
- [ ] `planning_constraints` is a required string array (may be empty)
- [ ] `schema_version` bumped in the schema file
- [ ] `validate-artifact` accepts a valid artifact with all new fields present
- [ ] `validate-artifact` emits `migration_required` (not hard failure) for artifacts missing new fields
- [ ] `CHANGELOG.md` entry documents the new fields and states which artifact type is affected

## Blocked by

[04 — Add `/upgrade-workflow` command and `migration_required` validator state](04-add-upgrade-workflow-and-migration-state.md)
