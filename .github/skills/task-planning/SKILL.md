---
name: task-planning
description: Use when planning a task, diagnosing a bug, or classifying quick work before any edits.
---

# task-planning

Use this skill for `/plan`.

## Purpose

Produce an execution-ready PlanRecord or explicitly stop at `DIAGNOSIS_REQUIRED`.

## Use When

- A user asks to plan a task.
- A bug or regression needs diagnosis before edits.
- A small task may qualify for quick-task classification.

## Instructions

- Create or update `.github/tasks/TASK-{NNN}/plan.json`.
- Populate `created_at` with the artifact creation time in ISO 8601 format.
- Read `.github/workflow/graph-record.json` and `graphify-out/GRAPH_REPORT.md` before selecting intended files. Graph state and module relationships must inform scope decisions before any broad repository search.
- For tasks that are not quick tasks with `graph_light_planning_allowed=true`, run `graphify query "<question>"` to traverse cross-file relationships before selecting intended files.
- Declare intended files, risk class, verification command, graph freshness mode, selected `graph_refs[]`, and structured `graph_usage`.
- Set `graph_usage.required=true` for every plan.
- Set `graph_usage.status` to exactly one of `used`, `skipped-with-approval`, or `unavailable`.
- For non-quick tasks with `graph_usage.status=used`, record non-empty `graph_usage.graph_refs`.
- Populate `graph_scope` for every plan: relevant modules, directly intended files, nearby files intentionally excluded, graph-discovered risk notes, and a concrete graph-to-plan decision.
- `graph_scope.graph_to_plan_decision` must say how graph context changed or constrained scope. Do not write vague statements like "Graphify was checked."
- Keep `graph_scope.nearby_but_out_of_scope` separate from `intended_files`; do not include files just because Graphify mentioned them.
- If Graphify reveals test, documentation, or configuration files, either include them in `graph_scope.in_scope_files` when they are intended work or list them under `nearby_but_out_of_scope` with the reason.
- For graph-light quick tasks, set `quick_task_classification.graph_light_planning_allowed=true` and explain why.
- Never silently skip Graphify. If Graphify is unavailable or skipped, record the reason and required approval.
- If the bug is unclear, set planning status to `DIAGNOSIS_REQUIRED`.
- Do not produce an execution-ready plan until root cause, evidence, affected files, and verification strategy are explicit.
- Before producing an execution-ready plan, verify key assumptions against official documentation when the task involves external APIs, CLIs, frameworks, or specifications.
- Represent quick tasks as `quick_task_classification` inside PlanRecord.
- Quick tasks still require intended files, risk, verification command, graph freshness mode, and human approval before edits.
- Record assumptions, deviations, planning notes, context refs, and diagnosis evidence inside PlanRecord.
- Require human approval before `/execute`.

## Must Not

- Expose `/quick-task` as a user-facing command.
- Create separate debugging, TDD, safe-refactor, or legacy-explore commands.
- Approve execution.
