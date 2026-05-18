---
name: graph-context
description: Use when setup or planning needs codebase graph context from graphify output.
---

# graph-context

Use this skill when setup or planning needs codebase graph context.

## Purpose

Connect graphify output to workflow artifacts without loading the whole graph into the prompt.

## Use When

- `/setup` must detect and record graphify output state.
- `/setup` tells the user to run `graphify copilot install` and records that expectation without treating it as proof of future skill behavior.
- `/setup` can run `.github/workflow/validators/check-graphify-copilot` to check the local Graphify command, `graphify-out/`, and discoverable Copilot Graphify skill without mutating user files.
- `/plan` needs codebase context for intended files, affected modules, or risk.
- `/verify` records which approved graph refs were used.

## Setup: Write the Managed AGENTS.md Block

`/setup` writes a bounded block into the target repo's `AGENTS.md`. This block is the
orientation surface for every future Copilot session in that repo.

### Rules

- If `AGENTS.md` does not exist, create it with only the managed block.
- If `AGENTS.md` exists, find the markers and replace the block between them. If the markers are
  absent, append the block at the end of the file. Never delete or overwrite content outside the
  markers (`overwrite_existing_team_instructions: false`).
- After writing, confirm the file contains both markers and all six required links.

### Exact managed block to write

```
<!-- BEGIN COPILOT WORKFLOW V1 -->
## Copilot Workflow (managed — do not edit this block manually)

This repo uses a structured Copilot CLI workflow bundle.
See `.github/QUICKSTART.md` for setup instructions.

Workflow rules: `.github/copilot-instructions.md`
Quick start: `.github/QUICKSTART.md`
Skills: `.github/skills/`
Agent: `.github/agents/workflow-orchestrator.agent.md`
Workflow config: `.github/workflow/config.json`
Graph state: `.github/workflow/graph-record.json`
<!-- END COPILOT WORKFLOW V1 -->
```

Write this block verbatim (substituting no values — the paths are repo-relative constants).
After writing, tell the user which file was created or updated and confirm the markers are present.

## Setup: Detect and Record Graph State

`/setup` is responsible for detecting actual graphify output and writing `graph-record.json`. It must not assume output exists.

- Inspect `graphify-out/` and each required file (`graph.json`, `GRAPH_REPORT.md`, `manifest.json`) to determine actual presence.
- Write `graph_output_exists` (each key as a boolean) and `last_checked_at` (ISO 8601) into `graph-record.json`.
- Set `graph_status` to `fresh`, `stale`, `missing`, or `degraded-approved` based on detected state.
- If `graphify-out/` is absent or required files are missing, set `graph_status: missing` and complete setup. Do not halt. The plan phase gate handles degraded-mode approval.
- Run `check-graphify-copilot` as a non-mutating health check. Report its fix command on failure; do not auto-install.

### When graph is missing or stale — output this pre-flight checklist to the user

```
⚠ Graphify output not found (or stale). Bundle is in degraded mode.

To enable full graph context, run from your repo root:

  pip install graphify          # install once per machine
  graphify .                    # build the knowledge graph
  graphify copilot install      # register the Copilot skill

Then re-run /setup to record fresh graph state.

If Graphify is unavailable, you can still proceed — each phase will
ask for explicit human approval to continue in degraded mode.

See .github/QUICKSTART.md for the full setup guide.
```

Output this block verbatim (or equivalent). Do not silently record degraded mode and move on.

## Instructions

- Treat `graphify-out/` as generated graph output.
- Use `check-graphify-copilot` as a setup doctor check. If it fails, report its fix command; do not auto-install or write to `~/.copilot`.
- Require `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md`, and `graphify-out/manifest.json` for fresh or stale graph records.
- Treat `.github/workflow/graph-record.json` as orchestration metadata.
- Select only relevant `graph_refs[]` for a task.
- Prefer graph refs that identify a bounded module, file, community, symbol, or relationship needed by the current plan.
- Prefer the nearest and most specific refs first: file refs before module refs, module refs before community refs.
- Cap default ref selection at five refs. Record justification in PlanRecord when more than five refs are needed.
- Use compact refs such as `graph:file:src/app.py`, `graph:module:auth`, `graph:community:payment-flow`, or `graph:edge:controller->service`.
- Store task-scoped refs in PlanRecord.
- Record freshness as `fresh`, `stale`, `missing`, or `degraded-approved`.
- Require degraded-mode approval before normal planning when freshness is not `fresh`.
- When files change, mark graph freshness as potentially stale; do not regenerate without approval.

## Must Not

- Load the whole graph by default.
- Regenerate graph output without explicit approval.
- Treat graph data as verification evidence.
