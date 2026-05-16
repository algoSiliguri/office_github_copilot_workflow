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

## Setup: Detect and Record Graph State

`/setup` is responsible for detecting actual graphify output and writing `graph-record.json`. It must not assume output exists.

- Inspect `graphify-out/` and each required file (`graph.json`, `GRAPH_REPORT.md`, `manifest.json`) to determine actual presence.
- Write `graph_output_exists` (each key as a boolean) and `last_checked_at` (ISO 8601) into `graph-record.json`.
- Set `graph_status` to `fresh`, `stale`, `missing`, or `degraded-approved` based on detected state.
- If `graphify-out/` is absent or required files are missing, set `graph_status: missing` and complete setup. Do not halt. The plan phase gate handles degraded-mode approval.
- Tell the user to run `graphify` then `graphify copilot install` when status is `missing` or `stale`.
- Run `check-graphify-copilot` as a non-mutating health check. Report its fix command on failure; do not auto-install.

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
