# Master Context — AI Workflow System

Paste this into a new chat session to give the AI full context about this repository's `.github` folder, how it works, how to use it, how to improve it, how to debug it, and how its evaluation system functions.

---

## What This System Is

This repository contains a **structured AI workflow system** living entirely inside `.github/`. It ships as a **Copilot/JetBrains-native workflow bundle** and turns a bounded AI assistant into an **auditable, self-evaluating agent** for software engineering tasks. Other LLM runtimes (e.g. Claude Code) may use the same governance files but require their own entrypoint setup. `CLAUDE.md` at the repo root provides the Claude Code entrypoint.

Without this system, an AI operates as a free-form assistant: no scope enforcement, no artifact trail, no human checkpoints, no way to know if the AI did what it said it would do.

With this system, every task the AI performs is:
- **Grilled** (requirements clarified before any code is written)
- **Planned** (scope locked, files declared, verification command defined)
- **Executed** (only within declared scope)
- **Verified** (real command evidence, not narrative claims)
- **Reviewed** (scope drift caught, human approval required)
- **Evaluated** (scored against declared success criteria, human-confirmed)

The system is implemented entirely in `.github/` as YAML schemas, JSON schemas, shell validators, markdown agents, and prompts. No external services. No CI required.

**Enforcement model (v1):** v1 is a *governed convention system with deterministic validators and human-enforced gates*. There is no hard runtime enforcement in v1. CLI wrappers, Git hooks, and CI gates are deferred to v2. Compliance depends on: validators running clean, human approval gates being honoured, and governed files not being edited outside the workflow.

---

## Full Architecture Map

```
.github/
├── copilot-instructions.md          ← loaded by Copilot as system prompt
├── instructions/
│   └── workflow.instructions.md     ← rules applied when editing .github/ files
├── prompts/                         ← /slash-command definitions (one per command)
│   ├── grill.prompt.md
│   ├── write-plan.prompt.md
│   ├── execute-plan.prompt.md
│   ├── verify.prompt.md
│   ├── review.prompt.md
│   └── evaluate.prompt.md           ← NEW: terminal evaluation command
├── agents/                          ← detailed agent instruction files
│   ├── grill.md
│   ├── write-plan.md
│   └── execute-plan.md
├── ai-workflow/
│   ├── manifest.yaml                ← machine-readable registry (source of truth)
│   ├── contracts/commands/          ← one contract per command (what it reads/writes)
│   │   ├── grill.v1.yaml
│   │   ├── write-plan.v1.yaml
│   │   ├── execute-plan.v1.yaml
│   │   ├── verify.v1.yaml
│   │   ├── review.v1.yaml
│   │   └── evaluate.v1.yaml
│   ├── schemas/                     ← JSON Schema for every artifact type
│   │   ├── grill.schema.json
│   │   ├── plan.schema.json
│   │   ├── execution-checkpoint.schema.json
│   │   ├── verification.schema.json
│   │   ├── review.schema.json
│   │   ├── task-manifest.schema.json
│   │   └── evaluation.schema.json
│   ├── policies/                    ← behavioral constraints per phase
│   │   ├── workflow-policy.v1.yaml
│   │   ├── verification-policy.v1.yaml
│   │   ├── review-policy.v1.yaml
│   │   ├── artifact-path-policy.v1.yaml
│   │   └── evaluation-policy.v1.yaml
│   ├── skills/                      ← skill definitions (authority + procedure)
│   │   ├── planning/SKILL.md
│   │   ├── execution/SKILL.md
│   │   ├── verification/SKILL.md
│   │   ├── review/SKILL.md
│   │   └── evaluation/SKILL.md
│   ├── protocols/                   ← decision protocols for edge cases
│   │   ├── verification-gate.md
│   │   ├── stage-review.md
│   │   ├── phase-checkpoint.md
│   │   └── retrieval-decision.md
│   ├── validators/                  ← shell scripts, exit 0=pass exit 1=fail
│   │   ├── bootstrap
│   │   ├── validate-manifest
│   │   ├── validate-artifact
│   │   ├── validate-artifact-path
│   │   ├── validate-plan-scope
│   │   ├── validate-review-gate
│   │   ├── validate-criteria-coverage
│   │   └── validate-evaluation-gate
│   └── artifacts/                   ← test fixtures and validator regression cases ONLY
│       └── examples/                ← not a runtime artifact location
├── CLAUDE.md                        ← Claude Code entrypoint (non-canonical for other runtimes)
├── tasks/                           ← per-task runtime artifact files (TASK-NNN/) — ONLY runtime artifact location
└── docs/
    ├── ARCHITECTURE.md
    ├── USAGE.md
    ├── INSTALL.md
    └── CHEAT-SHEET.md
```

---

## The Seven Layers Explained

### Layer 1 — Command Contracts (`contracts/commands/`)

Every slash command (`/grill`, `/write-plan`, etc.) has a contract YAML that declares:
- `input_artifacts` — what it must read before acting
- `output_artifacts` — what it must produce
- `authority` — what it may and may not do
- `required_validators` — which validators run before and after
- `semantics` — behavioral rules enforced at runtime

The contract is the **binding agreement** between the human and the AI. The AI cannot claim a command completed without producing the declared output artifact.

### Layer 2 — JSON Schemas (`schemas/`)

Every artifact the AI produces is validated against a JSON Schema. If the AI produces malformed output (missing fields, wrong types, violated constraints), the schema catches it.

Key enforcement points:
- `GrillRecord`: `success_criteria` are **structured objects** (`id`, `description`, `verification_type`, `verification_command`, `expected_signal`, `observable: true`) — free-text criteria are rejected by `grill.schema.v2`. `open_blockers` required when `decision: stop`; `task_type` always required; `triggered_by` required when `task_type: system_improvement`
- `VerificationRecord`: `criteria_outcomes[]` required (1:1 with GrillRecord `success_criteria`)
- `ReviewRecord` + `VerificationRecord`: structured `reason` required when human rejects
- All artifacts: `created_at` ISO 8601 required (enables temporal ordering)
- `EvaluationRecord`: `override_reason` required when `evaluation_status: overridden`; adds `criteria_count`, `criteria_met_count`, `criteria_unmet_count`, `outcome_band`

### Layer 3 — Protocols (`protocols/`)

Decision protocols for edge cases that cut across phases. Every protocol must be referenced by at least one prompt or skill. Protocols sit between governance and prompts/skills in the precedence chain:

`copilot-instructions.md` > governance > **protocols** > prompts > skills > docs > agents (non-canonical)

| Protocol | Purpose |
|----------|---------|
| `verification-gate.md` | When to block execution pending verification |
| `stage-review.md` | How to stage multi-phase reviews |
| `phase-checkpoint.md` | What to check before advancing phase |
| `retrieval-decision.md` | When bounded retrieval is required |

### Layer 4 — Policies (`policies/`)

Policies are behavioral constraints that govern what the AI is allowed to produce. Examples:
- `review-policy.v1.yaml`: AI cannot smooth over scope drift; must record violations; must require human authorization for PASS
- `verification-policy.v1.yaml`: evidence required; degraded status must be explicit
- `evaluation-policy.v1.yaml`: EvaluationRecord always starts as `draft`; human must confirm before authoritative; overrides require structured reason
- `artifact-path-policy.v1.yaml`: each artifact type has a declared storage directory; misplaced artifacts are rejected

### Layer 5 — Validators (`validators/`)

Shell scripts that run against artifacts. Exit 0 = valid. Exit 1 = violation. Validators are called by the AI during the workflow and can be run manually by developers.

| Validator | What it checks |
|-----------|---------------|
| `bootstrap` | System prerequisites met |
| `validate-manifest` | manifest.yaml is internally consistent AND filesystem consistent (every declared file exists; every governed file on disk is registered) |
| `validate-artifact` | Artifact conforms to declared schema |
| `validate-artifact-path` | Artifact is stored in its declared directory |
| `validate-plan-scope` | Execution stayed within plan file scope |
| `validate-review-gate` | Review has required human authorization |
| `validate-criteria-coverage` | criteria_outcomes count == success_criteria count across VerificationRecord + GrillRecord |
| `validate-evaluation-gate` | EvaluationRecord has valid status, confirmed_at when confirmed, override_reason when overridden |

Run all validators manually:
```bash
bash .github/ai-workflow/validators/bootstrap
bash .github/ai-workflow/validators/validate-manifest
bash .github/ai-workflow/validators/validate-artifact <path-to-artifact>
bash .github/ai-workflow/validators/validate-criteria-coverage <verification.json> <grill.json>
bash .github/ai-workflow/validators/validate-evaluation-gate <evaluation.json>
```

### Layer 6 — TaskManifest (lifecycle tracker)

Every task has one `TaskManifest` at `.github/tasks/TASK-{NNN}/task-manifest.json`. It is:
- **Created** at `/grill` time
- **Updated** at every phase transition (plan → execution → verification → review → evaluated)
- **Read first** by `/evaluate` to determine if a task is complete before scoring

`status` values: `in_progress | completed | blocked | abandoned`
`phase` values: `grill | plan | execution | verification | review | evaluated`

This solves the "incomplete chain" problem: evaluation never scores a task that was abandoned mid-workflow.

### Layer 7 — EvaluationRecord (scoring terminal)

The terminal artifact of every completed task. Produced by `/evaluate` (auto-triggered after a passing `/review`). Contains:

- `scores.criteria_satisfaction_rate` — (criteria met / total criteria), 0.0–1.0
- `scores.scope_adherence` — boolean from ReviewRecord.scope_match
- `scores.unplanned_files_count` — count of files touched outside plan scope
- `scores.verification_status` — from VerificationRecord
- `scores.review_status` — from ReviewRecord
- `scores.human_approval_first_pass` — was the review approved on first pass?
- `outcome_band` — `success | partial_success_high | partial_success_low | failure`
- `criteria_count` / `criteria_met_count` / `criteria_unmet_count` — raw counts for direct inspection
- `evaluation_status` — `draft | confirmed | overridden`

---

## Complete Workflow Walkthrough

```
Developer: /grill
  AI asks clarifying questions one at a time
  AI produces GrillRecord (task_type, success_criteria, approach, decision)
  AI creates TaskManifest (status: in_progress, phase: grill)

Developer: /write-plan
  AI reads GrillRecord
  AI locks scope: files_in_scope[], files_out_of_scope[]
  AI declares verification_command
  AI produces PlanArtifact
  AI updates TaskManifest (phase: plan)

Developer: /context-packet (conditionally mandatory)
  AI reads PlanArtifact
  If context_packet_required: true — this step is REQUIRED; /execute-plan preflight halts if context-packet.json is absent
  AI builds ContextPacketArtifact
  AI updates TaskManifest (phase: context_packet)

Developer: /execute-plan
  AI reads PlanArtifact
  AI edits ONLY declared files
  AI escalates if scope needs to expand
  AI produces ExecutionRecord (actual_changes, unplanned_files_touched)
  AI updates TaskManifest (phase: execution)

Developer: /verify
  AI runs verification_command exactly as declared
  AI maps each success_criterion to a criteria_outcomes entry (1:1)
  AI captures verbatim command output as evidence
  AI produces VerificationRecord
  AI updates TaskManifest (phase: verification)

Developer: /review
  AI diffs actual_changed_files against plan.files_in_scope
  Any file outside scope = scope_violation, status: FAIL
  If PASS/PASS_WITH_DEGRADATION: requests human authorization
  Human types "approved by <name>" or "rejected: <category> — <details>"
  AI produces ReviewRecord
  AI updates TaskManifest (phase: review, status: completed if PASS)
  AI automatically triggers /evaluate

/evaluate (auto)
  AI reads TaskManifest — skips if status != completed
  AI computes scores from all 5 upstream artifacts
  AI classifies outcome using declared outcome-band rules
  AI presents draft scoring block to human (NO write yet)
  Human: "confirm evaluation by <name>" or "override evaluation: <category> — <details>"
  AI writes TaskManifest ONCE: phase: evaluated, status: completed, evaluated_at, artifact_refs.evaluation
  AI writes EvaluationRecord ONCE: evaluation_status confirmed/overridden, outcome_band, criteria_count, criteria_met_count, criteria_unmet_count
  AI shows completion block: improvement_signal, unmet criteria IDs, suggested_next_action (pre-filled /grill invocation)
  (No automatic task creation — human decides whether to act on the signal)
```

---

## What It Means to Have This System

**For solo developers:**
- Every AI action is traceable. You can read any artifact file and understand exactly what the AI did, what it was allowed to do, and whether it stayed within bounds.
- Verification is real. The AI cannot claim "tests pass" without running the command and recording verbatim output.
- Evaluation gives you a score. After each task: did the AI actually achieve what was declared in the grill session?

**For teams:**
- Artifacts are the audit trail. Any team member can open `TASK-042/grill.json` and see the original intent, then `TASK-042/review.json` and see whether scope was respected.
- Human approval is recorded. Who approved what, when, and why rejection happened.
- Evaluation trends expose system-level problems before they become silent drift.

**For the AI:**
- The system constrains the AI's authority at every phase. The AI cannot edit source files during `/review`. It cannot self-approve its own evaluation. It cannot skip scope enforcement.
- The schema and validator chain gives the AI a self-check mechanism — it knows what a valid artifact looks like before producing one.

---

## Effective Usage Patterns

### Starting a task
Always start with `/grill`. Weak grills produce weak plans. A good grill:
- Declares `task_type` (feature / bugfix / system_improvement / exploration)
- Produces at least one measurable `success_criterion` (something that can be verified by a command or observable output)
- Identifies risks and rejects alternatives with rationale

### When to use `/quick-task`
For trivially small, known-scope changes (single-file typo fix, one-line config change). Quick tasks skip the full artifact chain. Use them sparingly — they produce no EvaluationRecord, no traceability.

### When scope changes during execution
Stop. Do not edit opportunistically. Go back to `/write-plan` and update the plan. `unplanned_files_touched` is a hard signal that something went wrong.

### When the AI produces a degraded artifact
`VERIFIED_WITH_DEGRADATION` or `PASS_WITH_DEGRADATION` means the task completed but with known compromises. These count as `partial_success` in evaluation. Document the degradation reason honestly — it becomes a signal for future improvement.

### When human rejects at review or verification
The rejection reason is now structured: `category + details`. This is the most valuable signal in the system. It feeds directly into evaluation and, over time, into system improvement tasks.

---

## How to Upgrade Without Breaking Existing Flow

### Version boundary rules

1. **Never modify an existing schema field** that is already `required`. Adding new required fields requires a new schema version (e.g., `grill.schema.v2`).
2. **New optional fields** can be added to existing schema versions without a version bump.
3. **Contracts are versioned** (`grill.v1.yaml`, `grill.v2.yaml`). Old tasks that reference `grill.v1` remain valid under v1. New tasks use v2.
4. **Manifest `validated_under`** in every artifact records which schema version was active at creation time. A v1 artifact validated against v1 schema will always pass — even after v2 ships.
5. **Never rename an artifact type constant** (e.g., `"GrillRecord"`). Renaming breaks existing artifact validation.

### Safe upgrade checklist
- [ ] New schema file created (e.g., `grill.schema.v2.json`)
- [ ] New contract file created (e.g., `grill.v2.yaml`)
- [ ] Old schema and contract files left in place (do not delete)
- [ ] Manifest updated to register new schema and contract
- [ ] New skill/prompt files created for v2 commands
- [ ] Old skill/prompt files left as-is for v1 tasks still in flight
- [ ] `CHANGELOG.md` updated
- [ ] Bootstrap + manifest validators pass after the change

### What NOT to do during upgrades
- Do not change `const` values in existing schemas (e.g., `"artifact_type": { "const": "GrillRecord" }`)
- Do not add required fields to existing schema without bumping version
- Do not remove validators — only deprecate them by documenting they are no longer called
- Do not change `command_contract_id` const values in contracts

---

## How to Identify Where the System Fails

### Signal 1 — EvaluationRecord outcome
After every task, read the EvaluationRecord at `.github/tasks/TASK-{NNN}/evaluation.json`.

| Outcome band | Rate condition | Meaning |
|---------|---------|---------|
| `success` | rate == 1.0 | All criteria met, scope clean, human approved first pass |
| `partial_success_high` | rate >= 0.8 | Most criteria met; minor degradation or first-pass revision |
| `partial_success_low` | rate >= 0.5 | Meaningful gaps; degraded states |
| `failure` | rate < 0.5, or review FAIL/BLOCKED, or human rejected | Task did not meet minimum bar |

### Signal 2 — Human rejection category
When a human rejects a VerificationRecord or ReviewRecord, the `reason.category` field identifies the root cause:

| Category | System failure point |
|----------|---------------------|
| `scope_violation` | Planning or execution skill — plan scope was too loose or AI drifted |
| `incorrect_implementation` | Execution or grill — approach was wrong or underdefined |
| `criteria_not_met` | Grill — criteria were untestable, or execution didn't address them |
| `verification_incomplete` | Verification skill — evidence was nominal, not real |
| `quality_issue` | Execution — output was technically correct but unacceptable quality |

### Signal 3 — TaskManifest status
A task stuck at `status: blocked` in TaskManifest means the workflow stopped mid-chain. Find the last `phase` recorded and read that phase's artifact to understand why it blocked.

### Signal 4 — Unplanned files
`ExecutionRecord.actual_changes.unplanned_files_touched` non-empty = the AI edited outside scope. This is a planning failure (scope too narrow) or an execution failure (AI drifted).

### Signal 5 — Criteria satisfaction rate trending down
If multiple tasks in a skill area show `criteria_satisfaction_rate` below 0.7, the grill criteria or the skill's procedure needs improvement.

---

## Developer Error Tracing Guide

### Tracing a failed task end-to-end

```bash
# 1. Find the TaskManifest — shows lifecycle state and all artifact paths
cat .github/tasks/TASK-{NNN}/task-manifest.json

# 2. Read the GrillRecord — what was the declared intent?
cat .github/tasks/TASK-{NNN}/grill.json
# Check: success_criteria, approach, decision, task_type

# 3. Read the PlanArtifact — what scope was declared?
cat .github/tasks/TASK-{NNN}/plan.json
# Check: files_in_scope, verification_command, steps[].risk_class

# 4. Read the ExecutionRecord — what actually happened?
cat .github/tasks/TASK-{NNN}/execution.json
# Check: actual_changes.unplanned_files_touched, decision.status, commands_run

# 5. Read the VerificationRecord — was verification real?
cat .github/tasks/TASK-{NNN}/verification.json
# Check: criteria_outcomes[].met, evidence[], command_output

# 6. Read the ReviewRecord — did scope drift? Did human approve?
cat .github/tasks/TASK-{NNN}/review.json
# Check: scope_violations, scope_match, human_authorization.status, human_authorization.reason

# 7. Read the EvaluationRecord — final score
cat .github/tasks/TASK-{NNN}/evaluation.json
# Check: outcome, scores.criteria_satisfaction_rate, human_evaluation.status
```

### Running validators manually against a specific artifact

```bash
# Validate any artifact against its schema
bash .github/ai-workflow/validators/validate-artifact \
  .github/tasks/TASK-{NNN}/verification.json

# Validate criteria coverage (cross-artifact)
bash .github/ai-workflow/validators/validate-criteria-coverage \
  .github/tasks/TASK-{NNN}/verification.json \
  .github/tasks/TASK-{NNN}/grill.json

# Validate evaluation artifact
bash .github/ai-workflow/validators/validate-evaluation-gate \
  .github/tasks/TASK-{NNN}/evaluation.json

# Validate artifact is in correct directory
bash .github/ai-workflow/validators/validate-artifact-path \
  .github/tasks/TASK-{NNN}/evaluation.json
```

### Common error patterns

| Symptom | Likely cause | Where to look |
|---------|-------------|---------------|
| AI edited a file not in plan | Execution drift | `ExecutionRecord.actual_changes.unplanned_files_touched` |
| Verification "passes" but criteria not met | Nominal evidence | `VerificationRecord.criteria_outcomes[].evidence` — is it real command output? |
| Review blocked despite clean scope | Missing required context packet | `PlanArtifact.context_packet_required` — was it satisfied? |
| EvaluationRecord stays draft | Human never confirmed | Check chat history — confirmation request may have been missed |
| Task stuck at `in_progress` | Workflow abandoned mid-phase | `TaskManifest.phase` shows last completed phase |
| Schema validation error on artifact | Missing required field | Read error message — field name + schema version shown |

---

## Evaluation System — Deep Dive

### What we evaluate

Every completed task is evaluated against its own declared success criteria from the GrillRecord. The system does not evaluate against external benchmarks or generic quality rubrics — it evaluates against what **you declared in the grill session**.

This means: the quality of evaluation is directly proportional to the quality of your success criteria. Vague criteria ("it should work") produce meaningless evaluation. Testable criteria ("running `npm test` returns 0 exit code and all 42 tests pass") produce meaningful evaluation.

### The three evaluation actors

| Actor | Role |
|-------|------|
| AI | Computes scores from artifacts, classifies outcome, writes draft |
| Human | Confirms or overrides — final authority, always |
| System | Enforces that draft → confirmed transition requires human action |

The AI cannot self-confirm. `evaluation_status: confirmed` requires `human_evaluation.confirmed_at` and `human_evaluation.reviewer`. If those are missing, `validate-evaluation-gate` fails.

### Metrics explained

**`criteria_satisfaction_rate`** (0.0–1.0)
The fraction of success criteria from the GrillRecord that were verifiably met. Computed from `VerificationRecord.criteria_outcomes`. A task with 4 criteria where 3 were met = 0.75.

**`scope_adherence`** (boolean)
Did execution stay within declared plan scope? Sourced from `ReviewRecord.scope_match`. False = scope drift occurred.

**`unplanned_files_count`** (integer)
How many files were touched outside plan scope? Zero is the target. Any non-zero value is a planning or execution failure.

**`verification_status`**
Was verification clean (`VERIFIED`), degraded (`VERIFIED_WITH_DEGRADATION`), or did it fail/block? Degraded means tests passed but with known compromises documented.

**`review_status`**
Was the final review clean (`PASS`), degraded (`PASS_WITH_DEGRADATION`), blocked, or failed?

**`human_approval_first_pass`**
Was the review approved on the first human pass, or did it require revision? `rejected` on first pass with subsequent approval counts as `partial_success`, not `success`.

### Outcome classification rules (applied in order)

```
outcome_band = success:
  criteria_satisfaction_rate == 1.0
  AND scope_adherence == true
  AND review_status in [PASS, PASS_WITH_DEGRADATION]
  AND human_approval_first_pass == approved

outcome_band = failure:
  criteria_satisfaction_rate < 0.5
  OR review_status in [FAIL, BLOCKED]
  OR human_approval_first_pass == rejected

outcome_band = partial_success_high:
  criteria_satisfaction_rate >= 0.8
  (and not already classified as success or failure)

outcome_band = partial_success_low:
  criteria_satisfaction_rate >= 0.5
  (and not already classified above)
```

`EvaluationRecord` also carries `criteria_count`, `criteria_met_count`, `criteria_unmet_count` for direct inspection.

### Human override

When the AI's evaluation is wrong — it scored `success` but the human knows the implementation was unacceptable — the human overrides with a structured reason:

```
override evaluation: incorrect_implementation — The auth refactor passes tests
but silently breaks the session invalidation path which has no test coverage.
```

The override is recorded with category + details. This is a high-value signal: it means the success criteria were insufficient to catch a real failure. The right follow-up is a `system_improvement` task that improves the grill criteria template.

---

## The Improvement Loop

The system improves itself through the same workflow it governs.

After `/evaluate` completes, the AI surfaces a **discoverable improvement signal** — not an automatic action:

```
/evaluate completion block (shown to human):
  improvement_signal: prompt_gap | skill_gap | criteria_gap | protocol_missing | none
  unmet_criteria_ids: [SC-003, SC-007]
  suggested_next_action: |
    /grill
    task_type: system_improvement
    triggered_by:
      source_type: evaluation_failure
      evaluation_refs: [.github/tasks/TASK-042/evaluation.json]
      failure_category: criteria_not_met
```

Human decides whether to act on it:

```
Human runs suggested /grill (or modifies it, or discards it)
        ↓
/write-plan → /execute-plan → /verify → /review → /evaluate
        ↓
Updated grill.md agent or grill.prompt.md — versioned, verified, evaluated
```

**Key constraint:** No automated writes to system files. No automatic task creation. Every improvement is a human-initiated task that runs through the full workflow. This prevents the AI from silently rewriting its own rules.

**Traceability:** The `triggered_by` field on the improvement GrillRecord links back to the EvaluationRecord(s) that caused it. Six months later, you can trace any system change back to the evidence that justified it.

---

## Questions This Context Enables You to Answer

- "What did the AI do in task TASK-042?" → Read TaskManifest + artifact chain
- "Why did task TASK-042 fail?" → Read EvaluationRecord + rejection reason
- "Is the AI drifting outside scope?" → Aggregate `unplanned_files_count` across tasks
- "Are success criteria being met?" → Aggregate `criteria_satisfaction_rate` over time
- "Why was this system file changed?" → Find the `system_improvement` task that changed it; read its `triggered_by` field
- "What changed between v1 and v2 of this workflow?" → Read `CHANGELOG.md` + git history on `.github/`
- "Is a task complete?" → Read TaskManifest `status` field
- "Did the human approve on first pass?" → Read `human_approval_first_pass` in EvaluationRecord
- "What metrics declined this month?" → Aggregate EvaluationRecords by `created_at` range
