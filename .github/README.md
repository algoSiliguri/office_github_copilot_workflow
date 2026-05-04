# GitHub Copilot Workflow Bundle

Portable `.github` workflow bundle for GitHub Copilot Chat, Copilot CLI, and Claude Code style agent workflows.

This repository is not a standalone application. It contains the contents you copy into a target repository's `.github/` directory.

## What this gives you

- A structured command flow from discovery to review
- Portable prompts, agents, contracts, schemas, and validators
- Scope control so implementation stays bounded to an approved plan
- Verification and review gates that require explicit evidence
- A lightweight `/quick-task` path for small changes

## Workflow commands

| Command | Purpose |
|---|---|
| `/setup-workflow` | Detect repo stack and write workflow config |
| `/grill` | Clarify goal, risks, constraints, and decisions |
| `/legacy-explore` | Optional bounded exploration for ambiguous codebases |
| `/write-plan` | Produce a scope-locked implementation plan |
| `/context-packet` | Optional retrieval artifact for broader tasks |
| `/execute-plan` | Implement only the declared plan scope |
| `/verify` | Run the declared verification command and capture evidence |
| `/review` | Final scope and quality review |
| `/quick-task` | Small-task fast path without full workflow overhead |

## Recommended flow

For non-trivial work:

`/setup-workflow -> /grill -> [/legacy-explore] -> /write-plan -> [/context-packet] -> /execute-plan -> /verify -> /review`

For small bounded changes:

`/setup-workflow -> /quick-task`

## Repository layout

This repo mirrors a target `.github/` folder:

- `agents/` contains agent role instructions
- `ai-workflow/` contains manifest, contracts, policies, schemas, validators, and examples
- `instructions/` contains editing rules for workflow files
- `prompts/` contains command prompt files
- `tasks/` stores generated task artifacts
- `workflow/` stores repo-specific generated config
- `copilot-instructions.md` is the primary human-facing instruction entrypoint

## Start here

1. Read [docs/INSTALL.md](docs/INSTALL.md).
2. Read [docs/USAGE.md](docs/USAGE.md).
3. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
4. Read [docs/CHEAT-SHEET.md](docs/CHEAT-SHEET.md).
5. Copy these files into the target repository's `.github/` directory.
6. In the target repo, run `/setup-workflow` first.

## Validation

From the target repository root after installing into `.github/`:

```bash
python3 .github/ai-workflow/validators/bootstrap
python3 .github/ai-workflow/validators/validate-manifest
python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
```

## Important constraints

- `manifest.yaml`, schemas, and validators are governance files
- Repo-specific values belong in `.github/workflow/config.yaml`
- Workflow edits should preserve portability across repositories
- `/verify` must run a real command and capture real output before claiming success

## Docs

- [Installation](docs/INSTALL.md)
- [Effective usage](docs/USAGE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Cheat sheet](docs/CHEAT-SHEET.md)
