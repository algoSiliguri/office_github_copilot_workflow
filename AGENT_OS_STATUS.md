# Agent_OS Integration Status

## v1 Status: Copilot-primary, Agent_OS seam planned for v1.x

This repo is the **Copilot-native** workflow bundle. The canonical runtime for v1 is
GitHub Copilot Chat / JetBrains Copilot CLI. A secondary Claude Code path exists via
`CLAUDE.md` → `copilot-instructions.md`.

It is **not** an Agent_OS workflow pack today. Do not use it as one.

## What this repo owns (v1)

- Portable `.github/` folder for Copilot environments
- Governance layer: manifest, contracts, schemas, policies, validators
- Phase DAG and artifact conventions for Copilot-driven tasks

## What this repo does NOT own (v1)

- Agent_OS Pi extension runtime
- Pi command registration
- Task state machine
- Event recording / dashboard
- knowledge-brain integration

## v1.x pack seam plan

The governance layer in `.github/ai-workflow/` is designed to be runtime-neutral.
A future Agent_OS workflow pack can be built from it by:

1. Translating `.github/ai-workflow/manifest.yaml` → `workflow-pack.yaml` (Agent_OS format)
2. Wrapping Python validators in Agent_OS TypeScript validator shims
3. Mapping artifact root from `.github/tasks/TASK-NNN/` → `.agent-os/tasks/T-NNN/`
4. Adding `runtime_target: pi` and `min_agent_os_version` fields

Until that work is done, the Agent_OS runtime loads the bundled
`copilot-workflow` pack from `Agent_OS/src/ccp/commands/init/packs/` instead.

## Authority map (v1)

| Concern | Owner |
|---------|-------|
| Pi runtime, commands, state machine | Agent_OS |
| Memory backend | knowledge-brain |
| Project onboarding | agent-os-starter |
| Copilot workflow doctrine | this repo |
| Agent_OS workflow pack (v1) | bundled in Agent_OS repo |
