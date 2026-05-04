# Simple Capability Uplift Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Phase 1 context-efficiency and Phase 2 structural-discipline capabilities to the `github/` workflow system without changing the public slash-command surface.

**Architecture:** Implement the uplift in dependency order: first establish the new reusable primitives (`scripts/`, `protocols/`, `refs/`, `caveman`), then remove obsolete V1 and persona indirection, then thread the new structural-authority model through setup, planning, indexing, execution, and stage review. Documentation updates are coupled to the implementation phases they describe so the human-facing references never lag the behavior.

**Tech Stack:** Markdown artifacts under `github/`, shell scripts under `github/scripts/`, verification via `rg`, `sed`, `find`, `wc`, and direct script execution.

---

## All Files Changed

**Phase 1 — Silent execution + handoff extraction:**
- Create: `github/scripts/run-silent.sh`
- Create: `github/protocols/handoff.md`
- Modify: `github/copilot-instructions.md`
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`

**Phase 2 — Validation + subagent contract + schema relocation:**
- Create: `github/scripts/validate-artifact.sh`
- Create: `github/protocols/subagent-task.md`
- Create: `github/refs/schema.md`
- Delete: `github/skills/SCHEMA.md`
- Delete: `github/skills/validate-artifact/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/protocols/stage-review.md`
- Modify: `github/ARCHITECTURE.md`

**Phase 3 — Caveman mode + agent-file evaluation + V1 removal sweep:**
- Create: `github/skills/caveman/SKILL.md`
- Modify: `github/skills/brainstorming/SKILL.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/context-packet/SKILL.md`
- Modify: `github/skills/index-codebase/SKILL.md`
- Modify: `github/skills/index-knowledge/SKILL.md`
- Modify: `github/skills/cross-repo/SKILL.md`
- Modify: `github/prompts/brainstorm.prompt.md`
- Modify: `github/prompts/execute-plan.prompt.md`
- Modify: `github/prompts/review.prompt.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`
- Modify: `github/ARCHITECTURE.md`
- Delete: `github/agents/design.agent.md`
- Delete: `github/agents/implementation.agent.md`
- Delete: `github/agents/review.agent.md`

**Phase 4 — Structural declarations in conventions + setup:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

**Phase 5 — Architecture-map generation in codebase indexing:**
- Modify: `github/skills/index-codebase/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

**Phase 6 — Plan structural constraints + planning analysis:**
- Modify: `github/refs/schema.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

**Phase 7 — Execution structural protocol + Stage 3 gate:**
- Create: `github/protocols/implementation-structure.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/protocols/stage-review.md`
- Modify: `github/protocols/phase-checkpoint.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

**Phase 8 — Final consistency pass and acceptance verification:**
- Modify as needed: any file above to resolve wording drift or acceptance gaps discovered during verification

---

## Phase 1: Silent Execution + Handoff Extraction

**Files in this phase:**
- Create: `github/scripts/run-silent.sh`
- Create: `github/protocols/handoff.md`
- Modify: `github/copilot-instructions.md`
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`

- [ ] **Step 1: Create `github/scripts/run-silent.sh`**

Write a POSIX-shell-compatible helper that exposes `run_silent()` exactly as specified in the design:
- capture combined stdout/stderr from the invoked command
- print `✓` and return `0` on success
- print the captured output and return the original exit code on failure
- keep the file sourceable so `setup` and `conventions` can reference it directly

- [ ] **Step 2: Create `github/protocols/handoff.md` by extracting the full handoff contract**

Move the full phase-completion block specification out of [github/copilot-instructions.md](/Users/koustavdas/Documents/Obsidian%20Vault/Claude%20Projects/Office/github/copilot-instructions.md), including:
- required block fields
- create-or-append write mechanics
- `log.md` append rule
- `artifact-index.md` append rule
- read-back confirmation requirement
- failure behavior when write confirmation is missing

The content should preserve current handoff behavior verbatim; only the file location changes.

- [ ] **Step 3: Shrink `github/copilot-instructions.md` to pointer-only handoff guidance**

Replace the extracted handoff mechanics with a single pointer line:

```md
Phase completion: follow protocols/handoff.md
```

Then trim the file so it is under 50 lines while preserving:
- priority order
- hard rules
- drift control
- conscious skip protocol
- context hygiene pointer

- [ ] **Step 4: Add silent-test-command guidance to `github/skills/conventions/SKILL.md`**

Extend the Testing section so conventions explicitly carries:

```md
Test command:
Test command (silent):
```

Document that the silent form wraps the normal test command through `run-silent.sh` and is the default during TDD loops and between-step verification.

- [ ] **Step 5: Update `github/skills/setup/SKILL.md` to populate the silent test command**

Add setup instructions that:
- continue detecting the repository’s ordinary test command
- derive the silent form as `run-silent.sh [test command]`
- write both fields into `conventions/SKILL.md`
- leave an existing populated silent field unchanged on re-run

- [ ] **Step 6: Verify Phase 1 behavior**

Run:

```bash
zsh -lc 'source github/scripts/run-silent.sh; run_silent true'
zsh -lc 'source github/scripts/run-silent.sh; run_silent false'
wc -l github/copilot-instructions.md
rg -n "Phase completion: follow protocols/handoff.md|Test command \\(silent\\)" github/copilot-instructions.md github/skills/conventions/SKILL.md github/skills/setup/SKILL.md
```

Expected:
- first command prints only `✓`
- second command returns non-zero and prints failure output
- `github/copilot-instructions.md` line count is `< 50`
- the new pointer and silent-command references are present

- [ ] **Step 7: Commit**

```bash
git add github/scripts/run-silent.sh github/protocols/handoff.md github/copilot-instructions.md github/skills/conventions/SKILL.md github/skills/setup/SKILL.md
git commit -m "workflow: add silent command wrapper and extract handoff protocol"
```

---

## Phase 2: Validation Script + Subagent Contract + Schema Relocation

**Files in this phase:**
- Create: `github/scripts/validate-artifact.sh`
- Create: `github/protocols/subagent-task.md`
- Create: `github/refs/schema.md`
- Delete: `github/skills/SCHEMA.md`
- Delete: `github/skills/validate-artifact/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/protocols/stage-review.md`
- Modify: `github/ARCHITECTURE.md`

- [ ] **Step 1: Create `github/scripts/validate-artifact.sh`**

Implement a deterministic validator that accepts `validate-artifact.sh <artifact-path>` and checks:
- required fields on the V2 primitive records used by the repo
- ID format rules for problems, decisions, requirements, and step nodes
- duplicate ID detection within each primitive array
- `requirement_ids[]` references resolve
- `source_decision` references resolve
- `depends_on[]` references resolve to existing same-or-earlier-step IDs

Keep pass behavior silent by default. On failure, print `FAIL:` lines with field-level paths.

- [ ] **Step 2: Create `github/protocols/subagent-task.md`**

Write the bounded-task protocol under 30 lines, including:
- scope rules forbidding plan/spec/convention edits
- no architectural authority
- ambiguity must be reported, not guessed
- mandatory `SUBAGENT RESULT` output block with the exact fields from the spec

- [ ] **Step 3: Move `github/skills/SCHEMA.md` to `github/refs/schema.md`**

Preserve the schema content byte-for-byte during the move. After the move:
- `github/skills/SCHEMA.md` must not exist
- all skill/protocol references that pointed to `skills/SCHEMA.md` must point to `refs/schema.md`

- [ ] **Step 4: Replace skill-based validation with script-based validation**

Delete `github/skills/validate-artifact/SKILL.md`, then update consumers to call the script:
- `github/skills/spec-writing/SKILL.md`
- `github/skills/planning/SKILL.md`
- `github/skills/execution/SKILL.md`
- `github/skills/review/SKILL.md`
- `github/protocols/stage-review.md` if it references validation flow

Preserve silent-pass behavior: no output on pass, hard stop on fail.

- [ ] **Step 5: Document the new primitives in `github/ARCHITECTURE.md`**

Add or update sections describing:
- `github/scripts/run-silent.sh`
- `github/scripts/validate-artifact.sh`
- `github/protocols/handoff.md`
- `github/protocols/subagent-task.md`
- `github/refs/schema.md`
- removal of `validate-artifact` as a skill

- [ ] **Step 6: Verify Phase 2 behavior**

Run:

```bash
find github -maxdepth 2 \( -path 'github/refs/schema.md' -o -path 'github/scripts/validate-artifact.sh' -o -path 'github/protocols/subagent-task.md' \) | sort
test ! -e github/skills/SCHEMA.md
test ! -e github/skills/validate-artifact/SKILL.md
rg -n "refs/schema.md|validate-artifact.sh|SUBAGENT RESULT" github
zsh github/scripts/validate-artifact.sh docs/superpowers/specs/2026-04-30-simple-capability-uplift-design.md
```

Expected:
- new files exist
- old schema and validator-skill paths are gone
- references use `refs/schema.md` and the shell validator
- validator exits `0` on a known-good V2 artifact

- [ ] **Step 7: Commit**

```bash
git add github/scripts/validate-artifact.sh github/protocols/subagent-task.md github/refs/schema.md github/skills/spec-writing/SKILL.md github/skills/planning/SKILL.md github/skills/execution/SKILL.md github/skills/review/SKILL.md github/protocols/stage-review.md github/ARCHITECTURE.md
git add -u github/skills/SCHEMA.md github/skills/validate-artifact/SKILL.md
git commit -m "workflow: replace artifact validation skill with scripts and refs"
```

---

## Phase 3: Caveman Mode + Agent Cleanup + V1 Removal Sweep

**Files in this phase:**
- Create: `github/skills/caveman/SKILL.md`
- Modify: `github/skills/brainstorming/SKILL.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/context-packet/SKILL.md`
- Modify: `github/skills/index-codebase/SKILL.md`
- Modify: `github/skills/index-knowledge/SKILL.md`
- Modify: `github/skills/cross-repo/SKILL.md`
- Modify: `github/prompts/brainstorm.prompt.md`
- Modify: `github/prompts/execute-plan.prompt.md`
- Modify: `github/prompts/review.prompt.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`
- Modify: `github/ARCHITECTURE.md`
- Delete: `github/agents/design.agent.md`
- Delete: `github/agents/implementation.agent.md`
- Delete: `github/agents/review.agent.md`

- [ ] **Step 1: Create `github/skills/caveman/SKILL.md`**

Write a single-skill file under 80 lines that defines:
- activation triggers: `/caveman`, `caveman mode`, automatic activation inside execution/TDD loops
- one-line status-update rules
- abbreviated file-path and test-result formatting
- prohibition during brainstorming, planning, stage-review findings, and durable artifacts
- deactivation via `/no-caveman` or leaving execution

- [ ] **Step 2: Remove V1 compatibility logic from the workflow skills**

Sweep the V1-only branches out of the six core skills named in the spec:
- `github/skills/spec-writing/SKILL.md`
- `github/skills/planning/SKILL.md`
- `github/skills/execution/SKILL.md`
- `github/protocols/stage-review.md`
- `github/skills/review/SKILL.md`
- `github/skills/verification/SKILL.md` if it still references version gating behavior

Also remove any stale V1 references from adjacent skills if they remain after the main edits.

- [ ] **Step 3: Evaluate and remove the static agent files**

Compare the behavior in:
- `github/agents/design.agent.md`
- `github/agents/implementation.agent.md`
- `github/agents/review.agent.md`

against the corresponding skills and prompts. If the agent files add no unique routing or behavior, delete them and update any prompt text that still refers to them so runtime dispatch points straight to the skills.

- [ ] **Step 4: Thread caveman awareness into execution-facing entry points**

Update:
- `github/skills/execution/SKILL.md`
- `github/prompts/execute-plan.prompt.md`
- `github/prompts/review.prompt.md` only where stage-review precision must explicitly override caveman
- any adjacent skill that talks about execution-loop communication

so the caveman skill is available during execution but explicitly blocked from review-grade outputs.

- [ ] **Step 5: Update phase-1 human docs for caveman, scripts, V1 removal, and static-agent removal**

Refresh:
- `github/WORKFLOW.md`
- `github/CHEAT-SHEET.md`
- `github/ARCHITECTURE.md`

to document:
- `/caveman` and `/no-caveman`
- `run-silent.sh` and `validate-artifact.sh`
- V2-only workflow expectations
- removal of `@Design Agent`, `@Implementation Agent`, and `@Review Agent`
- preserved subagent execution through `SUBAGENT RESULT` blocks

- [ ] **Step 6: Verify the sweep**

Run:

```bash
test ! -d github/agents
rg -n "V1|PLAN_VERSION = 1|BRAINSTORM_VERSION = 1|@Design Agent|@Implementation Agent|@Review Agent|/caveman|/no-caveman|run-silent.sh|validate-artifact.sh|SUBAGENT RESULT" github
wc -l github/skills/caveman/SKILL.md
```

Expected:
- `github/agents` is absent or empty
- the ripgrep command returns no active compatibility headings or static-agent references that the spec forbids
- the new caveman, script, and subagent-contract references are present in the expected docs
- caveman skill is present and under 80 lines

- [ ] **Step 7: Commit**

```bash
git add github/skills/caveman/SKILL.md github/skills/brainstorming/SKILL.md github/skills/planning/SKILL.md github/skills/execution/SKILL.md github/skills/review/SKILL.md github/skills/verification/SKILL.md github/skills/context-packet/SKILL.md github/skills/index-codebase/SKILL.md github/skills/index-knowledge/SKILL.md github/skills/cross-repo/SKILL.md github/prompts/brainstorm.prompt.md github/prompts/execute-plan.prompt.md github/prompts/review.prompt.md github/WORKFLOW.md github/CHEAT-SHEET.md github/ARCHITECTURE.md
git add -u github/agents
git commit -m "workflow: add caveman mode and remove V1 and agent indirection"
```

---

## Phase 4: Structural Declarations in Conventions + Setup

**Files in this phase:**
- Modify: `github/skills/conventions/SKILL.md`
- Modify: `github/skills/setup/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

- [ ] **Step 1: Add the `## Architecture` section to `github/skills/conventions/SKILL.md`**

Insert the exact fields required by the spec:

```md
## Architecture
Layer map:
Forbidden packages:
Simplicity mode:
```

Keep the section in the template, not as repo-specific prose.

- [ ] **Step 2: Teach `github/skills/setup/SKILL.md` to populate the architecture fields**

Add deterministic setup behavior:
- `Layer map:` always `.github/index/architecture.md` in generated repos
- `Forbidden packages:` pre-populate any detected `utils/`, `helpers/`, or `common/` directories
- `Simplicity mode:` default `true`
- re-running setup preserves existing non-empty architecture values

- [ ] **Step 3: Update human-facing docs for the declaration layer**

Document the new architecture section and setup behavior in:
- `github/ARCHITECTURE.md`
- `github/WORKFLOW.md`
- `github/CHEAT-SHEET.md`

This phase should explain what the fields mean, not just note that they exist.

- [ ] **Step 4: Verify the declaration layer**

Run:

```bash
rg -n "^## Architecture|Layer map:|Forbidden packages:|Simplicity mode:" github/skills/conventions/SKILL.md
rg -n "architecture.md|Forbidden packages|Simplicity mode" github/skills/setup/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
```

Expected:
- the template contains the new section and fields
- setup and docs describe how those fields are populated and used

- [ ] **Step 5: Commit**

```bash
git add github/skills/conventions/SKILL.md github/skills/setup/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
git commit -m "workflow: add structural declarations to conventions and setup"
```

---

## Phase 5: Architecture-Map Generation in Codebase Indexing

**Files in this phase:**
- Modify: `github/skills/index-codebase/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

- [ ] **Step 1: Extend `github/skills/index-codebase/SKILL.md` to generate `index/architecture.md`**

Add generation instructions for:
- layered repos: produce Layers, Placement Heuristics, Existing Anti-Patterns, Extension Points
- flat/ambiguous repos: produce the minimal fallback file with a manual-population warning

Ensure the skill still writes `index.md` and module pages as before; `architecture.md` is additive.

- [ ] **Step 2: Document the new indexed artifact**

Update:
- `github/ARCHITECTURE.md` to describe `index/architecture.md` as structural authority
- `github/WORKFLOW.md` to explain that `/index codebase` now emits it and engineers should review it on first run
- `github/CHEAT-SHEET.md` to include the new output in quick-reference form

- [ ] **Step 3: Verify the indexing changes are wired consistently**

Run:

```bash
rg -n "architecture.md|Placement Heuristics|Existing Anti-Patterns|Manual population required" github/skills/index-codebase/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
```

Expected:
- index-codebase describes both the normal and fallback generation paths
- the docs consistently describe `architecture.md` as a generated output of `/index codebase`

- [ ] **Step 4: Commit**

```bash
git add github/skills/index-codebase/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
git commit -m "workflow: generate architecture maps from codebase indexing"
```

---

## Phase 6: Plan Structural Constraints + Planning Analysis

**Files in this phase:**
- Modify: `github/refs/schema.md`
- Modify: `github/skills/planning/SKILL.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

- [ ] **Step 1: Add optional `structural_constraints` to `github/refs/schema.md`**

Extend the PlanArtifact schema with the exact fields from the spec:
- `layers_touched`
- `forbidden_new_packages`
- `simplicity_mode`
- optional `follows_pattern`
- optional `packaging_rationale`

Make the field optional and document the plan-wins authority rule when it conflicts with `architecture.md`.

- [ ] **Step 2: Add a structural-analysis section to `github/skills/planning/SKILL.md`**

Insert the new analysis step after retrieval and before StepNode writing. The flow must:
- read `.github/index/architecture.md` when present
- log the warning and omit the block when absent
- determine layers touched
- propagate forbidden packages
- choose a canonical example path for `follows_pattern`
- require `packaging_rationale` when new packages are introduced
- write the `structural_constraints` block before phases

- [ ] **Step 3: Update docs for plan-time structural authority**

Reflect the new plan header block in:
- `github/ARCHITECTURE.md`
- `github/WORKFLOW.md`
- `github/CHEAT-SHEET.md`

These updates should explain who reads the block and what happens when the plan consciously overrides `architecture.md`.

- [ ] **Step 4: Verify the planning additions**

Run:

```bash
rg -n "structural_constraints|layers_touched|forbidden_new_packages|follows_pattern|packaging_rationale" github/refs/schema.md github/skills/planning/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
```

Expected:
- schema and planning skill both define the same field names
- docs describe the same authority and fallback behavior

- [ ] **Step 5: Commit**

```bash
git add github/refs/schema.md github/skills/planning/SKILL.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
git commit -m "workflow: add structural constraints to plan artifacts"
```

---

## Phase 7: Execution Structural Protocol + Stage 3 Gate

**Files in this phase:**
- Create: `github/protocols/implementation-structure.md`
- Modify: `github/skills/execution/SKILL.md`
- Modify: `github/protocols/stage-review.md`
- Modify: `github/protocols/phase-checkpoint.md`
- Modify: `github/ARCHITECTURE.md`
- Modify: `github/WORKFLOW.md`
- Modify: `github/CHEAT-SHEET.md`

- [ ] **Step 1: Create `github/protocols/implementation-structure.md`**

Write the under-45-line protocol with the ordered checks from the spec:
- prefer modify over create
- placement must be justified by architecture or plan
- new package creation is a stop unless sanctioned
- unscheduled abstractions are a stop
- neighbour-complexity note is informational, not a hard gate
- framework placement rules override convenience

- [ ] **Step 2: Add the simplicity IRON LAW to `github/skills/execution/SKILL.md`**

Insert the exact law near the top of the skill:

```md
> **IRON LAW:** Small code. Existing place. Existing pattern. No new structure unless the plan says so. Before creating any file, read protocols/implementation-structure.md.
```

Then thread the protocol into the new-file creation flow and subagent dispatch flow.

- [ ] **Step 3: Extend `github/protocols/stage-review.md` with Stage 3**

Implement the compact structural-integrity gate:
- runs after Stage 1 PASS and Stage 2 PASS
- checks placement, forbidden packages, incidental source files, duplicate abstractions
- gracefully skips placement checks when `architecture.md` is absent
- fails on real placement/package/duplication violations, but only flags oversize-file complexity as informational

- [ ] **Step 4: Update `github/protocols/phase-checkpoint.md` for Stage 3 output**

Add the new Stage 3 line and, when applicable, the architecture-missing note and conscious-override logging language. Preserve the existing compact checkpoint style.

- [ ] **Step 5: Update docs for the full structural-discipline stack**

In:
- `github/ARCHITECTURE.md`
- `github/WORKFLOW.md`
- `github/CHEAT-SHEET.md`

document the four-layer model:
- declare
- inform
- constrain
- gate

and explain where Stage 3 appears in the workflow.

- [ ] **Step 6: Verify the execution and review wiring**

Run:

```bash
rg -n "IRON LAW|implementation-structure.md|Stage 3|Structural integrity|Conscious structural override" github/skills/execution/SKILL.md github/protocols/implementation-structure.md github/protocols/stage-review.md github/protocols/phase-checkpoint.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
wc -l github/protocols/implementation-structure.md
```

Expected:
- execution skill contains the exact IRON LAW and references the protocol before new-file creation
- Stage 3 exists in review and checkpoint protocols
- docs describe the same structural-discipline model
- `implementation-structure.md` is under 45 lines

- [ ] **Step 7: Commit**

```bash
git add github/protocols/implementation-structure.md github/skills/execution/SKILL.md github/protocols/stage-review.md github/protocols/phase-checkpoint.md github/ARCHITECTURE.md github/WORKFLOW.md github/CHEAT-SHEET.md
git commit -m "workflow: enforce structural discipline during execution and stage review"
```

---

## Phase 8: Final Consistency Pass and Acceptance Verification

**Files in this phase:**
- Modify as needed: files touched in Phases 1–7

- [ ] **Step 1: Run the full acceptance sweep from the spec**

Run:

```bash
wc -l github/copilot-instructions.md github/skills/caveman/SKILL.md github/protocols/subagent-task.md github/protocols/implementation-structure.md
rg -n "V1|PLAN_VERSION = 1|BRAINSTORM_VERSION = 1|@Design Agent|@Implementation Agent|@Review Agent" github
test ! -e github/skills/SCHEMA.md
test ! -d github/agents
rg -n "run-silent.sh|validate-artifact.sh|protocols/handoff.md|protocols/subagent-task.md|Structural Discipline|structural_constraints|Stage 3|architecture.md" github
zsh -lc 'source github/scripts/run-silent.sh; run_silent true'
zsh github/scripts/validate-artifact.sh docs/superpowers/specs/2026-04-30-simple-capability-uplift-design.md
```

Expected:
- `copilot-instructions.md` `< 50` lines
- `caveman/SKILL.md` `< 80` lines
- `subagent-task.md` `< 30` lines
- `implementation-structure.md` `< 45` lines
- forbidden legacy references are gone
- old schema path and static agents are gone
- the new scripts, protocols, docs, structural constraints, and Stage 3 references are present
- `run-silent.sh` passes the success-path check
- `validate-artifact.sh` passes on a valid V2 artifact

- [ ] **Step 2: Resolve any acceptance failures inline**

If any command above fails, fix the exact files implicated and re-run only the failing checks until the full sweep is green.

- [ ] **Step 3: Commit**

```bash
git add github
git commit -m "workflow: complete simple capability uplift"
```

---

## Testing Checklist

- [ ] `zsh -lc 'source github/scripts/run-silent.sh; run_silent true'`
- [ ] `zsh -lc 'source github/scripts/run-silent.sh; run_silent false'`
- [ ] `zsh github/scripts/validate-artifact.sh docs/superpowers/specs/2026-04-30-simple-capability-uplift-design.md`
- [ ] `rg -n "structural_constraints|Stage 3|architecture.md|run-silent.sh|validate-artifact.sh" github`
- [ ] `wc -l github/copilot-instructions.md github/skills/caveman/SKILL.md github/protocols/subagent-task.md github/protocols/implementation-structure.md`
- [ ] `test ! -e github/skills/SCHEMA.md && test ! -d github/agents`

## Rollback Plan

- Revert the most recent phase commit if a failure is isolated to that phase.
- If the uplift must be backed out entirely, revert the phase commits in reverse order from Phase 8 to Phase 1 so the docs and behavior roll back together.
- If the script migration causes issues, restore `github/skills/validate-artifact/SKILL.md` and `github/skills/SCHEMA.md` together; do not restore one without the other.
- If Stage 3 proves too disruptive, revert Phase 7 only and keep the earlier context-efficiency improvements intact.
