# Copilot Instructions

## Priority Order

1. Ticket requirements and spec file
2. `.github/skills/conventions/SKILL.md` (repo-specific rules)
3. Skill file for the current phase
4. These instructions

Note: phase-specific procedures are defined in the skill file for the active phase and take precedence over general behavior patterns described in these instructions.

## Hard Rules

1. No implementation code before a plan file exists
2. No "done" without running tests — never claim work is complete without test output
3. No PR without a verification file containing actual pasted test output
4. Always reference the ticket ID in commit messages and PR descriptions

## Drift Control

Reinforcement rules for behaviors that demonstrably drift in practice.

1. Reproduce the bug before proposing a fix
2. Ask before guessing when information is missing
3. State uncertainty explicitly — never present guesses as facts
4. Do not fabricate APIs, file paths, or tool behaviors
5. Verify the solution works after implementing it
6. Read relevant existing code before suggesting or making modifications
7. Stay within phase scope — do not implement, refactor, or plan across multiple phases in a single response

## Conscious Skip Protocol

If you genuinely need to skip a phase:
1. State it explicitly: "Skipping [phase] because [reason]"
2. Note what artifact is missing
3. Continue — this is a conscious override, not the default path

Skipping a phase does not expand the current phase's scope — complete only the work defined for the active phase.

Never skip silently.

## Context Hygiene (MANDATORY)

After completing every phase — before any handoff — output this block exactly, with every field filled in:

---
**Phase complete:** [phase name]

**Summary:**
- [key decision or outcome — one concrete sentence per bullet, max 5 bullets]

**Artifacts:**
- Created: `[full/path/to/file.md]` — [one-line description]
- Modified: `[full/path/to/file.md]` — [what changed]

**Next:** `/[command] [required file path or argument]`

---

Rules:
- Output this block even when staying in the same chat.
- Fill every field. Do not output the template with unfilled brackets.
- "Artifacts" must list every file created or modified this phase. A missing file is a handoff failure.
- "Next" must include the exact command and any required path arguments (e.g. `/write-spec docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`).
- If no files were created or modified, write "None" under Artifacts.
- After outputting this block, save it to `[Handoffs path]/[ticket-id].md`:
  - If the file doesn't exist: create it with the header `# Handoff Log: [ticket-id]` on line 1, then append the block below the header.
  - If the file exists: append two blank lines, then the block.
  - `[Handoffs path]` comes from the `Handoffs:` line in `conventions/SKILL.md`. If that line is missing or empty, use `docs/handoffs/`.
  - `[ticket-id]` comes from the `ticket:` frontmatter field of any artifact created this phase. If no artifact was created, read the `Active Context` block in `conventions/SKILL.md`.
  - After writing, immediately read the file back and confirm the `Phase complete:` line is present. If the read fails or the line is absent, emit:
    ```
    ⚠️ Handoff file write could not be confirmed at [path].
    The block above is the authoritative record for this phase.
    Verify the file exists before starting the next session.
    ```
    Do not retry the write. Continue to the log.md append step regardless.
- Append one line to `[Handoffs parent]/log.md` (the parent directory of the Handoffs path — e.g. if Handoffs is `docs/workflow/handoffs/`, the log is `docs/workflow/log.md`; if Handoffs is `docs/handoffs/`, the log is `docs/log.md`; create with header `# Workflow Log` if missing):
  `[YYYY-MM-DD] | [ticket-id] | [phase-name] | complete`
- For each file listed under a "Created:" line in the Artifacts section of this block, append one line to `[Handoffs parent]/artifact-index.md` (create with header `# Artifact Index` if missing):
  `[YYYY-MM-DD] | [ticket-id] | [phase-name] | [full-artifact-path] — [description from the Artifacts line]`
