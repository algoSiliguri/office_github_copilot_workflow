# /quick-task

Lightweight path for small, low-risk changes. Automatically escalates to `/grill` when scope, risk, or uncertainty grows.

## Eligibility check (run BEFORE making any changes)

Evaluate ALL eight rules. If ANY fails, escalate immediately:

| Rule | Pass condition |
|------|----------------|
| File count | Files to touch ≤ 2 |
| Protected files | No changes to schema, validator, policy, manifest, contract, prompt, skill, instruction, agent, VERSION, CHANGELOG, or CI files |
| Architecture | No architectural or design decision required |
| Clarity | Acceptance criteria are clear and unambiguous |
| Module boundary | No cross-module behavior changes |
| Risk | No security, data, migration, or release impact |
| Verification | Can be verified with one simple command or direct inspection |
| Acceptance | User has explicitly accepted quick-task mode |
| Gate bypass | Retrieval, TDD, and full evaluation can each be safely bypassed with a concrete reason |

If escalation triggered:
1. Do NOT make any changes.
2. Tell the user which trigger fired.
3. Output:

```
STATUS: escalated
REASON: <which trigger(s) fired>
NEXT: /grill — run this instead
```

Save a QuickTaskRecord with `escalation_triggered: true`, `status: ESCALATED_TO_FULL_WORKFLOW`, the reason list populated, and `eligibility_check` with `all_passed: false` and the failed rule names in `failures`.

## Execution (no escalation)

If no triggers fire:
1. Make the change directly — no plan required.
2. Keep changes to declared files only.
3. Save a QuickTaskRecord to `.github/tasks/TASK-{NNN}/quick-task.json`.

Required fields:
- `artifact_type: QuickTaskRecord`
- `schema_version: quick-task.schema.v1`
- `task_id` — next sequential ID
- `primary_surface: copilot_plugin`
- `secondary_surfaces_allowed: [copilot_cli]`
- `task_summary` — one sentence
- `created_at` — ISO 8601 timestamp
- `files.planned` — exact list of files expected before editing
- `files.actual` — actual edited files after execution
- `change_class.value`
- `change_class.policy_allowed`
- `change_class.classification_status: locked_for_execution`
- `change_class.public_behavior_change: false`
- `bypass_justification.retrieval_decision: { bypassed: true, reason }`
- `bypass_justification.tdd_decision: { bypassed: true, reason }`
- `bypass_justification.evaluation_decision: { bypassed: true, reason }`
- `verification.command`
- `verification.evidence` — must be real evidence (test output, build output, run output, or before/after behavior note). See allowed evidence types:

#file:.github/ai-workflow/protocols/verification-gate.md
- `escalation_triggered: false`
- `escalation_reason: []`
- `eligibility_check` — `all_passed: true`, `failures: []`, all 9 rules listed in `rules_evaluated` with `passed: true`
- `status: PASS_QUICK` (or `FAIL` if something went wrong)
- `validated_under` — exact workflow/command/schema/config tuple

After saving, output:

```
STATUS: quick-task complete
TASK: TASK-{NNN}
FILES: [list of files touched]
ARTIFACT: .github/tasks/TASK-{NNN}/quick-task.json
```
