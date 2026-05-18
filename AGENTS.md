# Office GitHub Copilot Workflow Bundle

This repository maintains a repo-local GitHub Copilot CLI orchestration bundle. The product is the portable instruction, skill, agent, hook, validator, and artifact structure under `.github/`.

Runtime precedence and command behavior are defined in `.github/copilot-instructions.md`.

## V1 Constraints

- Safe Default Mode is the v1 acceptance target.
- The core path is `/setup -> /plan -> /execute -> /verify`.
- `/evaluate` is maintainer-only and outside the normal task path.
- Required config and artifacts are JSON or JSONL, not YAML.
- Required validators use Python standard library only.
- Do not add plugin, MCP, LSP, package install, or admin privilege requirements to the Safe Default path.
- Do not add user-facing command sprawl. New behavior should usually become a skill, artifact field, validator check, or hook guard.

## Change Discipline

- Preserve the fresh v1 layout unless an accepted ADR changes it.
- Do not copy this file verbatim into target repositories.
- Target repository `AGENTS.md` content is managed by `/setup` as a bounded block that preserves existing team instructions.
- Workflow governance changes require maintainer approval.
- Never treat stale graph metadata as fresh.
- Never claim verification without a real command/check result.

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
