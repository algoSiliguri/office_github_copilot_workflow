# Copilot Workflow Instructions

This repository uses a repo-local Copilot CLI orchestration bundle.

## Commands

- `/setup`: validate the bundle, create or update the target repo managed `AGENTS.md` block, record Graphify output presence, and tell the user to run `graphify copilot install`.
- `/plan`: create a PlanRecord before edits.
- `/execute`: perform only approved plan edits and record execution.
- `/verify`: prove the result with real checks and review.
- `/evaluate`: maintainer-only workflow evaluation.

Do not expose `/quick-task`. Quick work is a classification inside `/plan`.

## Precedence

1. Root `AGENTS.md` and this file define always-on behavior.
2. `.github/agents/workflow-orchestrator.agent.md` routes intent and compacts context.
3. `.github/skills/<skill>/SKILL.md` defines specialized task behavior.
4. `.github/workflow/schemas/` and `.github/workflow/validators/` define artifact structure.
5. `.github/hooks/` guards and logs when hooks are enabled.
6. Docs explain; they do not govern.

## Always-On Rules

- Keep the Safe Default path free of plugin, MCP, LSP, admin, package-install, YAML, or third-party Python requirements.
- Load only the relevant skill for the current phase.
- Use GraphRecord and selected `graph_refs[]` for planning context; do not load the whole graph by default.
- Missing or stale graph freshness requires explicit degraded-mode approval before normal planning.
- `graphify copilot install` is a setup instruction, not proof that a future Copilot session will load or use Graphify behavior.
- Do not treat graph data as verification evidence.
- Do not copy raw prompts, model responses, tool transcripts, or chat history into repo artifacts.
- Hooks and validators guard and log; they do not secretly plan, execute, verify, evaluate, or regenerate graph data.
- Human approval is required before execution, risky tool use, and final verification acceptance.
