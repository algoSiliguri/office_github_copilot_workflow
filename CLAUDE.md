Workflow tooling for GitHub Copilot (IntelliJ) and Claude Code. Artifacts are Markdown documents: skills, prompts, agents, specs, and plans. No build system, no tests, no deployable code.

## Agent skills

### Issue tracker

Issues and PRDs for this repo live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

This repo uses the canonical triage labels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This repo is configured as a single-context layout. Skills should read the repo-root domain docs when they exist. See `docs/agents/domain.md`.

## Project map

- `.github/copilot-instructions.md` — global hard rules for Copilot
- `.github/prompts/` — slash command prompts
- `.github/ai-workflow/manifest.yaml` — central workflow graph and runtime registry
- `.github/ai-workflow/contracts/commands/` — versioned command contracts
- `.github/ai-workflow/schemas/` — artifact and manifest schemas
- `.github/ai-workflow/validators/` — deterministic validators
- `.github/ai-workflow/skills/` — one SKILL.md per command phase
- `.github/ai-workflow/protocols/` — supplemental phase protocols
- `.github/ai-workflow/artifacts/examples/` — example artifacts per phase
- `workflow/config.yaml` — repo-local wiring only
- `docs/superpowers/specs/` — design specs (`YYYY-MM-DD-<topic>-design.md`)
- `docs/superpowers/plans/` — implementation plans (`YYYY-MM-DD-<topic>.md`)

<important if="you are naming or creating a new artifact file">
Artifact naming: `YYYY-MM-DD-<topic>[-design].md`
</important>

<important if="you are modifying manifest.yaml, config.yaml, or command contracts">
- `manifest.yaml` owns workflow semantics and command ordering
- `workflow/config.yaml` owns repo-local wiring only — not workflow semantics
- Skills and contracts must stay aligned; prompts are thin wrappers, not a second source of truth
</important>

<important if="you are running or advising on workflow phase commands">

Phase order: `/setup-workflow` → `/grill` → `/write-plan` → optional `/context-packet` → `/execute-plan` → `/verify` → `/review`

Parallel narrow path: `/quick-task`

- `/context-packet` required when plan or phase trigger rules say execution needs bounded retrieved context
- `/grill` is the single pre-planning decision phase; do not route v1 work through `/brainstorm` or `/write-spec`
- `/execute-plan` always leaves an ExecutionCheckpointArtifact
- Start a new chat at every phase boundary to reset context cost
- Hard rules: no implementation before a plan exists; no "done" without test output; no PR without a verification file
</important>

<important if="you are editing skills in .github/ai-workflow/skills/">
Skills must stay command-focused, operational, and reusable. Repo-specific values belong in `workflow/config.yaml`, not in skills.
</important>
