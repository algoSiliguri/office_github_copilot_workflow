# Claude Code — Workflow Entrypoint

This repo uses a structured AI workflow system in `.github/`. Claude Code does not auto-load `.github/copilot-instructions.md`, so this stub provides the entrypoint.

## Always read first

Before acting on any workflow command, read:
- `.github/copilot-instructions.md` — always-on workflow rules
- `.github/ai-workflow/manifest.yaml` — governed commands registry

## Authority

Governance files are authoritative:
- `.github/ai-workflow/contracts/commands/` — what each command reads/writes
- `.github/ai-workflow/schemas/` — artifact structure
- `.github/ai-workflow/policies/` — behavioral constraints
- `.github/ai-workflow/validators/` — validation scripts

## Important

- Do not assume hidden memory or automatic orchestration.
- Do not self-approve evaluations.
- Do not skip validator requirements declared in contracts.
- Every phase must produce its declared output artifact before the next command runs.
- Runtime: this system is Copilot/JetBrains-native. Claude Code is a supported secondary runtime — see `INSTALL.md` for setup.
