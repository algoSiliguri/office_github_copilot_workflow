---
name: verification-review
description: Use when proving task results with real checks and human review after execution.
---

# verification-review

Use this skill for `/verify`.

## Purpose

Prove task results with real checks and review before human acceptance.

## Use When

- ExecutionRecord exists after `/execute`.
- The user asks to verify or review task completion.

## Instructions

- Run the approved verification command. Command execution and its exit code are the primary verification evidence — not graph data, graph refs, or graph structure.
- Create VerificationRecord with `created_at`, command refs, result, and short safe evidence summaries.
- Create ReviewRecord with `created_at` comparing actual changed files against both `intended_files` from the PlanRecord and the approved graph scope from `graph_scope.in_scope_files`.
- Record whether graph context was used and which graph_refs from the PlanRecord influenced the task.
- Do not use graph data as correctness evidence. Graphify is a map for planning and review context, not a test result.
- Populate `graph_scope_review` to classify actual changed files inside approved graph scope, outside approved graph scope, graph-near drift, and graph-unrelated drift.
- Flag graph-unrelated drift explicitly: any file changed outside approved graph scope and not covered by an approved deviation must be flagged as graph-unrelated drift and treated as higher risk than graph-near drift.
- Require scope-drift approval for files outside the approved plan, graph scope, and approved deviations.
- Treat tests, checks, diff scope, and human review as authoritative.
- Require human approval for final result, scope drift, degraded verification, and remaining assumptions or deviations.
- If verification or review is rejected, record a structured reason with `category` and a specific `details` string.

## Must Not

- Accept degraded verification silently.
- Mark verification passed because Graphify says the architecture looks correct.
- Paste full shell output by default.
- Close a task without review of scope drift.
