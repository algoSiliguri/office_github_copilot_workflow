---
name: bounded-execution
description: Use when carrying out an approved PlanRecord and recording what actually changed.
---

# bounded-execution

Use this skill for `/execute`.

## Purpose

Carry out only the approved PlanRecord and record what actually changed.

## Use When

- A human-approved PlanRecord exists.
- The task is ready for bounded edits.

## Instructions

- Read the approved PlanRecord first.
- Edit only files listed in the approved intended file scope.
- Follow the approved `graph_refs[]` from the plan as context pointers; do not broaden context without recording why.
- Prefer targeted graph_refs over broad repository search when relevant refs exist.
- Do not expand scope based on Graphify findings discovered during execution. The plan's `intended_files` is fixed at approval time.
- If graph context during execution reveals that the plan's scope is structurally wrong — files the plan should have included but did not — halt with `status: blocked`, surface the gap clearly, and require the user to amend the plan via `/plan` and re-approve before continuing. Do not use scope-drift approval to paper over a plan with wrong scope.
- When the plan includes test changes, write or update tests before or alongside implementation edits.
- Record test outcomes and verification-relevant results in ExecutionRecord without pasting full output.
- Record `created_at`, actual modified files, command refs, checkpoints, and deviations in ExecutionRecord.
- Request approval for writes outside scope, destructive shell, network commands, dependency installation, graph regeneration, workflow governance edits, or secret access.
- Record each risky tool approval or denial in ExecutionRecord.

## Must Not

- Install packages, fetch network resources, regenerate graph data, push git refs, broadly delete files, or edit workflow governance files autonomously.
- Treat unapproved scope drift as accepted.
- Use scope-drift approval to resolve structural scope errors discovered via Graphify during execution.
