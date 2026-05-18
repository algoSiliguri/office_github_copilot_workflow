---
name: grill
description: Use when a user invokes /grill to run the mandatory Discovery Gate before planning.
---

# grill

Use this skill for `/grill`.

## Purpose

Produce a GrillRecord that maps the blast radius of the task before any planning begins. The human
must approve the blast-radius analysis (Discovery Gate) before `/plan` is allowed to proceed.

## Use When

- A user invokes `/grill` on a task or request.
- `/setup` completes and the user is ready to start work.
- `/plan` is attempted without a valid `grill_ref` — refuse and route back to `/grill`.

## Instructions

### Task initialization (always first)

1. Read `.github/workflow/state.json`. If `active_task` is non-null, the task folder already
   exists — use that task ID and skip to the graph-context step below.
2. If `active_task` is null, allocate a new task ID:
   - List all directories under `.github/tasks/` matching `TASK-\d+`.
   - Take the highest numeric suffix found; the new ID is that number plus one, zero-padded to
     three digits. If no TASK folders exist, start at `TASK-001`.
   - Create `.github/tasks/TASK-{NNN}/`.
   - Update `.github/workflow/state.json` to set `active_task: "TASK-{NNN}"`.
3. All subsequent artifacts for this session go under `.github/tasks/TASK-{NNN}/`.

### Grill session

- Populate `task_id` with the active task ID determined above.
- Populate `grilled_at` with the current time in ISO 8601 format.
- Read `.github/workflow/graph-record.json`. If freshness is `stale` or `missing`, warn the user
  before proceeding; degraded grill is allowed with explicit acknowledgement.
- Read `graphify-out/GRAPH_REPORT.md` to understand module boundaries and community hubs.
- Run `graphify query "<task description>"` to surface related files, dependency edges, and
  cross-module connections relevant to the task.
- Identify every file that could be affected by the task, not just files you intend to change.
  This includes callers, tests, configuration, documentation, and generated artifacts.
- Write `impacted_files` as the full potential blast radius. The plan's `intended_files` must be a
  subset of this list — err on the side of inclusion here.
- Write `mandatory_verification_steps` as the pool of valid verification commands for this task.
  Each entry is a string array, e.g. `["python3", "-m", "pytest", "tests/"]`. The plan's
  `verification_commands` must be a subset of this pool.
- Write `risk_notes` for any high-risk files, fragile dependency edges, cross-module side effects,
  or areas where graph data indicates risk not visible from file names alone. Can be empty if no
  elevated risk is found.
- Set `requirements_ref` to the path of a requirements snapshot if one was used; otherwise null.
- Present the blast-radius analysis to the user. Explain the scope, risks, and proposed
  verification approach in plain language before requesting approval.
- Require human approval before writing the final `grill.json`. The approval kind must be `grill`.
- Write `human_approval` with `decision: "approved"`, the approver identity, and a non-empty
  reason confirming the blast-radius analysis is correct.
- Run `python3 .github/workflow/validators/check-grill .github/tasks/TASK-{NNN}/grill.json` to
  validate the record before declaring the Discovery Gate passed.

## Contract with /plan

- `plan.intended_files` must be a subset of `grill.impacted_files`. If the user wants to include
  a file not in `grill.impacted_files`, the grill must be re-run or amended before planning.
- `plan.verification_commands` must be a subset of `grill.mandatory_verification_steps`. If the
  plan needs a verification command not in the grill pool, the grill must be amended.

## Must Not

- Produce a grill record without a human-approved Discovery Gate.
- Treat `impacted_files` as a planning decision — that belongs to `/plan`.
- Use graph data as verification evidence.
- Silently skip Graphify context. If the graph is unavailable, record it in `risk_notes` and
  surface the limitation to the user before proceeding.
- Auto-approve the grill record on behalf of the user.
