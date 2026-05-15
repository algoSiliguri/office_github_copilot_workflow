# graph-context

Use this skill when setup or planning needs codebase graph context.

## Purpose

Connect graphify output to workflow artifacts without loading the whole graph into the prompt.

## Use When

- `/setup` detects or records graphify output.
- `/plan` needs codebase context for intended files, affected modules, or risk.
- `/verify` records which approved graph refs were used.

## Instructions

- Treat `graphify-out/` as generated graph output.
- Treat `.github/workflow/graph-record.json` as orchestration metadata.
- Select only relevant `graph_refs[]` for a task.
- Store task-scoped refs in PlanRecord.
- Record freshness as `missing`, `stale`, `unknown`, or `fresh`.
- Require degraded-mode approval before normal planning when freshness is not `fresh`.

## Must Not

- Load the whole graph by default.
- Regenerate graph output without explicit approval.
- Treat graph data as verification evidence.
