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
- Record actual modified files, command refs, checkpoints, and deviations in ExecutionRecord.
- Request approval for writes outside scope, destructive shell, network commands, dependency installation, graph regeneration, workflow governance edits, or secret access.
- Record each risky tool approval or denial in ExecutionRecord.

## Must Not

- Install packages, fetch network resources, regenerate graph data, push git refs, broadly delete files, or edit workflow governance files autonomously.
- Treat unapproved scope drift as accepted.
