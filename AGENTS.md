# Office GitHub Copilot Workflow Bundle

This repository maintains a repo-local GitHub Copilot CLI orchestration bundle. The product is the portable instruction, skill, agent, hook, validator, and artifact structure under `.github/`.

## Authority

- `AGENTS.md` and `.github/copilot-instructions.md` define always-on behavior.
- `.github/skills/<skill>/SKILL.md` defines specialized behavior loaded only when relevant.
- `.github/agents/workflow-orchestrator.agent.md` routes workflow intent and keeps context compact.
- `.github/hooks/` guards and logs in Enhanced Local Mode only.
- `.github/workflow/schemas/` and `.github/workflow/validators/` define and check artifact structure.
- Docs explain decisions; they do not govern behavior.

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
