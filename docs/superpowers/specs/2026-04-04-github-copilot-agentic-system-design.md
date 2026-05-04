# Design: GitHub Copilot Agentic System — Structural Refactor

**Date:** 2026-04-04  
**Scope:** `.github/` Copilot configuration at `Office/github/`  
**Type:** Structural refactor — no workflow logic changes

---

## Context

The `.github/` Copilot configuration implements a 10-phase structured development workflow
for GitHub Copilot in IntelliJ. The workflow itself is correct and must not change. The
problem is structural:

- `copilot-instructions.md` contains workflow routing and model routing, violating the
  "global constraints only" principle
- Skill files lack consistent formal metadata sections (inputs, outputs, dependencies, handoff)
- Agent files lack formal structure and use generic tool descriptions instead of exact
  IntelliJ tool names
- Agent files have no explicit Skill Usage Mapping (routing lives in copilot-instructions.md)
- `instructions/` folder required by target structure does not exist
- `WORKFLOW.md` will become stale after routing moves to agent files

**Goal:** Structural correctness and clean agentic composition without changing workflow logic.

---

## Core Principles (Non-Negotiable)

1. Skills are the single source of truth for execution logic
2. Agents orchestrate behavior and decide when to use skills
3. Instructions define global constraints only — no workflows
4. Prompts are thin entry points — no logic
5. No duplication across files
6. Each concept exists in exactly one place

---

## Canonical Templates

### Skill (`skills/[name]/SKILL.md`)

```markdown
## Metadata
- **Name:** [skill-name]
- **Description:** [one-line purpose]
- **Phase:** [phase number and name]
- **Inputs:** [what this skill receives to start]
- **Outputs:** [artifact produced]

## When To Use
[Trigger conditions]

## Inputs
[Detail each input]

## Steps
[Numbered, deterministic steps]

## Rules
[Constraints specific to this skill]

## Output Format
[Structure of the artifact produced]

## Dependencies
[File references only — paths, no skill calls]

## Handoff
Next phase: `/[prompt-name]`
[One sentence on what to do next]
```

### Agent (`agents/[name].agent.md`)

```markdown
## Metadata
- **Name:** [agent-name]
- **Description:** [one-line role summary]
- **Phases:** [comma-separated phases this agent handles]

## Role
[Who this agent is and what it owns]

## Responsibilities
- [Responsibility]

## Rules
- [Behavioral constraint]

## Interaction Style
[Tone, what it asks, what it never does]

## Tools
[Exact IntelliJ tool names]

## Skill Usage Mapping
| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
```

### Prompt (`prompts/[name].prompt.md`)

```yaml
---
mode: agent
description: [one-line]
---

**Phase:** [phase name]
**Agent:** @[agent-name]
**Skill:** `.github/skills/[name]/SKILL.md`
**Conventions:** `.github/skills/conventions/SKILL.md`

**Input:** [what the user provides — omit if none]
```

### `copilot-instructions.md` (constraints-only)

```markdown
## Priority Order
1–4 items

## Hard Rules
1–4 rules

## Conscious Skip Protocol
One paragraph
```

---

## Skill Usage Mapping

This table moves from `copilot-instructions.md` into each agent's Skill Usage Mapping section.

### Design Agent

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 1 — Setup | `setup/SKILL.md` | Standard | `/setup` or "set up this repo" |
| 2 — Brainstorm | `brainstorming/SKILL.md` | Premium | `/brainstorm` |
| 3 — Spec | `spec-writing/SKILL.md` | Standard | `/write-spec` |
| 4 — Plan | `planning/SKILL.md` | Premium | `/write-plan` |

### Implementation Agent

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 5 — Execute | `execution/SKILL.md` | Standard | `/execute-plan` |
| 6 — TDD | `tdd/SKILL.md` | Standard | `/tdd` |
| 7 — Debug | `debugging/SKILL.md` | Premium | `/debug` |
| 10 — Quick Task | `execution/SKILL.md` | Standard | `/quick-task` |

### Review Agent

| Phase | Skill | Model Tier | Trigger |
|-------|-------|------------|---------|
| 8 — Verify | `verification/SKILL.md` | Standard | `/verify` |
| 9 — Review | `review/SKILL.md` | Premium | `/review` |

---

## IntelliJ Tool Names (exact)

From the Configure Tools dialog in IntelliJ Copilot Chat settings.

**Design agent:** `read_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`, `show_content`

**Implementation agent:** `read_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`,
`insert_edit_into_file`, `replace_string_in_file`, `create_file`, `apply_patch`,
`run_in_terminal`, `get_terminal_output`, `get_errors`, `open_file`, `run_subagent`

**Review agent:** `read_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`,
`show_content`, `get_errors`, `run_in_terminal`, `get_terminal_output`, `validate_cves`

---

## File Inventory

| Layer | Action | Count |
|-------|--------|-------|
| `copilot-instructions.md` | Strip to constraints-only | 1 |
| `skills/` | Add metadata + missing sections | 10 |
| `agents/` | Add formal structure + tools + routing | 3 |
| `prompts/` | Verify thin; fix if needed | 10 |
| `instructions/` | Create empty folder | 1 new |
| `WORKFLOW.md` | Update routing references | 1 |

**Total:** 25 files modified, 1 created.

---

## Implementation Order (Layer-by-Layer)

1. Strip `copilot-instructions.md`
2. Refactor skill files (workflow order: conventions → setup → brainstorming → spec-writing → planning → execution → tdd → debugging → verification → review)
3. Refactor agent files (design → implementation → review)
4. Verify/tighten prompt files
5. Create `instructions/` folder
6. Update `WORKFLOW.md`

---

## Verification Checklist

- [ ] `copilot-instructions.md` has no routing tables, no model tiers, no session hygiene
- [ ] Every skill file has all 8 sections: Metadata, When To Use, Inputs, Steps, Rules, Output Format, Dependencies, Handoff
- [ ] Every agent file has all 7 sections: Metadata, Role, Responsibilities, Rules, Interaction Style, Tools, Skill Usage Mapping
- [ ] All tool names in agent files match IntelliJ built-in tool list exactly
- [ ] Every prompt is ≤10 lines of content (excluding frontmatter)
- [ ] No skill content duplicated in any agent or prompt
- [ ] `WORKFLOW.md` accurately describes where routing and model selection live
- [ ] Each phase (1–10) has exactly one skill, one prompt, one agent responsible
