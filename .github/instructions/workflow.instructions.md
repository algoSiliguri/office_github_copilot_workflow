---
applyTo: ".github/**"
---

# Workflow file editing rules

These rules apply whenever you edit any file under `.github/`.

## Schema changes

- Increment `schema_version` in the changed schema file
- Update all example artifacts in `artifacts/examples/` that reference that schema

## Contract changes

- Update corresponding validator test artifacts before marking the change complete

## Validator changes

- Add or update test artifacts in `.github/ai-workflow/artifacts/examples/` before shipping
- Run `validate-artifact` against all examples and confirm the pass/fail matrix is correct

## Governance files (Tier 4)

Manifest, schemas, and validators require explicit human instruction before editing.
Files in scope: `manifest.yaml`, `*.schema.json`, `validators/*`

## Portability

- Never embed repo-specific values in prompts or agents
- Repo-specific values belong in `.github/workflow/config.yaml` only
- The `.github/` folder must remain drop-in portable across repos

## Scope enforcement

Edits to `.github/ai-workflow/` must not touch files outside `.github/` unless those files are explicitly declared in a `PlanArtifact` scope.

## Evaluation and improvement loop

- `/review` with status PASS or PASS_WITH_DEGRADATION automatically triggers `/evaluate`.
- `/evaluate` produces a draft EvaluationRecord. Human confirms or overrides before it becomes authoritative.
- EvaluationRecord is the terminal artifact of every completed task.
- To improve the system after repeated failures: create a new `/grill` task with `task_type: system_improvement` and populate `triggered_by` with the relevant EvaluationRecord paths. Run the full workflow. No automated system file mutations.
- `triggered_by` is required on all GrillRecords where `task_type: system_improvement`. Missing it fails schema validation.
