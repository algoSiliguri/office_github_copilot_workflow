# System Evaluation

Use this skill when the user asks whether the workflow system is working, wants to inspect logs, wants recurring metrics, or asks what to improve based on prior task artifacts.

## Core Rule

Logs are not user homework. Convert logs into a small decision report with metrics, repeated patterns, and ranked human choices.

## Method

1. Read completed task folders under `.github/tasks/TASK-{NNN}/`.
2. Prefer confirmed or overridden `evaluation.json` files.
3. Aggregate task outcome separately from process quality.
4. Identify repeated problem patterns only when supported by evidence refs.
5. Map each pattern to one likely implicated stack component as a hypothesis, not blame.
6. Produce a `SystemEvaluationReport`.
7. Recommend `/grill task_type=system_improvement ...` for the highest-impact candidate.

## Evidence Policy

Structured artifacts are the primary evidence. Raw logs are secondary evidence only.

Read raw logs only when a metric or repeated pattern cannot be explained from structured artifacts, or when an upstream artifact explicitly points to a specific log file. If raw logs are used, cite the path and summarize only the relevant signal.

Use `implicated_component: unknown` when evidence does not support a specific component. Do not force a blame assignment.

## Trigger Policy

Run periodically, not after every task. Recommended triggers:

- 5 evaluated tasks since the last system evaluation.
- Any human override or rejection.
- Before changing prompts, schemas, validators, command contracts, policies, or workflow instructions.
- Explicit user request to evaluate logs or system quality.

## Constraints

Do not bulk-read raw logs. Do not edit source code, prompts, schemas, validators, command contracts, or policies.

Do not claim the system self-improved. V1 only observes, summarizes, and asks for human approval.
