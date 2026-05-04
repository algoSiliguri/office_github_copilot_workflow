# /quick-task

Lightweight path for small, low-risk changes. Automatically escalates to `/grill` when scope, risk, or uncertainty grows.

## Escalation check (run BEFORE making any changes)

Evaluate all four triggers. If ANY fires, escalate immediately:

| Trigger | Condition |
|---|---|
| Scope | Files to touch > 3 |
| Risk | Change touches auth, infra, schema, config, or migrations |
| Uncertainty | Task description contains "maybe", "not sure", "depends", "could be", or similar |
| Unknown decisions | More than 1 decision point that requires architectural judgment |

If escalation triggered:
1. Do NOT make any changes.
2. Tell the user which trigger fired.
3. Output:

```
STATUS: escalated
REASON: <which trigger(s) fired>
NEXT: /grill — run this instead
```

Save a QuickTaskRecord with `escalation_triggered: true`, `status: ESCALATED_TO_FULL_WORKFLOW`, and the reason list populated.

## Execution (no escalation)

If no triggers fire:
1. Make the change directly — no plan required.
2. Keep changes to declared files only.
3. Save a QuickTaskRecord to `.github/tasks/TASK-{NNN}/quick-task.yaml`.

Required fields:
- `artifact_type: QuickTaskRecord`
- `schema_version: quick-task.schema.v1`
- `task_id` — next sequential ID
- `primary_surface: copilot_plugin`
- `secondary_surfaces_allowed: [copilot_cli]`
- `task_summary` — one sentence
- `files.planned` — exact list of files expected before editing
- `files.actual` — actual edited files after execution
- `change_class.value`
- `change_class.policy_allowed`
- `change_class.classification_status: locked_for_execution`
- `change_class.public_behavior_change: false`
- `verification.command`
- `verification.evidence` — must be real evidence (test output, build output, run output, or before/after behavior note). See allowed evidence types:

#file:.github/ai-workflow/protocols/verification-gate.md
- `escalation_triggered: false`
- `escalation_reason: []`
- `status: PASS_QUICK` (or `FAIL` if something went wrong)
- `validated_under` — exact workflow/command/schema/config tuple

After saving, output:

```
STATUS: quick-task complete
TASK: TASK-{NNN}
FILES: [list of files touched]
ARTIFACT: .github/tasks/TASK-{NNN}/quick-task.yaml
```
