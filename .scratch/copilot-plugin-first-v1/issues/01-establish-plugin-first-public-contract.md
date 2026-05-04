## Parent

[2026-05-03-copilot-plugin-first-v1-prd.md](/Users/koustavdas/Documents/Obsidian Vault/Claude Projects/Office/docs/superpowers/specs/2026-05-03-copilot-plugin-first-v1-prd.md)

Status: needs-triage
Type: AFK

# Establish the plugin-first public contract

## What to build

Reshape the public workflow surface so it aligns with officially documented GitHub Copilot customization for JetBrains: repository instructions, path-specific instructions, and prompt files. Remove any public claims that depend on unsupported instruction hierarchies, and make the visible plugin entrypoints small, durable, and easy to understand.

## Acceptance criteria

- [ ] The public plugin contract is defined only through `.github/copilot-instructions.md`, `.github/instructions/**/*.instructions.md`, and prompt files.
- [ ] Unsupported or misleading public references to internal agent/skill behavior are removed, renamed, or clearly marked internal-only.
- [ ] The user-facing command surface for v1 is documented as `/setup-workflow`, `/grill`, `/write-plan`, `/execute-plan`, `/quick-task`, and `/review`.
- [ ] The repo contains a clear plugin-first onboarding path for imported use in another repository.

## Blocked by

None - can start immediately.
