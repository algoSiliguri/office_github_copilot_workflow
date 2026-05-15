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
- Record actual modified files, command refs, checkpoints, and deviations in ExecutionRecord.
- Request approval for any write outside scope or any risky tool use.

## Must Not

- Install packages, fetch network resources, regenerate graph data, push git refs, broadly delete files, or edit workflow governance files autonomously.
- Treat unapproved scope drift as accepted.
