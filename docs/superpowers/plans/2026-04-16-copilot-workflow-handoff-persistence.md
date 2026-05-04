# Copilot Workflow: Phase Handoff Persistence — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the phase handoff gap by persisting context hygiene summaries to disk as per-ticket handoff files, adding YAML frontmatter to verification artifacts, and writing deviations and discoveries back into the plan file during execution.

**Architecture:** A new `Handoffs:` path in conventions stores one append-only file per ticket (`[handoffs-path]/[ticket-id].md`). Each context hygiene block is appended to it, giving both per-phase continuity and a running artifact registry for the ticket in one file. Verification artifacts gain YAML frontmatter (ticket, phase, created, status, source) matching the schema from Plan 1. The execution skill gains two write-back protocols: accepted deviations appended to `## Amendments` in the plan file, and unexpected discoveries appended to `## Discoveries` in the plan file.

**Tech Stack:** Markdown only — no code, no build system, no test runner. Verification for each phase is a concrete scenario trace.

**Spec:** `docs/superpowers/specs/2026-04-16-copilot-workflow-gap-analysis-design.md`

**Depends on:** Plan 1 (`2026-04-16-copilot-workflow-artifact-contracts.md`) must be implemented first.

---

## Out of Scope (covered in Plan 3)

| Item | Deferred to |
|------|-------------|
| Post-ticket learning prompt | Plan 3 |
| Append-only workflow log | Plan 3 |
| Artifact index | Plan 3 |
| Conventions domain segmentation | Plan 3 |
| Semantic search protocol | Plan 3 |

---

> **Execution mode:** phased

## All Files Changed

- `github/skills/conventions/SKILL.md` — Phase 1: add `Handoffs:` line to Artifact Paths template
- `github/skills/setup/SKILL.md` — Phase 1: add handoffs detection and output field
- `github/skills/verification/SKILL.md` — Phase 2: add YAML frontmatter to verification template
- `github/copilot-instructions.md` — Phase 3: extend context hygiene rules with file persistence step
- `github/skills/execution/SKILL.md` — Phase 4: add deviation write-back and discovery logging

---

## Phase 1: Add Handoffs Path to Conventions and Setup

**Files in this phase:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`

- [ ] **Step 1: Add Handoffs path to conventions template**

In `github/skills/conventions/SKILL.md`, find the `## Artifact Paths` section:

```
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
Handoffs:       <e.g. docs/workflow/handoffs/>
```

- [ ] **Step 2: Trace scenario to verify conventions change**

Mental trace — a new team member runs `/setup`. Confirm the updated conventions template now contains the `Handoffs:` field so setup will populate it. Check: the `<e.g. docs/workflow/handoffs/>` placeholder is present and follows the same format as the other four paths. No other lines changed.

- [ ] **Step 3: Add handoffs detection to setup/SKILL.md Step 5**

In `github/skills/setup/SKILL.md`, find the directory detection block in Step 5:

```
Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path
- `docs/brainstorms/` or `docs/workflow/brainstorms/` → use as brainstorms path

If none exist, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
- Brainstorms: `docs/brainstorms/`
```

Replace with:

```markdown
Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path
- `docs/brainstorms/` or `docs/workflow/brainstorms/` → use as brainstorms path
- `docs/handoffs/` or `docs/workflow/handoffs/` → use as handoffs path

If none exist, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
- Brainstorms: `docs/brainstorms/`
- Handoffs: `docs/handoffs/`
```

- [ ] **Step 4: Add Handoffs field to setup/SKILL.md Step 6 output template**

In `github/skills/setup/SKILL.md`, find the `## Artifact Paths` block inside the Step 6 output template:

```
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
Handoffs:       [detected value]
```

- [ ] **Step 5: Trace scenario to verify setup changes**

Mental trace — user runs `/setup` on a repo that has `docs/workflow/handoffs/`.
1. Detection logic finds it and assigns `docs/workflow/handoffs/` as the handoffs path.
2. Generated conventions file contains `Handoffs:       docs/workflow/handoffs/`.

Mental trace — repo with no handoffs directory:
1. Detection falls through; default `docs/handoffs/` is used.
2. Generated conventions file contains `Handoffs:       docs/handoffs/`.

- [ ] **Step 6: Commit**

```bash
git add github/skills/conventions/SKILL.md github/skills/setup/SKILL.md
git commit -m "feat: add Handoffs artifact path to conventions template and setup detection"
```

**Engineer review prompt:**
- Does `Handoffs: [detected value]` use the same placeholder format as the other four path fields?
- Would running `/setup` on a repo with `docs/workflow/handoffs/` produce `Handoffs:       docs/workflow/handoffs/`? Trace the detection logic in Step 5 to confirm.

---

## Phase 2: Verification Artifact Frontmatter

**Files in this phase:**
- Modify: `github/skills/verification/SKILL.md`

- [ ] **Step 1: Update Metadata Inputs to document source field**

In `github/skills/verification/SKILL.md`, find the Metadata Inputs line:

```
- **Inputs:** Spec file path
```

Replace with:

```markdown
- **Inputs:** Spec file path — recorded as `source` in the verification frontmatter
```

- [ ] **Step 2: Add frontmatter to the verification template**

In `github/skills/verification/SKILL.md`, find the start of the auto-generated verification template block (inside the fenced code block that begins with `# Verification:`):

```
# Verification: [TICKET-ID] — [Feature Name]

## Requirement Coverage
```

Replace with:

```markdown
---
ticket: [TICKET-ID]
phase: verify
created: [YYYY-MM-DD]
status: pending
source: [spec-file-path]
---

# Verification: [TICKET-ID] — [Feature Name]

## Requirement Coverage
```

- [ ] **Step 3: Update Output Format section to mention frontmatter**

Find:

```
## Output Format

Verification file containing:
- Requirement coverage table (each requirement mapped to a test + pasted output)
- Targeted test output (pasted)
- Full suite output (pasted)
- Manual testing results
- Sign-off checklist
```

Replace with:

```markdown
## Output Format

Verification file containing:
- YAML frontmatter (`ticket`, `phase`, `created`, `status`, `source`)
- Requirement coverage table (each requirement mapped to a test + pasted output)
- Targeted test output (pasted)
- Full suite output (pasted)
- Manual testing results
- Sign-off checklist
```

- [ ] **Step 4: Trace scenario to verify**

Mental trace — user runs `/verify docs/specs/2026-04-16-PROJ-123-feature.md`.

Confirm:
1. Agent reads the spec from the provided path.
2. Generated verification file starts with filled YAML frontmatter:
   ```
   ticket: PROJ-123
   phase: verify
   created: 2026-04-16
   status: pending
   source: docs/specs/2026-04-16-PROJ-123-feature.md
   ```
3. `source` contains the spec path exactly as received (not normalized to absolute).
4. `## Requirement Coverage` follows immediately after the frontmatter.

- [ ] **Step 5: Commit**

```bash
git add github/skills/verification/SKILL.md
git commit -m "feat: add YAML frontmatter to verification artifact template"
```

**Engineer review prompt:**
- Does the `source` field use the spec path exactly as the user passed it to `/verify`, or does it normalize it? Confirm the template instruction is unambiguous.
- The frontmatter is inside a fenced code block (the template). Confirm the nested structure renders correctly in the Copilot Chat output pane and does not cause fencing collisions.

---

## Phase 3: Context Hygiene Persistence to Disk

**Files in this phase:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Locate the end of the context hygiene rules**

In `github/copilot-instructions.md`, find the `## Context Hygiene (MANDATORY)` section. The current last rule reads:

```
- If no files were created or modified, write "None" under Artifacts.
```

- [ ] **Step 2: Add the persistence rule after the last existing rule**

Replace:

```
- If no files were created or modified, write "None" under Artifacts.
```

With:

```markdown
- If no files were created or modified, write "None" under Artifacts.
- After outputting this block, save it to `[Handoffs path]/[ticket-id].md`:
  - If the file doesn't exist: create it with the header `# Handoff Log: [ticket-id]` on line 1, then append the block below the header.
  - If the file exists: append two blank lines, then the block.
  - `[Handoffs path]` comes from the `Handoffs:` line in `conventions/SKILL.md`. If that line is missing or empty, use `docs/handoffs/`.
  - `[ticket-id]` comes from the `ticket:` frontmatter field of any artifact created this phase. If no artifact was created, read the `Active Context` block in `conventions/SKILL.md`.
```

- [ ] **Step 3: Trace scenario to verify**

Mental trace — conventions has `Handoffs: docs/workflow/handoffs/`. Engineer completes the spec phase for PROJ-123. Spec file frontmatter has `ticket: PROJ-123`.

Confirm:
1. Context hygiene block is output in chat (as before).
2. `docs/workflow/handoffs/PROJ-123.md` does not exist → agent creates it with header `# Handoff Log: PROJ-123` and appends the context hygiene block.
3. Plan phase completes for same ticket. File exists → agent appends two blank lines, then the new block.
4. After two phases, `docs/workflow/handoffs/PROJ-123.md` contains two context hygiene blocks separated by blank lines.

Mental trace — conventions has no `Handoffs:` line:
1. Agent defaults to `docs/handoffs/` as the handoff path.
2. Saves to `docs/handoffs/PROJ-123.md`.

- [ ] **Step 4: Verify no skill needs updating**

All skills end with "Apply context hygiene summary, then proceed." — they defer to the `copilot-instructions.md` definition. The new persistence rule is in `copilot-instructions.md`, so all skills pick it up automatically. No skill files need changing.

Check: none of the skill Handoff sections embed the context hygiene rules inline. (They should all say "Apply context hygiene summary" and nothing more.) This is already the case from Plan 1.

- [ ] **Step 5: Commit**

```bash
git add github/copilot-instructions.md
git commit -m "feat: persist context hygiene blocks to per-ticket handoff files on disk"
```

**Engineer review prompt:**
- The persistence rule depends on `Handoffs:` being set in conventions. What happens on a repo where `/setup` was run before Plan 2 was implemented (i.e., no `Handoffs:` line in conventions)? Confirm the fallback `docs/handoffs/` is sufficient and will not cause an error.
- Is the two-blank-line separator between blocks enough to make the handoff file readable by a human scanning it quickly? If not, consider `---` as a visual divider (but note `---` at a line boundary renders as a horizontal rule in Markdown, which may be desirable here).

---

## Phase 4: Deviation Write-Back and Discovery Logging in Execution

**Files in this phase:**
- Modify: `github/skills/execution/SKILL.md`

- [ ] **Step 1: Update inline mode rule 4 to include deviation write-back**

In `github/skills/execution/SKILL.md`, find the inline mode rules (Step 2a):

```
3. Before doing anything not in the plan, stop and ask:
   "This isn't in the plan — should I add it before proceeding?"
4. If deviation is necessary, state it explicitly and get confirmation.
```

Replace with:

```markdown
3. Before doing anything not in the plan, stop and ask:
   "This isn't in the plan — should I add it before proceeding?"
4. If deviation is necessary, state it explicitly, get confirmation, then append to the plan file:
   - Add `## Amendments` at the end of the plan file if the section does not exist.
   - Append: `- [YYYY-MM-DD] Phase [N] (or Step [N] for inline): [what changed from the plan and why it was necessary]`
```

- [ ] **Step 2: Add discovery logging as rule 8 in inline mode**

In the same inline mode section (Step 2a), find the last existing rule:

```
7. Commit at the end: `[ticket-id]: implement [feature name]`
```

Replace with:

```markdown
7. Commit at the end: `[ticket-id]: implement [feature name]`
8. When you encounter an unexpected constraint, system behavior, or implementation detail not in the spec or plan: append to the plan file:
   - Add `## Discoveries` at the end of the plan file if the section does not exist.
   - Append: `- [YYYY-MM-DD] [Brief description of the constraint or behavior discovered]`
```

- [ ] **Step 3: Add rules 8 and 9 to the subagent prompt template (phased mode)**

In `github/skills/execution/SKILL.md`, find the RULES block inside the subagent prompt template in Step 2b:

```
RULES:
1. Execute steps in order. Do not skip any.
2. After each step, run the test command from CONVENTIONS.
3. If any test fails: stop immediately and return the failure output. Do not proceed.
4. Do not make changes not listed in the steps above. If something looks wrong, report back.
5. **REQUIRED:** Follow TDD for any step creating new logic: write the failing test FIRST (RED), then implement (GREEN). No production code without a failing test.
6. **REQUIRED:** If a test fails and the cause is not obvious, follow systematic debugging: reproduce -> isolate -> hypothesise -> verify -> fix. Do not guess.
7. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
```

Replace with:

```markdown
RULES:
1. Execute steps in order. Do not skip any.
2. After each step, run the test command from CONVENTIONS.
3. If any test fails: stop immediately and return the failure output. Do not proceed.
4. Do not make changes not listed in the steps above. If something looks wrong, report back.
5. **REQUIRED:** Follow TDD for any step creating new logic: write the failing test FIRST (RED), then implement (GREEN). No production code without a failing test.
6. **REQUIRED:** If a test fails and the cause is not obvious, follow systematic debugging: reproduce -> isolate -> hypothesise -> verify -> fix. Do not guess.
7. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
8. If a deviation from the plan is necessary and engineer-approved: append to the plan file — add `## Amendments` section at the end if missing, then append: `- [YYYY-MM-DD] Phase [N]: [what changed and why it was necessary]`
9. If you discover an unexpected constraint or system behavior: append to the plan file — add `## Discoveries` section at the end if missing, then append: `- [YYYY-MM-DD] [brief description of what you discovered]`
```

- [ ] **Step 4: Trace scenario to verify**

Mental trace — phased execution of ticket PROJ-123. During Phase 2, the subagent discovers that a third-party API returns a different response format than documented in the spec.

Confirm:
1. Subagent appends to `## Discoveries` in the plan file: `- 2026-04-16 Third-party API returns snake_case keys; spec assumed camelCase. Adjusted deserialization accordingly.`
2. During Phase 3, the engineer asks to deviate from the original caching strategy.
3. Subagent (after engineer confirmation) appends to `## Amendments` in the plan file: `- 2026-04-16 Phase 3: Replaced Redis caching with in-memory cache per engineer decision — Redis setup blocked by infra constraints.`
4. Both sections are at the end of the plan file, below the existing "Rollback Plan" section.

Mental trace — inline execution with a deviation:
1. Agent stops and asks "This isn't in the plan — should I add it before proceeding?"
2. Engineer confirms.
3. Agent appends to `## Amendments`: `- 2026-04-16 Step 4: Added null guard on user.email — discovered email field is nullable in production data.`

- [ ] **Step 5: Commit**

```bash
git add github/skills/execution/SKILL.md
git commit -m "feat: write deviations to plan Amendments and discoveries to plan Discoveries during execution"
```

**Engineer review prompt:**
- The `## Amendments` and `## Discoveries` sections are appended at the end of the plan file. Confirm this does not conflict with the `## Rollback Plan` section that currently closes each plan (they should appear after it, or between it and the end of the file — either is acceptable).
- In phased mode, the subagent has access to the plan file via the content embedded in its prompt. It can write back to the plan file only if it has write access to the repo. Confirm the subagent's tool permissions include `insert_edit_into_file` or equivalent. If not, the write-back must be done by the parent session after reviewing the subagent's output.

---

## Testing Checklist (run after all phases complete)

- [ ] Open `github/skills/conventions/SKILL.md` — confirm `Handoffs:` line is present in `## Artifact Paths`
- [ ] Open `github/skills/setup/SKILL.md` — confirm Step 5 detection includes `docs/handoffs/` and `docs/workflow/handoffs/`; confirm default includes `Handoffs: docs/handoffs/`; confirm Step 6 output template has `Handoffs:       [detected value]`
- [ ] Open `github/skills/verification/SKILL.md` — confirm Metadata Inputs mentions `source`; confirm template starts with YAML frontmatter block; confirm Output Format lists frontmatter
- [ ] Open `github/copilot-instructions.md` — confirm the persistence rule is the last bullet in Context Hygiene; confirm it references `Handoffs:` from conventions with `docs/handoffs/` fallback
- [ ] Open `github/skills/execution/SKILL.md` — confirm inline rule 4 includes write-back to `## Amendments`; confirm rule 8 writes to `## Discoveries`; confirm subagent RULES block has rules 8 and 9
- [ ] End-to-end trace: PROJ-123 goes through spec → plan → execute (one deviation, one discovery) → verify. Verify:
  - `docs/handoffs/PROJ-123.md` created at spec phase, appended at each subsequent phase
  - Plan file has `## Amendments` and `## Discoveries` sections at the end after execution
  - Verification file has YAML frontmatter with `source: [spec path]`

## Rollback Plan

- Revert all phase commits: `git revert HEAD~4` (4 commits, one per phase)
- No data migration required — all changes are to template files; existing artifacts are unaffected
- Existing handoff files created before rollback can be retained as-is or deleted from `docs/handoffs/`
