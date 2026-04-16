---
name: spec-writing
description: Creates a design specification from brainstorm output. Use when writing a spec for a new feature, bug fix, or change. Input is the brainstorm summary. Output is a spec file saved to the specs path defined in conventions.
---

## Metadata

- **Name:** spec-writing
- **Description:** Formalises brainstorm output into a testable design specification before any planning or implementation begins.
- **Phase:** 3 — Spec
- **Inputs:** Brainstorm artifact file path (output of `/brainstorm`) — the file is read directly; do not paste the chat summary
- **Outputs:** Spec file at `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`

## When To Use

After a `/brainstorm` session has reached convergence and produced a summary. Do not write a spec without a brainstorm summary — if one is missing, run `/brainstorm` first. For `/quick-task` paths, a spec may be consciously skipped; note this in the plan header.

## Inputs

- Brainstorm artifact file path (e.g. `docs/brainstorms/2026-04-16-PROJ-123-brainstorm.md`)
  — Read the file. Extract: problem, success criteria, constraints, risks. The ticket ID is in the frontmatter.
- If the brainstorm file is missing: stop and ask for the file path. Do not accept a pasted summary — file provenance is required.

---

You are in spec phase. Create a design specification before any code is written.

**Input needed:** the brainstorm summary (problem, success criteria, constraints, edge cases)
and the ticket ID.

Read `.github/skills/conventions/SKILL.md` for the spec file path and ticket format.

Create the spec file at: `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`

## Spec Structure

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
What is broken or missing? Why does it matter?
(1–3 sentences, concrete and specific)

## Solution Approach
What are you building or fixing? High-level approach — describe the solution, not the code.
(2–3 sentences)

## Requirements

For each requirement, ask: "Can I write a failing test for this?"
If not, make it more specific until you can.

- [ ] Requirement 1: [specific, testable — "X returns Y when Z"]
- [ ] Requirement 2: [specific, testable]
- [ ] Edge case: [how the system handles the edge case from brainstorm]
- [ ] Constraint: [non-functional: performance, security, compatibility]

## Architecture / Design Decisions
Which files or systems change? Why this approach over alternatives?
(Brief for small changes, detailed for cross-system changes)

## Design Rationale
Why this design was chosen over alternatives. This section is permanent — never remove it as the spec evolves.

- **Chosen:** [one sentence: what was chosen and the primary reason]
- **Rejected: [alternative name]** — [reason it was ruled out]

(Add one "Rejected" line per alternative considered during brainstorm. If no alternatives were explored, write: "No alternatives surfaced during brainstorm.")

## Risks & Dependencies
- What existing behaviour could break?
- What other code or system must work first?
- What assumptions in this spec could turn out to be wrong?

## Testing Strategy
- Unit tests: [what to test in isolation]
- Integration tests: [cross-system scenarios to verify]
- Manual testing: [user-facing behaviour to walk through step by step]
```

For every requirement: if you cannot describe a failing test for it, push back and make it
more specific before accepting it.

## Decision Conflict Check (run after the Architecture section is written, before Self-Review)

1. Read the `## Architecture / Design Decisions` section of the spec you just drafted. List every module, service, or system named or implied by the design.

2. Read `Codebase Index:` path from `.github/skills/conventions/SKILL.md`. For each identified module, attempt to read `[codebase-index-path]/[module].md`. Extract the `## Decisions` section only.
   - If the index does not exist, or a module page does not exist: skip that module.
   - If no module pages are found at all: note `_Decision check: index not available — [YYYY-MM-DD]_` at the end of `## Architecture / Design Decisions` and proceed to Self-Review.

3. Compare each recorded decision against the spec's architectural choices. Flag a conflict when any of these are true:
   - The spec's design directly contradicts a recorded decision (proposes X where the decision chose not-X).
   - The spec weakens a load-bearing assumption that a recorded decision depends on.
   - The spec re-proposes an alternative that appears as `Rejected:` in a module's `## Decisions`.

4. **If one or more conflicts are found:** Stop. Do not proceed to Self-Review or output the spec. Present each conflict to the engineer:
   > "**Decision conflict — `[module-name]`:** A recorded decision states: '[exact decision text from the module page].'
   > Your spec [one sentence describing how the spec conflicts].
   > Options:
   > **A** — Revise the spec to align with the recorded decision.
   > **B** — Override: I'll add a `## Design Override` section and Job B will pick it up on the next `/index knowledge` run."
   Wait for the engineer to choose A or B for each conflict. Apply A (revise the spec) or B (add override section) before continuing.
   **Override section format (option B):**
   Add this section to the spec immediately before `## Risks & Dependencies`:
   ```
   ## Design Override
   **Overrides:** [module-name] decision from [YYYY-MM-DD] [TICKET-ID]
   **Reason:** [engineer's stated reason for overriding]
   ```

5. **If no conflicts:** Note at the end of `## Architecture / Design Decisions`:
   `_Decision check: no conflicts found — [YYYY-MM-DD]_`
   Proceed to Self-Review.

---

## Self-Review (before handoff)

Before handing off to `/write-plan`, review the spec you just wrote. Fix issues inline — no separate review cycle.

1. **Placeholder scan:** Search for "TBD", "TODO", "implement later", `[placeholder]` syntax, or any vague language. Replace with specifics.
2. **Testability check:** For every requirement, can you write a failing test? If not, rewrite the requirement until you can.
3. **Internal consistency:** Do the requirements, architecture, and testing strategy all describe the same system? Flag contradictions.
4. **Scope check:** Does any requirement belong in a separate ticket? If so, remove it and note it as a follow-up.

## Output Format

Spec file at `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md` containing:
- YAML frontmatter (`ticket`, `phase`, `created`, `status`, `source`)
- Problem Statement, Solution Approach, Requirements (each testable), Architecture/Design Decisions, Design Rationale, Risks & Dependencies, Testing Strategy

## Dependencies

- `.github/skills/conventions/SKILL.md` — for specs path and ticket format

## Handoff

Next phase: `/write-plan`

After spec is reviewed and approved, use `/write-plan` with the spec file path as input.

Start a new chat. Recommended: **Premium**. Use `/write-plan`.

Apply context hygiene summary, then proceed.
