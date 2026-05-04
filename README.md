# GitHub Copilot Workflow Bundle

Portable `.github` workflow bundle for GitHub Copilot Chat and Copilot CLI.

This repository is intentionally small: the canonical product is the `.github/` folder. Everything important for installation, workflow behavior, architecture, and daily usage lives there.

## Start Here

1. Copy this repository's `.github/` folder into a target repository.
2. Read `.github/copilot-instructions.md`.
3. Read `.github/docs/INSTALL.md`.
4. Run `/setup-workflow` in Copilot Chat.

## Core Workflow

Full path:

`/setup-workflow -> /grill -> [/legacy-explore] -> /write-plan -> [/context-packet] -> /execute-plan -> /verify -> /review`

Fast path:

`/setup-workflow -> /quick-task`

## What Is Canonical

- `.github/copilot-instructions.md` defines the top-level workflow rules Copilot should follow.
- `.github/prompts/` exposes the slash-command surface.
- `.github/agents/` contains the command behavior.
- `.github/ai-workflow/manifest.yaml` is the machine-readable workflow graph.
- `.github/ai-workflow/contracts/`, `schemas/`, `policies/`, and `validators/` enforce behavior.
- `.github/docs/` contains the human docs you should actually read.

## Essential Docs

- `.github/docs/INSTALL.md` — install and upgrade the bundle
- `.github/docs/USAGE.md` — practical developer usage
- `.github/docs/ARCHITECTURE.md` — how the system is structured
- `.github/docs/CHEAT-SHEET.md` — quick command and workflow reference

## Validation

Run from the target repository root:

```bash
python3 .github/ai-workflow/validators/bootstrap
python3 .github/ai-workflow/validators/validate-manifest
python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
```

## Constraints

- Treat `.github/` as the only canonical workflow implementation.
- Treat `manifest.yaml`, schemas, and validators as governance files.
- Put repo-specific values only in `.github/workflow/config.yaml`.
- Never claim work is verified without real command output.
