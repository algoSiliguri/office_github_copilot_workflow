# execute-plan

## Skill purpose
Execute a valid plan without expanding scope silently.

## Implemented command contract
execute-plan.v1

## Required inputs
PlanArtifact and ContextPacketArtifact when the plan says one is required.

## Produced outputs
ExecutionRecord plus code changes and evidence for `/verify`.

## Authority limits
May modify only files declared in the active plan.
May update the TaskManifest for this task.
Must stop if scope or risk changes.

## Required policies
workflow-policy.v1
context-policy.v1

## Required schemas
plan.schema.v1
execution-checkpoint.schema.v1

## Required validators
validate-manifest
validate-artifact
validate-plan-scope
validate-compatibility

## Procedure
1. Load manifest, contract, policy, and input plan.
2. Validate the plan before editing.
3. If the plan requires a context packet, stop unless a valid packet is present in a proceed state.
4. If `plan.tdd_decision.required` is true, execute the task through a test-first loop: failing test or reproduced failure signal, minimal implementation, verification, then refactor. Record evidence in `ExecutionRecord.tdd_execution`.
5. Execute only the declared scope.
6. Produce an ExecutionRecord recording touched files, TDD evidence, command evidence, and context state.
7. If `execution.json` already exists, preserve it under `attempts/execution/<ISO_TIMESTAMP>.json` before replacement.
8. Update TaskManifest: phase → execution, artifact_refs.execution → path; status → blocked if escalated.
9. Stop and escalate back to planning if scope changes.

## Failure behavior
Missing required dependency blocks.
Scope or risk expansion stops execution.
Missing required context packet blocks before edits.

## Handoff/output format
Return the ExecutionRecord and direct the workflow to `/verify`.
