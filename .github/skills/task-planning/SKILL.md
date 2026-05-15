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
- Declare intended files, risk class, verification command, graph freshness mode, and selected `graph_refs[]`.
- If the bug is unclear, set planning status to `DIAGNOSIS_REQUIRED`.
- Do not produce an execution-ready plan until root cause, evidence, affected files, and verification strategy are explicit.
- Before producing an execution-ready plan, verify key assumptions against official documentation when the task involves external APIs, CLIs, frameworks, or specifications.
- Use graph_refs as the primary exploration boundary before broad repository search.
- Represent quick tasks as `quick_task_classification` inside PlanRecord.
- Quick tasks still require intended files, risk, verification command, graph freshness mode, and human approval before edits.
- Record assumptions, deviations, planning notes, context refs, and diagnosis evidence inside PlanRecord.
- Require human approval before `/execute`.

## Must Not

- Expose `/quick-task` as a user-facing command.
- Create separate debugging, TDD, safe-refactor, or legacy-explore commands.
- Approve execution.
