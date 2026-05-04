# Copilot Enterprise Plugin-First Workflow v1 — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-05-03-copilot-enterprise-plugin-first-v1-design.md`
**Branch:** `feat/copilot-enterprise-plugin-first-v1`
**Goal:** Greenfield build. Replace sub-par existing implementations. Drop `.github/` into any office repo, run `/setup-workflow` once, full workflow available from IntelliJ Copilot Chat.

**Philosophy:** HumanLayer 12-Factor Agents — human approval as first-class tool, bounded per-phase agents, stateful artifact-based resumption.

---

## Slice 1 — Foundation
**Blocked by:** None

**What:** Plugin-first behavioral contract, tech-stack auto-detection, manifest demotion, workflow editing rules.

**Files:**

Create:
- `.github/instructions/workflow.instructions.md` — applyGlob `.github/**`, rules: schema versioning on edit, contract scope enforcement, validator test requirements, governance tier classification
- `.github/agents/` directory placeholder (`.gitkeep`)
- `.github/tasks/` directory placeholder (`.gitkeep`)
- `workflow/config.yaml` — written by `/setup-workflow`, not manually edited

Rewrite:
- `.github/copilot-instructions.md` — under 80 lines: what this repo is, slash commands list, phase order, permission ladder (Tier 1–4 summary), output contract (status blocks not prose), CLI handoff rules, reference to `workflow/config.yaml`, instruction hierarchy
- `.github/prompts/setup-workflow.prompt.md` — full rewrite: auto-detect tech stack from `build.gradle`/`pom.xml`/`package.json`/`pyproject.toml`/`Makefile`/`Cargo.toml`, write `workflow/config.yaml` with all required fields

Demote:
- `.github/ai-workflow/manifest.yaml` — remove LLM instruction language, retain only CLI/validator registry fields

**Acceptance criteria:**
- [ ] `copilot-instructions.md` is under 80 lines and contains no manifest-load instructions
- [ ] `copilot-instructions.md` references `workflow/config.yaml` for project-specific values
- [ ] `/setup-workflow` detects tech stack and populates all `project.*` and `commands.*` fields in `workflow/config.yaml`
- [ ] `instructions/workflow.instructions.md` applies to `.github/**` via applyGlob
- [ ] Manifest contains no behavioral instructions for LLMs
- [ ] `.github/tasks/` directory exists

---

## Slice 2 — GrillRecord phase
**Blocked by:** Slice 1

**What:** Structured Q&A phase replacing brainstorm + write-spec. Produces validated GrillRecord with architecture decisions.

**Files:**

Create:
- `.github/ai-workflow/schemas/grill.schema.json` — fields: `artifact_type`, `schema_version`, `task_id`, `primary_surface`, `secondary_surfaces_allowed`, `goal`, `problem_statement`, `assumptions[]`, `questions[]`, `risks[]`, `constraints[]`, `approach[]` (each: `decision`, `rationale`, `alternatives_rejected[]`), `success_criteria[]`, `decision`, `open_blockers[]`, `validated_under`
- `.github/agents/grill.md` — multi-turn structured Q&A agent, context-restricted to task scope, produces GrillRecord, asks one question at a time, provides recommended answer per question, final output is GrillRecord YAML saved to `.github/tasks/TASK-{NNN}/grill.yaml`
- `.github/ai-workflow/artifacts/examples/grill-valid.yaml` — complete valid GrillRecord example
- `.github/ai-workflow/artifacts/examples/grill-missing-approach.yaml` — invalid: missing `approach` block
- `.github/ai-workflow/artifacts/examples/grill-missing-required.yaml` — invalid: missing required field

Rewrite:
- `.github/prompts/grill.prompt.md` — thin-wrap (~5 lines): invoke grill agent via `#file:` reference

Delete:
- `.github/ai-workflow/schemas/brainstorm.schema.json`
- `.github/ai-workflow/artifacts/examples/brainstorm-*.yaml` (if any)

**Acceptance criteria:**
- [ ] `grill.schema.json` validates all required fields including `approach[]` sub-fields
- [ ] `grill.md` agent restricts context to task scope (not whole repo)
- [ ] `grill.md` agent asks one question at a time with recommended answer
- [ ] Agent output includes `decision: proceed | stop` gate before plan is created
- [ ] `grill.prompt.md` is ≤10 lines and delegates entirely to agent
- [ ] Valid example passes `validate-artifact`, both invalid examples fail with clear error

---

## Slice 3 — PlanArtifact phase
**Blocked by:** Slice 2

**What:** Scope-locked plan grounded in GrillRecord. Declares file scope, context-packet requirement, preferred surface per step.

**Files:**

Create:
- `.github/agents/write-plan.md` — sees GrillRecord + declared in-scope files only, produces PlanArtifact, refuses to plan out-of-scope files, declares `context_packet_required` and `preferred_surface` per step, final output saved to `.github/tasks/TASK-{NNN}/plan.yaml`
- `.github/ai-workflow/artifacts/examples/plan-valid.yaml` — complete valid PlanArtifact example
- `.github/ai-workflow/artifacts/examples/plan-scope-violation.yaml` — invalid: file in steps not in `files_in_scope`
- `.github/ai-workflow/artifacts/examples/plan-missing-context-packet-path.yaml` — invalid: `context_packet_required: true` but no `context_packet_path`

Rewrite:
- `.github/ai-workflow/schemas/plan.schema.json` — canonical name `PlanArtifact`, add: `primary_surface`, `secondary_surfaces_allowed`, `context_packet_required`, `context_packet_path`, `files_in_scope[]`, `files_out_of_scope[]`
- `.github/prompts/write-plan.prompt.md` — thin-wrap: invoke write-plan agent

Delete:
- `.github/ai-workflow/schemas/spec.schema.json`
- `.github/ai-workflow/artifacts/examples/spec-*.yaml` (if any)

**Acceptance criteria:**
- [ ] Plan schema uses `artifact_type: PlanArtifact`
- [ ] Plan schema requires `files_in_scope`, `context_packet_required`, per-step `preferred_surface`
- [ ] `write-plan.md` agent refuses to include files not declared in scope
- [ ] Validator blocks plan artifact when `context_packet_required: true` and `context_packet_path` absent
- [ ] Valid example passes, both invalid examples fail with clear error

---

## Slice 4 — Execute-plan + CLI handoff
**Blocked by:** Slice 3

**What:** Scope-bounded execution agent with explicit human-approved CLI handoff and context-packet gating.

**Files:**

Create:
- `.github/agents/execute-plan.md` — bounded to plan-declared file scope, refuses out-of-scope edits, enforces CLI handoff protocol (3 triggers), produces ExecutionRecord, saves to `.github/tasks/TASK-{NNN}/execution.yaml`
- `.github/ai-workflow/artifacts/examples/execution-valid.yaml` — complete valid ExecutionRecord example

Rewrite:
- `.github/ai-workflow/schemas/execution.schema.json` — canonical name `ExecutionRecord`, add `primary_surface`, `secondary_surfaces_allowed`, `cli_handoff_approved`, `cli_handoff_block`
- `.github/prompts/execute-plan.prompt.md` — thin-wrap: invoke execute-plan agent
- `.github/prompts/context-packet.prompt.md` — full rewrite: produces context-packet artifact, scoped to plan-declared files

Update:
- `.github/ai-workflow/validators/validate-plan-scope` — enforce context-packet gating: block execution when `context_packet_required: true` and no context-packet artifact in task folder

**CLI handoff block format** (embedded in agent and enforced by execute-plan.md):
```
--- CLI HANDOFF REQUEST ---
Reason: <why CLI is needed>
Task path: .github/tasks/TASK-{NNN}/
Allowed commands: [list]
Allowed files: [list from plan scope]
Blocked actions: [list]
Expected return artifact: ExecutionRecord at .github/tasks/TASK-{NNN}/execution.yaml
HUMAN APPROVAL REQUIRED before switching to terminal.
---
```

**CLI handoff triggers:**
1. Plan step declares `preferred_surface: copilot_cli`
2. Verification requires running commands
3. Scope spans >5 files with non-trivial changes

**Acceptance criteria:**
- [ ] Execute-plan agent refuses to touch files not in `plan.files_in_scope`
- [ ] CLI handoff block appears for all 3 trigger conditions
- [ ] Agent waits for explicit human approval before proceeding past handoff block
- [ ] Validator blocks execute-plan when `context_packet_required: true` and no context-packet artifact exists
- [ ] ExecutionRecord uses canonical `artifact_type: ExecutionRecord`
- [ ] Valid example passes validator

---

## Slice 5 — Verify phase
**Blocked by:** Slice 4

**What:** Evidence-backed verification — command output required, no claim-only completion.

**Files:**

Create:
- `.github/ai-workflow/artifacts/examples/verification-valid.yaml` — complete valid VerificationRecord with command output
- `.github/ai-workflow/artifacts/examples/verification-missing-output.yaml` — invalid: no command output

Rewrite:
- `.github/ai-workflow/schemas/verification.schema.json` — canonical name `VerificationRecord`, add `primary_surface`, `secondary_surfaces_allowed`, require `command_output` field (non-empty)
- `.github/prompts/verify.prompt.md` — full rewrite: runs verification commands, records output verbatim, saves VerificationRecord to `.github/tasks/TASK-{NNN}/verification.yaml`, never claims success without command output

Update:
- `.github/ai-workflow/validators/validate-artifact` — enforce `command_output` non-empty for VerificationRecord

**Acceptance criteria:**
- [ ] VerificationRecord schema uses canonical `artifact_type: VerificationRecord`
- [ ] Schema requires `command_output` field, non-empty
- [ ] Verify prompt refuses to produce VerificationRecord without actual command output
- [ ] Valid example passes validator; missing-output example fails

---

## Slice 6 — Review phase
**Blocked by:** Slice 5

**What:** Scope-comparison gate — catches scope creep before merge.

**Files:**

Create:
- `.github/ai-workflow/artifacts/examples/review-valid.yaml` — valid ReviewRecord, changed files match plan scope
- `.github/ai-workflow/artifacts/examples/review-scope-mismatch.yaml` — invalid: changed file not in plan scope

Rewrite:
- `.github/ai-workflow/schemas/review.schema.json` — canonical name `ReviewRecord`, add `primary_surface`, `secondary_surfaces_allowed`, `scope_violations[]`
- `.github/prompts/review.prompt.md` — full rewrite: compares changed files vs `plan.files_in_scope`, records any `scope_violations`, saves ReviewRecord to `.github/tasks/TASK-{NNN}/review.yaml`

Update:
- `.github/ai-workflow/validators/validate-review-gate` — fail if `scope_violations` non-empty

**Acceptance criteria:**
- [ ] ReviewRecord schema uses canonical `artifact_type: ReviewRecord`
- [ ] Review prompt diffs changed files against plan scope, not just claims
- [ ] Scope violations recorded in `scope_violations[]` field
- [ ] Valid example passes; scope-mismatch example fails validator

---

## Slice 7 — QuickTask phase
**Blocked by:** Slice 2 (escalation target is `/grill`)

**What:** Lightweight path for small changes with automatic escalation when scope, risk, or uncertainty grows.

**Files:**

Create:
- `.github/ai-workflow/artifacts/examples/quick-task-valid.yaml` — valid QuickTaskRecord, small bounded change
- `.github/ai-workflow/artifacts/examples/quick-task-escalation.yaml` — triggers escalation (scope >3 files or risk flags set)

Rewrite:
- `.github/ai-workflow/schemas/quick-task.schema.json` — canonical name `QuickTaskRecord`, add `primary_surface`, `secondary_surfaces_allowed`, `escalation_triggered`, `escalation_reason`
- `.github/prompts/quick-task.prompt.md` — full rewrite: auto-escalates to `/grill` when any trigger fires (scope >3 files, risk indicators, uncertainty, >1 unknown), saves QuickTaskRecord to `.github/tasks/TASK-{NNN}/quick-task.yaml`

**Escalation triggers:**
- Files to touch > 3
- Change touches infra, auth, schema, or config
- Task description contains uncertainty language ("maybe", "not sure", "depends")
- >1 unknown decision point

**Acceptance criteria:**
- [ ] QuickTaskRecord schema uses canonical `artifact_type: QuickTaskRecord`
- [ ] Small bounded task completes without triggering grill
- [ ] Any escalation trigger causes explicit escalation to `/grill` with reason stated
- [ ] Valid example passes; escalation example triggers correct validator behavior

---

## Slice 8 — Schema cleanup
**Blocked by:** Slices 1–7

**What:** Remove legacy schema names, add surface metadata everywhere, update all command contracts to canonical names.

**Files:**

Delete:
- `.github/ai-workflow/schemas/brainstorm.schema.json` (if not already removed in Slice 2)
- `.github/ai-workflow/schemas/spec.schema.json` (if not already removed in Slice 3)

Update all command contracts (`.github/ai-workflow/contracts/commands/*.yaml`):
- Replace old artifact type names with canonical names: `GrillRecord`, `PlanArtifact`, `ExecutionRecord`, `VerificationRecord`, `ReviewRecord`, `QuickTaskRecord`
- Add `primary_surface` and `secondary_surfaces_allowed` to all artifact output declarations

Verify:
- No remaining references to `BrainstormArtifact`, `SpecArtifact`, or other pre-v1 names in any schema, contract, skill, or prompt

**Acceptance criteria:**
- [ ] `brainstorm.schema.json` and `spec.schema.json` deleted
- [ ] All command contracts reference canonical artifact type names
- [ ] All schemas include `primary_surface` and `secondary_surfaces_allowed` fields
- [ ] `grep -r "BrainstormArtifact\|SpecArtifact" .github/` returns no results

---

## Slice 9 — Validator test artifacts
**Blocked by:** Slice 8

**What:** Complete test artifact matrix. Every validator accept/reject path covered by a test YAML.

**Test matrix** (per testing decisions in spec):

| Artifact | Variant | Expected |
|---|---|---|
| GrillRecord | valid | pass |
| GrillRecord | missing required field | fail |
| GrillRecord | missing `approach` block | fail |
| PlanArtifact | valid | pass |
| PlanArtifact | scope violation | fail |
| PlanArtifact | `context_packet_required: true`, no path | fail |
| VerificationRecord | valid | pass |
| VerificationRecord | missing command output | fail |
| ReviewRecord | valid | pass |
| ReviewRecord | scope mismatch | fail |
| QuickTaskRecord | valid | pass |
| QuickTaskRecord | escalation trigger | escalation behavior |

**Files:**

Create (if not already created in per-slice work):
- All test artifact YAMLs listed in matrix at `.github/ai-workflow/artifacts/examples/`

Verify:
- Run `validate-artifact` against every example in the matrix, confirm expected pass/fail

**Acceptance criteria:**
- [ ] All example artifacts exist at `.github/ai-workflow/artifacts/examples/`
- [ ] Every valid artifact passes `validate-artifact`
- [ ] Every invalid artifact fails `validate-artifact` with a human-readable error message identifying the specific violation
- [ ] No test artifact references pre-v1 schema names

---

## Implementation order

```
1 → 2 → 3 → 4 → 5 → 6 → 8 → 9
              ↑
              7 (parallel from 2, independent of 4–6)
```

Start each slice in a fresh chat context. Save all artifacts to `.github/tasks/TASK-{NNN}/` for the implementation task itself.
