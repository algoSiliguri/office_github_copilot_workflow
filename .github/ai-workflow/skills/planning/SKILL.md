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
May create only a PlanArtifact.
May not edit source files.

## Required policies
workflow-policy.v1
retrieval-policy.v1
review-policy.v1

## Required schemas
plan.schema.v1

## Required validators
validate-artifact
validate-plan-scope

## Procedure
1. Load manifest, command contract, policies, and schema.
2. Read the input grill record and refuse if decision is not proceed.
3. Ground the plan in the grill record approach decisions.
4. Declare files in scope and out of scope explicitly.
5. Declare whether a context packet is required.
6. Declare the preferred execution surface per step.
7. Declare the exact verification command.
8. Save plan to task folder.
9. Run validators.

## Failure behavior
Missing required dependency blocks.
GrillRecord decision not proceed blocks plan creation.
Unreviewable scope or verification blocks.

## Handoff/output format
Return the PlanArtifact and concise result.
