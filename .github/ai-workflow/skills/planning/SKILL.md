# write-plan

## Skill purpose
Convert a valid grill record into a reviewable implementation plan with bounded scope and declared verification.

## Implemented command contract
write-plan.v1

## Required inputs
GrillRecord.

## Produced outputs
PlanArtifact.

## Authority limits
May create a PlanArtifact.
May update the TaskManifest for this task.
May not edit source files.

## Required policies
workflow-policy.v1
retrieval-policy.v1
review-policy.v1

## Required schemas
plan.schema.v1

## Required validators
validate-artifact
validate-artifact-path
validate-plan-scope

## Procedure
1. Load manifest, command contract, policies, and schema.
2. Read the input grill record and refuse if decision is not proceed.
3. Ground the plan in the grill record approach decisions.
4. If the grill references a DiagnosisRecord, record `diagnosis_confidence_gate`. Low-confidence diagnosis blocks production fixes; only reproduction tests, instrumentation, or test-surface improvements may proceed.
5. Declare files in scope and out of scope explicitly.
6. Declare whether a context packet is required.
7. Record `retrieval_decision` as `used | skipped | unavailable` with reasons and files considered. This decision is mandatory even when retrieval is skipped.
8. Record `tdd_decision`. TDD is required for behavior changes, bugfixes, shared logic, public APIs, persistence/data shape, permissions/security, and cross-module behavior. It is not required for docs-only, comments-only, formatting-only, or pure workflow metadata changes.
9. Declare the preferred execution surface per step.
10. Declare the exact verification command.
11. Save plan to task folder.
12. If `plan.json` already exists, preserve it under `attempts/plan/<ISO_TIMESTAMP>.json` before replacement.
13. Update TaskManifest: phase → plan, artifact_refs.plan → path.
14. Run validators.

## Failure behavior
Missing required dependency blocks.
GrillRecord decision not proceed blocks plan creation.
Unreviewable scope or verification blocks.

## Handoff/output format
Return the PlanArtifact and concise result.
