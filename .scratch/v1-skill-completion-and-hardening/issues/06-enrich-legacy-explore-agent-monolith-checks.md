## Parent

[PRD: v1 Skill Completion and Hardening](../PRD.md)

Status: needs-triage
Type: AFK

## What to build

Extend the `/legacy-explore` agent instructions with five explicit monolith-specific protocol checks. The current agent has 12 lines of instruction — "explore bounded, explain target area, produce record." This is not enough to guide Copilot on a 500k-line monolith with stored procedures, generated code, and weak tests.

Five checks to add (each as a named section in the agent instruction):

1. **Test surface quality** — search for test files adjacent to or covering the target area; count coverage signals; rate as `low` (no tests), `medium` (some tests, weak coverage), `high` (solid test suite); recommend characterization tests when `low`

2. **Generated code detection** — look for generation markers (`@generated`, `DO NOT EDIT`, build tool output headers, proto/thrift/openapi generated stubs); flag any target file that appears generated; record `has_generated_code: true` and do not recommend modifying generated files in the plan

3. **Stored procedure / DB-touching surface** — detect SQL strings, ORM call sites, migration files, repository pattern classes touching the target; flag schema-change risk; record `has_stored_procedures: true` if found; note migration requirement in `planning_constraints`

4. **Blast-radius via caller/import graph** — count direct callers of the target module/function using search; count one-hop dependents; record counts in `blast_radius` with `confidence` reflecting search completeness; flag high caller counts as scope risk

5. **Slow-build / expensive-verification signals** — detect build config files, CI time comments, full-rebuild triggers in Makefile or build scripts adjacent to the target; record slow-build risk in `planning_constraints` (e.g. "full rebuild required on module change")

Rule: if any check is inconclusive, record the field with best-effort values and `confidence: low`. Unknown must be stated. Silent omission is not acceptable.

## Acceptance criteria

- [ ] Agent instructions contain a named section for each of the five protocol checks
- [ ] Agent correctly populates `blast_radius` object including `confidence` field
- [ ] Agent correctly sets `test_surface_quality` to `low | medium | high`
- [ ] Agent correctly sets `has_generated_code` boolean based on marker detection
- [ ] Agent correctly sets `has_stored_procedures` boolean based on DB surface detection
- [ ] Agent appends to `planning_constraints` for slow-build and migration signals
- [ ] Agent explicitly states that generated files must not be recommended for modification in the plan scope
- [ ] Agent output status block is unchanged: `STATUS / TASK / FILES_REVIEWED / DECISION / ARTIFACT / NEXT`

## Blocked by

[05 — Enrich `LegacyExplorationRecord` schema with 5 monolith fields](05-enrich-legacy-exploration-record-schema.md)
