# Copilot Workflow: Artifact Contracts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate weak artifact contracts (C2) by giving brainstorm, spec, and plan artifacts a defined format, a persisted file, and a machine-readable frontmatter schema — so each phase reads the previous phase's output from disk instead of relying on pasted chat text.

**Architecture:** Three artifact types gain YAML frontmatter (ticket, phase, created, status, source). The brainstorming skill saves its output to a file for the first time; spec-writing accepts that file path as input. The context hygiene summary is converted from a prose description to an explicit fill-in template (standardisation only — persistence to disk is Plan 2). The conventions template and setup skill gain a `Brainstorms` path field to match the existing Specs / Plans / Verifications pattern.

**Tech Stack:** Markdown only — no code, no build system, no test runner. "Verification" for each phase is a concrete scenario trace showing the modified skill text produces the right behavior.

**Spec:** `docs/superpowers/specs/2026-04-16-copilot-workflow-gap-analysis-design.md`

---

## Out of Scope (covered in subsequent plans)

The following gap-analysis items are intentionally deferred:

| Item | Deferred to |
|------|-------------|
| Verification artifact frontmatter | Plan 2 |
| Context hygiene persistence to disk | Plan 2 |
| Per-ticket artifact registry | Plan 2 |
| Execution discovery log | Plan 2 |
| Plan amendment / deviation write-back | Plan 2 |
| Post-ticket learning prompt | Plan 3 |
| Append-only phase/ticket log | Plan 3 |
| Conventions domain segmentation | Plan 3 |
| Semantic search protocol | Plan 3 |
| Artifact index | Plan 3 |

---

> **Execution mode:** phased

## All Files Changed

- `github/skills/conventions/SKILL.md` — Phase 1: add `Brainstorms` line to Artifact Paths template
- `github/skills/setup/SKILL.md` — Phase 1: detect brainstorms directory; add to conventions output
- `github/skills/brainstorming/SKILL.md` — Phase 2: save brainstorm to file at convergence; update outputs and handoff
- `github/skills/spec-writing/SKILL.md` — Phase 3: accept brainstorm file path as input; add frontmatter and Design Rationale to spec template
- `github/skills/planning/SKILL.md` — Phase 4: add frontmatter to plan template
- `github/copilot-instructions.md` — Phase 4: convert context hygiene prose to explicit fill-in template

---

## Phase 1: Artifact Paths — Add Brainstorms Field

**Files in this phase:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`

- [ ] **Step 1: Add Brainstorms path to conventions template**

In `github/skills/conventions/SKILL.md`, find the `## Artifact Paths` section (lines 39–43):

```
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          <e.g. docs/workflow/specs/>
Plans:          <e.g. docs/workflow/plans/>
Verifications:  <e.g. docs/workflow/verifications/>
Brainstorms:    <e.g. docs/workflow/brainstorms/>
```

- [ ] **Step 2: Trace scenario to verify**

Mental trace — a new team member runs `/setup`. Confirm the updated conventions template now contains the `Brainstorms:` field so setup will populate it. Check: the `<e.g. docs/workflow/brainstorms/>` placeholder is present and follows the same format as the other three paths. No other lines changed.

- [ ] **Step 3: Add brainstorms detection logic to setup skill**

In `github/skills/setup/SKILL.md`, find the directory detection block in Step 5 (the list checking `docs/specs/`, `docs/workflow/specs/`, etc.):

```
Check if any of these directories exist:
- `docs/specs/` or `docs/workflow/specs/` → use as specs path
- `docs/plans/` or `docs/workflow/plans/` → use as plans path
- `docs/verifications/` or `docs/workflow/verifications/` → use as verifications path

If none exist, default to:
- Specs: `docs/specs/`
- Plans: `docs/plans/`
- Verifications: `docs/verifications/`
```

Replace with:

```markdown
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

- [ ] **Step 4: Add Brainstorms field to the conventions output template in setup skill**

In `github/skills/setup/SKILL.md`, find the `## Artifact Paths` block inside the Step 6 template (the section that outputs filled-in values like `[detected value]`):

```
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
```

Replace with:

```markdown
## Artifact Paths (relative to project root)

Specs:          [detected value]
Plans:          [detected value]
Verifications:  [detected value]
Brainstorms:    [detected value]
```

- [ ] **Step 5: Trace scenario to verify setup changes**

Mental trace — user runs `/setup` on a repo that has `docs/workflow/brainstorms/`. Confirm:
1. Detection logic finds it and assigns `docs/workflow/brainstorms/` as the brainstorms path.
2. The generated conventions file contains `Brainstorms:    docs/workflow/brainstorms/`.

Mental trace — repo with no brainstorms directory:
1. Detection falls through; default `docs/brainstorms/` is used.
2. Generated conventions file contains `Brainstorms:    docs/brainstorms/`.

- [ ] **Step 6: Commit**

```bash
git add github/skills/conventions/SKILL.md github/skills/setup/SKILL.md
git commit -m "feat: add Brainstorms artifact path to conventions template and setup detection"
```

**Engineer review prompt:**
- Does `Brainstorms: [detected value]` in the setup output template use the same placeholder format (`[detected value]`) as the other three path fields?
- Would running `/setup` on an existing repo that already has `docs/specs/` but no `docs/brainstorms/` produce `Brainstorms: docs/brainstorms/` (the default)? Trace the logic in step 5 to confirm.

---

## Phase 2: Canonical Brainstorm Artifact

**Files in this phase:**
- Modify: `github/skills/brainstorming/SKILL.md`

- [ ] **Step 1: Identify the lines that need changing**

Open `github/skills/brainstorming/SKILL.md`. The sections to modify are:
- **Metadata > Outputs** (line 14): currently `"A structured brainstorm summary — Problem, Success criteria, Constraints, Key risks/edge cases"`
- **Inputs block** (lines 19–22): currently lists `Active Context` from conventions; optionally ticket ID
- **Convergence section** (lines 58–76): currently ends with a chat message and "Does this capture it? If yes, use `/write-spec`..."
- **Output Format** (lines 80–87): describes chat output format
- **Handoff** (lines 92–98): currently "Paste the brainstorm summary as input to `/write-spec`"

- [ ] **Step 2: Update the Outputs field in Metadata**

Replace:
```markdown
- **Outputs:** A structured brainstorm summary — Problem, Success criteria, Constraints, Key risks/edge cases
```

With:
```markdown
- **Outputs:** A brainstorm artifact file saved to `[brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md`
```

- [ ] **Step 3: Update the Inputs block to reference conventions**

The current Inputs block starts after `## Inputs` and ends before the skill body. Replace:

```markdown
- `Active Context` block in `.github/skills/conventions/SKILL.md` (if populated)
- Optionally: ticket ID, one-sentence description of the work
```

With:

```markdown
- `Active Context` block in `.github/skills/conventions/SKILL.md` (if populated)
- `Brainstorms:` path from `.github/skills/conventions/SKILL.md` — where to save the artifact
- Optionally: ticket ID, one-sentence description of the work
```

- [ ] **Step 4: Add file-save step to the Convergence section**

The Convergence section currently ends with this block:

```markdown
When you reach convergence, say:

> "I think I understand enough to write a spec. Here's what we've aligned on:
>
> **Problem:** [1 sentence — specific, not vague]
> **Success criteria:** [bullet list — "X happens when Y" format, each testable]
> **Constraints:** [bullet list]
> **Key risks / edge cases:** [bullet list]
>
> Does this capture it? If yes, use `/write-spec` and paste this summary as input."
```

Replace with:

```markdown
When you reach convergence:

1. Read `Brainstorms:` path from `.github/skills/conventions/SKILL.md`.
2. Save the brainstorm artifact to `[brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md` using this exact template — fill in every field:

```yaml
---
ticket: [TICKET-ID]
phase: brainstorm
created: [YYYY-MM-DD]
status: complete
---

# Brainstorm: [TICKET-ID] — [Feature Name]

## Problem
[one specific sentence]

## Success Criteria
- [X happens when Y]
- [repeat for each criterion]

## Constraints
- [one constraint per bullet]

## Key Risks / Edge Cases
- [one risk or edge case per bullet]
```

3. Then say:

> "I think I understand enough to write a spec. Here's what we've aligned on:
>
> **Problem:** [1 sentence — specific, not vague]
> **Success criteria:** [bullet list — "X happens when Y" format, each testable]
> **Constraints:** [bullet list]
> **Key risks / edge cases:** [bullet list]
>
> Brainstorm saved to `[full path]`.
>
> Does this capture it? If yes: `/write-spec [full path]`"
```

- [ ] **Step 5: Update the Output Format section**

Replace:

```markdown
## Output Format

A brainstorm summary containing:
- **Problem:** one specific sentence
- **Success criteria:** bullet list, each in "X happens when Y" format and testable
- **Constraints:** bullet list
- **Key risks / edge cases:** bullet list
```

With:

```markdown
## Output Format

A brainstorm artifact file at `[brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md` containing:
- YAML frontmatter (`ticket`, `phase`, `created`, `status`)
- `## Problem` — one specific sentence
- `## Success Criteria` — bullet list, each in "X happens when Y" format and testable
- `## Constraints` — bullet list
- `## Key Risks / Edge Cases` — bullet list

Also: a convergence message in chat with the same content plus the saved file path.
```

- [ ] **Step 6: Update the Handoff section**

Replace:

```markdown
## Handoff

Next phase: `/write-spec`

Paste the brainstorm summary as input to `/write-spec` along with the ticket ID.

Start a new chat. Recommended: **Standard**. Use `/write-spec`.

Apply context hygiene summary, then proceed.
```

With:

```markdown
## Handoff

Next phase: `/write-spec`

Pass the brainstorm artifact path: `/write-spec [brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md`

The brainstorm summary is read from the file — do not paste the chat text.

Start a new chat. Recommended: **Standard**. Use `/write-spec`.

Apply context hygiene summary, then proceed.
```

- [ ] **Step 7: Trace scenario to verify**

Mental trace — user runs `/brainstorm` for ticket `PROJ-123`. Conventions has `Brainstorms: docs/brainstorms/`. Brainstorm completes.

Confirm:
1. Agent reads `docs/brainstorms/` from conventions.
2. Agent creates `docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md` with filled frontmatter and four populated sections.
3. Convergence message in chat ends with "Brainstorm saved to `docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`." and shows `/write-spec docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`.
4. Chat text no longer says "paste this summary as input."

- [ ] **Step 8: Commit**

```bash
git add github/skills/brainstorming/SKILL.md
git commit -m "feat: save brainstorm output to canonical artifact file at convergence"
```

**Engineer review prompt:**
- In Step 4, the fenced code block for the YAML frontmatter is inside a larger fenced code block for the skill instruction. Check that the nested fencing renders correctly in the target environment (GitHub Copilot skill viewer). If it causes a rendering issue, use an indented block instead of triple-backtick for the inner template.
- Does the convergence message tell the user the full artifact path, not just the filename? (Should be the full relative path from project root.)

---

## Phase 3: Spec Template — Brainstorm Input + Frontmatter + Design Rationale

**Files in this phase:**
- Modify: `github/skills/spec-writing/SKILL.md`

- [ ] **Step 1: Update Inputs to accept brainstorm file path**

In `github/skills/spec-writing/SKILL.md`, find the Metadata Inputs line:

```markdown
- **Inputs:** Brainstorm summary (problem, success criteria, constraints, edge cases) + ticket ID
```

Replace with:

```markdown
- **Inputs:** Brainstorm artifact file path (output of `/brainstorm`) — the file is read directly; do not paste the chat summary
```

- [ ] **Step 2: Update the Inputs block in the skill body**

The current Inputs block (before the skill body separator `---`) reads:

```markdown
- Brainstorm summary: problem statement, success criteria, constraints, key risks/edge cases
- Ticket ID (from conventions ticket format)
```

Replace with:

```markdown
- Brainstorm artifact file path (e.g. `docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`)
  — Read the file. Extract: problem, success criteria, constraints, risks. The ticket ID is in the frontmatter.
- If the brainstorm file is missing: stop and ask for the file path. Do not accept a pasted summary — file provenance is required.
```

- [ ] **Step 3: Add frontmatter to the spec template**

In `github/skills/spec-writing/SKILL.md`, find the start of the spec template block:

```markdown
```markdown
# Spec: [TICKET-ID] — [Feature Name]

## Problem Statement
```

Replace with:

```markdown
```markdown
---
ticket: [TICKET-ID]
phase: spec
created: [YYYY-MM-DD]
status: draft
source: [brainstorm-file-path]
---

# Spec: [TICKET-ID] — [Feature Name]

## Problem Statement
```

- [ ] **Step 4: Add Design Rationale section to the spec template**

In the spec template, find the `## Architecture / Design Decisions` section:

```markdown
## Architecture / Design Decisions
Which files or systems change? Why this approach over alternatives?
(Brief for small changes, detailed for cross-system changes)
```

Replace with:

```markdown
## Architecture / Design Decisions
Which files or systems change? Why this approach over alternatives?
(Brief for small changes, detailed for cross-system changes)

## Design Rationale
Why this design was chosen over alternatives. This section is permanent — never remove it as the spec evolves.

- **Chosen:** [one sentence: what was chosen and the primary reason]
- **Rejected: [alternative name]** — [reason it was ruled out]

(Add one "Rejected" line per alternative considered during brainstorm. If no alternatives were explored, write: "No alternatives surfaced during brainstorm.")
```

- [ ] **Step 5: Update the Output Format section to mention frontmatter**

Find:

```markdown
## Output Format

Spec file at `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md` containing:
- Problem Statement, Solution Approach, Requirements (each testable), Architecture/Design Decisions, Risks & Dependencies, Testing Strategy
```

Replace with:

```markdown
## Output Format

Spec file at `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md` containing:
- YAML frontmatter (`ticket`, `phase`, `created`, `status`, `source`)
- Problem Statement, Solution Approach, Requirements (each testable), Architecture/Design Decisions, Design Rationale, Risks & Dependencies, Testing Strategy
```

- [ ] **Step 6: Trace scenario to verify**

Mental trace — user runs `/write-spec docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`.

Confirm:
1. Agent reads the brainstorm file (does not ask for pasted text).
2. Ticket ID is extracted from the brainstorm frontmatter (`ticket: PROJ-123`).
3. Generated spec file starts with filled YAML frontmatter, including `source: docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`.
4. Spec contains a `## Design Rationale` section after `## Architecture / Design Decisions`.
5. If the brainstorm file path is missing (user only types `/write-spec` with no argument), agent stops and asks for the file path.

- [ ] **Step 7: Commit**

```bash
git add github/skills/spec-writing/SKILL.md
git commit -m "feat: spec accepts brainstorm file input; add frontmatter and Design Rationale section"
```

**Engineer review prompt:**
- Does the `source` field in the spec frontmatter use the brainstorm file path exactly as received (the argument passed to `/write-spec`), or does it normalize to an absolute path? Confirm the expected behavior and check the template instruction is unambiguous.
- The "Rejected: [alternative]" line uses inline brackets. Confirm this doesn't collide with Copilot's prompt variable syntax in the target environment.

---

## Phase 4: Plan Frontmatter + Context Hygiene Fill-in Template

**Files in this phase:**
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Add frontmatter to the plan template in planning/SKILL.md**

In `github/skills/planning/SKILL.md`, find the start of the plan structure template (the `~~~markdown` fenced block):

```markdown
~~~markdown
# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased]
```

Replace with:

```markdown
~~~markdown
---
ticket: [TICKET-ID]
phase: plan
created: [YYYY-MM-DD]
status: draft
source: [spec-file-path]
---

# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased]
```

- [ ] **Step 2: Trace scenario for plan frontmatter**

Mental trace — planner writes a plan for `PROJ-123`. Spec is at `docs/specs/2026-04-16-PROJ-123-feature.md`.

Confirm: plan file starts with filled YAML frontmatter where `ticket: PROJ-123`, `phase: plan`, `source: docs/specs/2026-04-16-PROJ-123-feature.md`.

- [ ] **Step 3: Convert context hygiene prose to fill-in template in copilot-instructions.md**

In `github/copilot-instructions.md`, find the entire `## Context Hygiene (MANDATORY)` section (lines 37–45):

```markdown
## Context Hygiene (MANDATORY)

After completing every phase — before any handoff — produce a context hygiene summary:

1. **Summary:** ≤5 bullet points capturing the key decisions and outcomes of this phase
2. **Artifacts:** List every file created or modified during this phase (full paths)
3. **Continuation:** State the next `/command` to use, with any required inputs

This pattern resets context for the next phase. Follow it even when staying in the same chat.
```

Replace with:

```markdown
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
```

- [ ] **Step 4: Verify context hygiene change is not a breaking change for existing skills**

Check that every skill still ends with "Apply context hygiene summary, then proceed." — these references still work because the definition has moved to a more explicit template, not been renamed. The phrase "Apply context hygiene summary" now means "output the filled-in block defined in copilot-instructions.md."

Grep confirmation — run mentally: every skill's Handoff section contains "Apply context hygiene summary, then proceed." and none of them embed the old prose description inline (they all defer to copilot-instructions.md). The skills do not need updating.

- [ ] **Step 5: Trace scenario for context hygiene template**

Mental trace — engineer completes the spec phase for `PROJ-123`. Spec saved to `docs/specs/2026-04-16-PROJ-123-brainstorm.md`.

Confirm the agent outputs:

```
---
**Phase complete:** Spec

**Summary:**
- Formalised brainstorm output into testable requirements
- Added Design Rationale: chose X over Y because Z
- All 4 requirements are specific and testable

**Artifacts:**
- Created: `docs/specs/2026-04-16-PROJ-123-brainstorm.md` — spec with frontmatter and Design Rationale

**Next:** `/write-plan docs/specs/2026-04-16-PROJ-123-brainstorm.md`

---
```

Key checks: full file path present, exact next command with file argument, no unfilled brackets.

- [ ] **Step 6: Commit**

```bash
git add github/skills/planning/SKILL.md github/copilot-instructions.md
git commit -m "feat: add frontmatter to plan template; convert context hygiene to explicit fill-in template"
```

**Engineer review prompt:**
- The context hygiene block uses `---` as a visual separator. In some Markdown renderers, a `---` at the start of a block can be interpreted as frontmatter. Does the block appear correctly in the Copilot Chat output pane, or does it need a different separator (e.g., `===` or `***`)?
- After this change, does each skill's Handoff section need any update, or does "Apply context hygiene summary, then proceed." continue to work as a reference to the now-explicit template in `copilot-instructions.md`?

---

## Testing Checklist (run after all phases complete)

- [ ] Open `github/skills/conventions/SKILL.md` — confirm `Brainstorms:` line is present in `## Artifact Paths`
- [ ] Open `github/skills/setup/SKILL.md` — confirm detection logic includes brainstorms directory variants and default; confirm output template includes `Brainstorms: [detected value]`
- [ ] Open `github/skills/brainstorming/SKILL.md` — confirm Convergence section saves file before showing chat message; confirm Handoff says "pass file path" not "paste summary"
- [ ] Open `github/skills/spec-writing/SKILL.md` — confirm Inputs blocks reject pasted summaries; confirm spec template has frontmatter block at top; confirm `## Design Rationale` section present after `## Architecture / Design Decisions`
- [ ] Open `github/skills/planning/SKILL.md` — confirm plan template starts with frontmatter block
- [ ] Open `github/copilot-instructions.md` — confirm `## Context Hygiene` section contains the fill-in template block, not the old prose
- [ ] Run full end-to-end scenario trace: PROJ-123 goes through brainstorm → spec → plan. Verify brainstorm file is created, spec reads it and sets `source:`, plan reads spec and sets `source:`, context hygiene block at each phase end is filled with no brackets

## Rollback Plan

- Revert all phase commits: `git revert HEAD~4` (4 commits, one per phase)
- No data migration required — all changes are to template files; existing artifacts are unaffected
