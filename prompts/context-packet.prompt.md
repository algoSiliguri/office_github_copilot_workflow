# /context-packet

Build a bounded context packet for plan execution when the plan declares `context_packet_required: true`.

## Pre-conditions

Read the PlanArtifact for this task. Confirm `context_packet_required: true`. If false, tell the user this phase is not needed.

## What to retrieve

Load only files listed in `plan.files_in_scope` plus any files they directly import or reference. Do not expand beyond one hop.

## Output

Save a context summary to the path declared in `plan.context_packet_path`. The file should contain:
- Task ID and plan reference
- List of files loaded with one-line summary of each
- Key symbols, types, or interfaces relevant to the plan steps
- Any surprising dependencies or constraints discovered

After saving, output:

```
STATUS: context-packet complete
TASK: TASK-{NNN}
FILES_LOADED: [N]
ARTIFACT: <context_packet_path from plan>
NEXT: /execute-plan
```
