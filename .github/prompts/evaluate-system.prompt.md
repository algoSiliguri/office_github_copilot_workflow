# /evaluate-system

Evaluate whether the workflow system is working across completed tasks. This is a retrospective over artifacts, not a source-code review and not an automatic self-improvement step.

## Purpose

The user should not have to inspect raw logs manually. Convert task artifacts into a short decision report:

1. What repeatedly failed?
2. Which metric proves it?
3. Which part of the agentic stack is most likely implicated?
4. What workflow improvement should the human approve for a `/grill` session?

## Inputs

Read completed task folders under `.github/tasks/TASK-{NNN}/`.

For each task, prefer confirmed or overridden `evaluation.json`. If evaluation is missing, record that task as unavailable and exclude it from metric denominators.

Read upstream artifact refs only when needed to explain a repeated pattern. Do not scan source code. Do not edit files.

## Evidence Policy

Use structured JSON artifacts first:

- `evaluation.json`
- `review.json`
- `verification.json`
- `execution.json`
- `plan.json`
- `grill.json`
- `diagnosis.json` when present
- `task-manifest.json`

Do not read or summarize raw logs by default.

Read raw logs only when:

- A metric or repeated pattern cannot be explained from structured artifacts.
- A human override/rejection references a missing or ambiguous detail.
- A verification or execution artifact points to a specific log file as evidence.

When raw logs are used:

- Read only the smallest relevant file/section.
- Cite the log path in `evidence_refs`.
- Summarize the signal, not the whole log.
- Do not include long raw output in the user-facing report.

## Trigger Policy

Do not run this after every task by default. Run `/evaluate-system` when:

- At least 5 tasks have confirmed or overridden evaluations since the last system evaluation.
- Any task evaluation was human-overridden.
- Any review/evaluation had a human rejection.
- The user is about to change prompts, schemas, validators, command contracts, policies, or workflow instructions.
- The user explicitly asks whether the system is working or what to improve from logs.

If none of these triggers apply, tell the user to continue collecting task evaluations instead of producing a low-signal report.

## Metrics

Aggregate these separately:

- `success_rate`: tasks with `EvaluationRecord.outcome == success` divided by evaluated tasks.
- `process_pass_rate`: tasks with `process_quality.status == pass` divided by evaluated tasks.
- `human_override_rate`: tasks with `evaluation_status == overridden` divided by evaluated tasks.
- `scope_violation_count`: tasks where score/process scope adherence is false.
- `verification_failure_count`: tasks where verification status is FAILED or BLOCKED.
- `tdd_noncompliance_count`: tasks where TDD was required but not followed.
- `retrieval_decision_missing_count`: tasks missing retrieval decision.
- `diagnosis_missing_when_required_count`: tasks where required diagnosis was not used.

## Pattern Rules

Do not treat a single bad task as a system problem unless severity is high.

A repeated problem pattern requires:

- Frequency >= 2 in the selected sample, or
- Frequency == 1 with high severity and direct human rejection/override.

Map each pattern to one likely implicated component. This is a diagnostic hypothesis, not blame.

- `model`
- `system_prompt`
- `tool_permissions`
- `context_window_usage`
- `retrieval_strategy`
- `session_state`
- `hidden_summaries`
- `test_feedback`
- `user_workflow`
- `workflow_contract`
- `schema`
- `validator`
- `unknown`

If unsure, use `unknown`. Do not invent certainty. Every non-`unknown` component must be supported by `evidence_refs`.

## Output

Save the report to:

`.github/tasks/system-evaluations/SYS-EVAL-{YYYYMMDD}-{HHMMSS}/system-evaluation.json`

Required fields:

- `artifact_type: SystemEvaluationReport`
- `schema_version: system-evaluation.schema.v1`
- `evaluation_id`
- `created_at`
- `source_task_refs`
- `sample_window`
- `aggregate_metrics`
- `repeated_problem_patterns`
- `improvement_candidates`
- `human_decision_request`
- `validated_under`

If raw logs were consulted, include their paths in the relevant `repeated_problem_patterns[].evidence_refs`. If no raw logs were needed, do not mention them.

After writing, present this block:

```text
--- SYSTEM EVALUATION ---
Evaluated tasks: <N>
Success rate: <success_rate>
Process pass rate: <process_pass_rate>
Human override rate: <human_override_rate>

Top repeated problems:
1. <pattern_id>: <problem> | frequency=<N> | component=<component>

Recommended human decision:
<human_decision_request.question>

Options:
- <option>

Next command:
/grill task_type=system_improvement triggered_by=<system-evaluation.json> failure_category=<top pattern id>
---
```

Do not apply any workflow change from this report. A human must choose an improvement candidate and run `/grill`.
