# /diagnose

Structured bug investigation: reproduce → hypothesise → instrument → fix → post-mortem. Hands off the fix to /write-plan or /quick-task.

#file:.github/agents/diagnose.agent.md

## v1 authority

`/diagnose` may read bounded files and run safe reproduction commands. It may not edit source files.

## Output

Save a DiagnosisRecord to `.github/tasks/TASK-{NNN}/diagnosis.json` and create/update `.github/tasks/TASK-{NNN}/task-manifest.json` with `artifact_refs.diagnosis` populated.

Required DiagnosisRecord fields:
- `artifact_type: DiagnosisRecord`
- `schema_version: diagnosis.schema.v1`
- `task_id`
- `task_type: bugfix`
- `primary_surface`
- `bug_summary`
- `reported_behavior`
- `expected_behavior`
- `reproduction: { command, output, reproduced }`
- `minimal_case`
- `hypotheses[]` with `id`, `summary`, `prediction`, `evidence`, `status`
- `suspected_root_cause`
- `recommended_files_in_scope[]`
- `recommended_files_out_of_scope[]`
- `test_surface`
- `confidence`
- `decision: proceed | blocked`
- `open_blockers[]` when blocked
- `created_at`
- `validated_under`

If `decision: proceed`, recommend `/grill` using the DiagnosisRecord as source context. If the fix is tiny and policy-allowed, recommend `/quick-task`.
