# /context-packet

Build a bounded context packet for plan execution when the plan declares `context_packet_required: true`.

## Pre-conditions

Read the PlanArtifact for this task. Confirm `context_packet_required: true`. If false, tell the user this phase is not needed.

## What to retrieve

Load only files listed in `plan.files_in_scope` plus any files they directly import or reference. Do not expand beyond one hop.

## Output

Save a `ContextPacketArtifact` JSON document to the path declared in `plan.context_packet_path`.

Required fields:
- `artifact_type: ContextPacketArtifact`
- `schema_version: context-packet.schema.v1`
- `task_id`
- `phase_id`
- `source_plan`
- `created_at` — ISO 8601 timestamp
- `generated_at` — ISO 8601 timestamp
- `scope`
- `retrieval_policy`
- `coverage`
- `included_context`
- `execution_decision`
- `validation`
- `validated_under`

After saving, update `.github/tasks/TASK-{NNN}/task-manifest.json`:
- Set `phase: context_packet`
- Set `updated_at: <ISO 8601 timestamp>`
- Set `artifact_refs.context_packet: <context_packet_path>`

After saving, output:

```
STATUS: context-packet complete
TASK: TASK-{NNN}
FILES_LOADED: [N]
ARTIFACT: <context_packet_path from plan>
NEXT: /execute-plan
```
