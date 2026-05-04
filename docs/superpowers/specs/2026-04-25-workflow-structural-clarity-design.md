---
title: Workflow System Structural Clarity
created: 2026-04-25
updated: 2026-04-25
phase: spec
ticket: workflow-structural-clarity
status: draft
---

# Design Spec: Workflow System Structural Clarity

## Problem

The `github/` workflow system is functionally complete but structurally implicit. Three compounding problems reduce legibility and increase cognitive load for both humans and LLMs executing the system:

1. **Embedded protocols** — Shared execution mechanics (codebase search, verification gates, checkpoint formatting, phase review, context packet loading) are defined inside larger skills rather than as standalone reusable units. They are duplicated up to 3× within a single skill.

2. **Scattered version branching** — v1/v2 artifact format differences (PLAN_VERSION / SPEC_VERSION) produce inline conditional annotations (`(PLAN_VERSION = 2)`) scattered across 16 locations in 3 files, forcing agents to track branching state throughout execution rather than at a single decision boundary.

3. **Implicit contracts** — Skills do not declare their non-goals, making scope boundaries invisible and enabling responsibility creep over time.

## Objective

Improve legibility, modularity, and determinism of the system through structural changes only. No behavioral changes. No new capabilities. No file splits beyond extracting shared protocols.

## Constraints

- Preserve all existing behavior exactly
- No new slash commands or invocable skills
- No changes to agent files, prompt files, or artifact schemas
- No split of any existing skill into multiple skills
- Planning's codebase exploration prose is distinct from the extracted Codebase Search Protocol and is not touched

## Architecture

### Directory Structure Change

```
github/
├── protocols/                    ← NEW: 5 referenced protocol documents
│   ├── codebase-search.md
│   ├── verification-gate.md
│   ├── phase-checkpoint.md
│   ├── stage-review.md
│   └── context-packet-load.md
├── skills/
│   ├── execution/SKILL.md        ← thinner: references protocols; v1/v2 isolated
│   ├── context-packet/SKILL.md   ← v1/v2 isolated; Non-goals added
│   ├── planning/SKILL.md         ← v1/v2 isolated; Non-goals added
│   └── [all other skills]        ← Non-goals field added to Metadata only
├── copilot-instructions.md       ← 3 targeted additions
└── [all other files unchanged]
```

### Skill vs. Protocol Distinction

- **Skills** (`skills/*/SKILL.md`): invocable intent units — represent something an agent deliberately chooses to do. Activated via slash command. Define *what* is being done.
- **Protocols** (`protocols/*.md`): inline execution mechanics — deterministic, non-invocable subroutines. Read via `read_file` and followed in-session. Define *how* a step is executed. Never invoked independently; no slash command; no session boundary.

## Change 1: Protocol Extraction

Five protocols extracted from their current embedded locations into `protocols/`. Each follows the same contract structure: Purpose, Inputs, Outputs, Non-goals.

---

### `protocols/codebase-search.md`

**Purpose:** Locate a specific code element using semantic search with bounded fallback to grep, capped at 2 searches per query.

**Inputs:** A specific, formulated query (what to find — class name, method name, or constant).

**Outputs:** The location of the requested code element, or a "not found" report after exhausting the search budget.

**Non-goals:** Does not modify code. Does not perform broad module exploration. Does not set or read context packet coverage.

**Current location:** `skills/execution/SKILL.md` — "Codebase Search Protocol" section.

**Call sites after extraction:** `skills/execution/SKILL.md` only. Planning's codebase exploration is a different (looser, non-bounded) behavior and is not changed.

**Reference syntax in execution:**
```
Read `.github/protocols/codebase-search.md` and follow it exactly.
```

---

### `protocols/verification-gate.md`

**Purpose:** Ensure no success claim is made without a fresh command execution and pasted terminal output as evidence.

**Inputs:** The claim being made (e.g., "tests pass"). The exact command that proves it.

**Outputs:** A verified assertion with pasted terminal output, or a blocked claim if evidence is absent.

**Non-goals:** Does not determine which command to run (orchestrator responsibility). Does not retry on failure. Does not interpret what the output means.

**Current location:** `skills/execution/SKILL.md` — "Verification Gate" section.

**Call sites after extraction:** `skills/execution/SKILL.md` only (end of Steps 2a, 2b, 2c).

---

### `protocols/phase-checkpoint.md`

**Purpose:** The standard output format for presenting a completed phase to the engineer for review.

**Inputs:**
- Phase N, phase name
- Stage 1 result (from stage-review): PASS/FAIL + plan-listed + actually-changed + unlisted (if FAIL)
- Stage 2 result (from stage-review): PASS/FAIL + finding (if FAIL)
- Test output (pasted)
- Plan review prompt text (from the plan's engineer review prompt for this phase)
- Amendments (if any written during this phase)
- Decisions & assumptions (optional — subagent mode only; omit if not provided)

**Outputs:** The formatted checkpoint block, ready to present to the engineer.

**Non-goals:** Does not run Stage 1 or Stage 2 review. Does not run tests. Does not wait for or handle the engineer's response (orchestrator responsibility).

**Current location:** `skills/execution/SKILL.md` Steps 2b and 2c — the same template duplicated, with one optional field difference (Decisions & Assumptions).

**Call sites after extraction:** `skills/execution/SKILL.md` Steps 2b and 2c. The template is defined once; the optional field is present when the orchestrator provides it.

---

### `protocols/stage-review.md`

**Purpose:** Validate a completed phase for spec compliance (Stage 1) and code quality (Stage 2) before it is presented to the engineer.

**Inputs:**
- Plan listed files — V2: from `phases[N].steps[*].files`; V1: from `**Files in this phase:**` prose section
- Actually changed files — from `git diff --name-status HEAD~1`
- Incidental file patterns — from `conventions/SKILL.md`

**Outputs:**
- Stage 1 result: PASS or FAIL, with plan-listed list, actually-changed list, and (on FAIL) unlisted list
- Stage 2 result: PASS or FAIL, with finding on FAIL (one line: what + where)

**Non-goals:** Does not present the checkpoint (phase-checkpoint protocol responsibility). Does not gate execution (orchestrator responsibility). Does not fix Stage 1 or Stage 2 failures.

**Internal v1/v2:** Stage 1 has isolated `### V2` / `### V1` subsections for plan-listed file resolution. The caller does not need to prepare version-specific inputs — version is read from the plan file's `schema_version` frontmatter within the protocol.

**Current location:** `skills/execution/SKILL.md` Steps 2b and 2c — identical logic duplicated.

**Call sites after extraction:** `skills/execution/SKILL.md` Steps 2b and 2c. Absorbs the two Stage 1 v1/v2 forks that currently appear in execution.

---

### `protocols/context-packet-load.md`

**Purpose:** Load a pre-assembled context packet for a given ticket+phase, and declare the coverage-based access restrictions the caller must enforce.

**Inputs:** Ticket ID, phase number, context packets path (from conventions).

**Outputs:**
- Packet content (full file text, or a null signal if not found)
- Coverage confidence level: `high`, `medium`, or `low`
- Enforcement rules per level (declared in the protocol; applied by the caller)

**Non-goals:** Does not assemble the packet (context-packet skill responsibility). Does not perform code search (codebase-search protocol responsibility). Does not interpret the packet content — callers decide how to use it.

**Subagent note:** In phased-subagent mode (Step 2c), the caller embeds the packet content in the subagent prompt rather than applying enforcement in the parent session. The protocol's output (content + confidence + rules) is the same; usage differs by mode. The enforcement rules declared by the protocol apply inside the subagent.

**Current location:** `skills/execution/SKILL.md` Steps 2a, 2b, and 2c — three near-identical copies with minor variation.

**Call sites after extraction:** `skills/execution/SKILL.md` Steps 2a, 2b, 2c — one reference each, same protocol, caller decides how to use the output.

---

## Change 2: V1/V2 Isolation

### Rule

Version is decided once per skill, at the top, as an explicit version gate. Every step that varies by version gets isolated `### V2` / `### V1` subsections. No inline `(PLAN_VERSION = 2)` annotations mid-logic. An agent executing against v1 reads only `### V1` blocks. An agent executing against v2 reads only `### V2` blocks.

### Standard Formats

**For steps where both versions differ:**
```markdown
### V2 (PLAN_VERSION = 2)
[v2-specific instructions]

### V1 (PLAN_VERSION = 1)
[v1-specific instructions]
```

**For v2-only steps:**
```markdown
### V2 (PLAN_VERSION = 2)
[v2-specific instructions]

### V1 (PLAN_VERSION = 1)
Not applicable — skip this step.
```

The explicit "Not applicable — skip this step" eliminates inference. Agents do not decide whether a missing v1 block means skip or use a default.

### Scope by File

**`skills/execution/SKILL.md`** — 6 version-sensitive locations before extraction, 3 after (2 absorbed into stage-review protocol):

| Location | Change |
|---|---|
| Step 1 version gate | Reformatted as explicit gate block with PLAN_VERSION storage declaration |
| Step 1.5 auto-trigger | → `### V2` / `### V1: Not applicable` subsections |
| Step 2a amendment tracking | → `### V2` / `### V1: Not applicable` subsections |
| Step 2b Stage 1 v1/v2 fork | Absorbed into `stage-review.md` — removed from execution |
| Step 2c conventions injection fork | → `### V2` / `### V1` subsections |
| Step 2c Stage 1 v1/v2 fork | Absorbed into `stage-review.md` — removed from execution |

**`skills/context-packet/SKILL.md`** — 5 version-sensitive locations:

| Location | Change |
|---|---|
| Step 1 version detection | Reformatted as explicit gate block |
| Step 2 phase file count | → `### V2` / `### V1` subsections |
| Step 3 phase file manifest extraction | → `### V2` / `### V1` subsections |
| Step 6.5 decision selection | → `### V2` / `### V1: Not applicable` subsections |
| Step 7 coverage confidence computation | → `### V2` / `### V1` subsections |

**`skills/planning/SKILL.md`** — 5 version-sensitive locations:

| Location | Change |
|---|---|
| Version Gate section | Reformatted to match consistent gate structure |
| Intelligence Retrieval: spec classification | → `### V2` / `### V1` subsections |
| Intelligence Retrieval: decision conflict check | → `### V2` / `### V1` subsections |
| Plan Structure: output templates | → `### V2` / `### V1` subsections (templates already large blocks, relabeled) |
| Cross-Repo Auto-Risk-Signal Injection | → `### V2` / `### V1: Not applicable` subsections |

**Total scope:** 3 version gates reformatted + 11 branch points restructured (2 absorbed into stage-review). All changes are structural — no behavioral content altered.

## Change 3: Explicit Contracts (Non-goals)

One `Non-goals:` field added to each skill's `## Metadata` block. No new sections created.

| Skill | Non-goals |
|---|---|
| setup | Does not create plans, specs, or workflow artifacts; does not run tests; does not modify source files |
| brainstorming | Does not write specs or plans; does not make implementation decisions; does not read the codebase |
| spec-writing | Does not read the codebase; does not create implementation steps; does not produce a plan |
| planning | Does not write code; does not execute steps; does not validate spec against test evidence |
| execution | Does not verify spec completeness (verification skill's job); does not raise a PR; does not assemble context packets |
| context-packet | Does not write code; does not modify plans or specs; does not build the codebase or knowledge index |
| verification | Does not fix failures; does not write new tests; does not raise a PR |
| review | Does not modify code; does not approve or raise PRs; does not re-run tests |
| debugging | Does not write new features; does not fix without root cause identification first |
| tdd | Does not apply to config or infrastructure files without testable behavior; does not write production code before a failing test |
| index-codebase | Does not modify source files or workflow artifacts; does not extract knowledge signals (index-knowledge's job) |
| index-knowledge | Does not modify source files; does not rebuild the codebase index (index-codebase's job); does not resolve contradictions automatically |
| validate-artifact | Does not validate v1 artifacts; does not perform semantic checks; does not auto-fix failures |
| retrieval-protocol | Does not run during brainstorm, spec, execution, or review phases; does not write any files |
| cross-repo | Does not generate exports.md or imports.md automatically; does not enforce cross-repo contracts at execution time |

## Change 4: copilot-instructions.md Alignment

Three targeted additions. No existing content removed.

**Addition 1 — Drift Control rule 7:**
```
7. Stay within phase scope — do not implement, refactor, or plan across multiple phases in a single response
```

**Addition 2 — Priority Order note:**
After the existing 4-item priority list, add:
```
Note: phase-specific procedures are defined in the skill file for the active phase and take precedence
over general behavior patterns described in these instructions.
```

**Addition 3 — Conscious Skip Protocol tightening:**
After "Continue — this is a conscious override, not the default path." add:
```
Skipping a phase does not expand the current phase's scope — complete only the work defined for the active phase.
```

The Context Hygiene block is not changed — it is a mandated universal procedure whose embedded detail ensures consistent handoff behavior across all agents.

## Non-goals of This Design

- No new capabilities introduced
- No behavioral logic modified
- No skill files split into multiple files
- No new slash commands
- No changes to agent files, prompt files, or artifact schemas
- No changes to planning's codebase exploration prose (distinct behavior from codebase-search protocol)
- No changes to WORKFLOW.md, ARCHITECTURE.md, CHEAT-SHEET.md, or SCHEMA.md

## Verification

Each change is verified structurally — no test command applies. Per-change verification:

- **Protocol extraction:** Read `protocols/[name].md` — confirm it contains the exact behavior previously in its source location. Read each call site in execution — confirm the protocol reference resolves and no embedded version of the logic remains.
- **V1/V2 isolation:** For each restructured step, confirm: one gate at the top of the skill; each branch point has both `### V2` and `### V1` subsections; no inline `(PLAN_VERSION = 2)` annotations remain mid-step.
- **Non-goals:** For each skill, confirm `Non-goals:` field is present in `## Metadata`. Confirm no new sections were added.
- **copilot-instructions.md:** Confirm 3 additions are present. Confirm no existing content was removed.
