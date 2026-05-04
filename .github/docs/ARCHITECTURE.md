# Architecture

## What this system is

This bundle is a plugin-first AI workflow for GitHub Copilot. It gives Copilot a bounded command system instead of leaving it to operate as a free-form assistant.

## Main layers

- `copilot-instructions.md`
  Top-level workflow rules, command order, CLI handoff rules, and hard constraints.

- `prompts/`
  The slash-command entrypoints a user invokes in Copilot Chat.

- `agents/`
  The operational behavior for each command. This is where command-specific logic and output requirements live.

- `ai-workflow/manifest.yaml`
  The authoritative workflow graph. It defines which commands exist, their allowed predecessors, required inputs, outputs, and handoffs.

- `ai-workflow/contracts/commands/`
  Versioned command contracts. These define authority limits, required validators, and non-negotiable semantics.

- `ai-workflow/policies/`
  Cross-cutting rules such as quick-task eligibility, context thresholds, verification status, and review dispositions.

- `ai-workflow/schemas/`
  Artifact formats for grill, plan, execution, verification, review, and related records.

- `ai-workflow/validators/`
  Deterministic checks that enforce manifest integrity, config correctness, plan scope, artifact compatibility, and review gating.

- `workflow/config.yaml`
  Repo-local wiring only. This is the generated file that stores detected commands and project metadata for the target repo.

## Workflow model

The governed path is:

`setup-workflow -> grill -> legacy-explore if needed -> write-plan -> context-packet if needed -> execute-plan -> verify -> review`

There is also a narrow escape hatch:

`quick-task`

This path is only for small, low-risk, tightly scoped work. If scope or risk grows, it escalates back to the full workflow.

## Key architectural constraints

- Planning must happen before implementation.
- Implementation must stay within declared file scope.
- Verification must use real command output.
- Review must compare actual changed files against plan scope.
- CLI execution requires explicit human approval when the workflow says so.

## What is canonical

For behavior, trust `.github/` over any external notes.

- Human guidance: `copilot-instructions.md`, `docs/`
- Command behavior: `prompts/`, `agents/`
- Enforcement and machine authority: `manifest.yaml`, contracts, policies, schemas, validators
