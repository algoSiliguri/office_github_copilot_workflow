# Installation

## What this repository contains

This repository is a portable `.github` workflow bundle. The files here are intended to become the target repository's `.github/` contents.

Example target shape:

```text
your-repo/
  .github/
    agents/
    ai-workflow/
    instructions/
    prompts/
    tasks/
    workflow/
    copilot-instructions.md
```

## Install into a target repository

From the target repository root:

```bash
mkdir -p .github
cp -R /path/to/office_github_copilot_workflow/. .github/
```

If you only want selected parts, keep the internal relative paths unchanged. Do not rename `ai-workflow/`, `workflow/`, `agents/`, or `prompts/`.

## First-run checklist

1. Confirm Python 3 is available for validators.
2. Copy this bundle into the target repo's `.github/`.
3. Open Copilot Chat or your compatible agent surface.
4. Run `/setup-workflow`.
5. Confirm `.github/workflow/config.yaml` was generated correctly.
6. Run:

```bash
python3 .github/ai-workflow/validators/bootstrap
python3 .github/ai-workflow/validators/validate-manifest
python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
```

## What `/setup-workflow` does

It detects the target repository stack and writes `.github/workflow/config.yaml` with:

- project name and description
- primary language and framework
- build, test, lint, and verify commands
- workflow settings such as task artifact path

Do not hand-edit that file unless you are intentionally overriding generated values and accept the divergence.

## Updating the workflow later

- Update the copied `.github/` files in the target repo
- Re-run `/setup-workflow` if project metadata or command defaults changed
- Re-run the validator commands after upgrades

## Upgrading

When you pull an updated bundle into a target repo:

1. **Check the CHANGELOG** — read `.github/CHANGELOG.md` for schema changes, new required fields, and breaking changes since your current `VERSION`.
2. **Run CLI validators** — run the bootstrap and manifest validators to confirm the new bundle is internally consistent:
   ```bash
   python3 .github/ai-workflow/validators/bootstrap
   python3 .github/ai-workflow/validators/validate-manifest
   python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
   ```
3. **Handle `migration_required` artifacts** — run `/upgrade-workflow` in Copilot Chat. It will scan `.github/tasks/` and report each artifact as `compatible`, `migration_required`, or `regenerate`.
4. **Regenerate affected phases** — for any artifact flagged `migration_required`, re-run the phase command that produced it (e.g. re-run `/legacy-explore` for a stale `LegacyExplorationRecord`). The new bundle version will produce a compliant artifact.

Do not skip step 3. A stale artifact used by a downstream phase will produce incorrect behavior, not a clear error.

## Do not do this

- Do not edit repo-specific values into prompts or agents
- Do not move validators away from `.github/ai-workflow/validators/`
- Do not delete `tasks/.gitkeep` if you want the task artifact folder preserved in git

