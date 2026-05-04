# V1 Enforcement Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the 10 enforcement constraints identified in the architecture audit, closing every direct scope-bypass path in the v1 GitHub Copilot workflow system.

**Architecture:** New files live under `github/ai-workflow/` (policies, schemas, validators). Existing files (`refs/schema.md`, `scripts/validate-artifact.sh`, prompts, skills) are updated to reference and enforce the new contracts. No new runtime dependencies — everything is Markdown, YAML, and shell.

**Tech Stack:** YAML schemas, zsh shell validators, Markdown skill/prompt files

---

## File Map

**New files:**
- `github/ai-workflow/manifest.yaml` — bootstrap authority (discovery only)
- `github/ai-workflow/policies/quick-task.yaml` — quick-task thresholds and risky boundaries
- `github/ai-workflow/policies/planning-states.yaml` — degraded/blocked state rules
- `github/ai-workflow/policies/governance.yaml` — protected paths and governance-change rules
- `github/ai-workflow/policies/phase-prerequisites.yaml` — prerequisite table per command
- `github/ai-workflow/schemas/QuickTaskRecord.yaml` — schema definition
- `github/ai-workflow/schemas/EscalationSeed.yaml` — schema definition
- `github/ai-workflow/schemas/VerificationArtifact.yaml` — schema definition
- `github/ai-workflow/schemas/ReviewArtifact.yaml` — schema definition
- `github/ai-workflow/validators/preflight-quick-task.sh` — pre-write gate for quick-task
- `github/ai-workflow/validators/post-write-quick-task.sh` — post-write diff vs. allowed_files
- `github/ai-workflow/validators/phase-prerequisite.sh` — checks required input artifact exists
- `github/ai-workflow/validators/review-gate.sh` — enforces human_authorization and verification integrity

**Modified files:**
- `github/refs/schema.md` — add QuickTaskRecord, EscalationSeed, VerificationArtifact, ReviewArtifact; add `planning_state`, `validated_under`, `verification` fields
- `github/scripts/validate-artifact.sh` — add validated_under check to all artifact types
- `github/prompts/quick-task.prompt.md` — two-gate model with task_id
- `github/prompts/execute-plan.prompt.md` — mandatory artifact read from task path, no verbal additions
- `github/prompts/verify.prompt.md` — read verification.command from PlanArtifact
- `github/prompts/review.prompt.md` — require human_authorization
- `github/skills/planning/SKILL.md` — add verification field, validated_under, task_id storage path
- `github/skills/verification/SKILL.md` — read command from PlanArtifact; record execution not choice
- `github/skills/review/SKILL.md` — draft ReviewArtifact; require human_authorization for APPROVED

---

### Task 1: Directory structure + manifest

**Files:**
- Create: `github/ai-workflow/manifest.yaml`
- Create: `github/ai-workflow/policies/` (directory marker via `.gitkeep` or first file)
- Create: `github/ai-workflow/schemas/` (directory marker)
- Create: `github/ai-workflow/validators/` (directory marker)
- Create: `github/ai-workflow/artifacts/tasks/.gitkeep`

- [ ] **Step 1: Create manifest.yaml**

```yaml
# github/ai-workflow/manifest.yaml
schema: manifest/v1
version: "1.0.0"
description: "Single bootstrap authority for ai-workflow discovery. Owns discovery only — not policy."

policy_path: github/ai-workflow/policies
schema_path: github/ai-workflow/schemas
validator_path: github/ai-workflow/validators
artifact_path: github/ai-workflow/artifacts/tasks

schema_versions:
  QuickTaskRecord: "1.0.0"
  EscalationSeed: "1.0.0"
  VerificationArtifact: "1.0.0"
  ReviewArtifact: "1.0.0"
  PlanArtifact: "2.1.0"

validator_versions:
  preflight-quick-task: "1.0.0"
  post-write-quick-task: "1.0.0"
  phase-prerequisite: "1.0.0"
  review-gate: "1.0.0"

policy_versions:
  quick-task: "1.0.0"
  planning-states: "1.0.0"
  governance: "1.0.0"
  phase-prerequisites: "1.0.0"
```

- [ ] **Step 2: Create artifact task directory placeholder**

Create `github/ai-workflow/artifacts/tasks/.gitkeep` (empty file to track the directory).

- [ ] **Step 3: Verify manifest is valid YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('github/ai-workflow/manifest.yaml'))" && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add github/ai-workflow/manifest.yaml github/ai-workflow/artifacts/tasks/.gitkeep
git commit -m "feat: add ai-workflow manifest and artifact storage root"
```

---

### Task 2: Policy files

**Files:**
- Create: `github/ai-workflow/policies/quick-task.yaml`
- Create: `github/ai-workflow/policies/planning-states.yaml`
- Create: `github/ai-workflow/policies/governance.yaml`
- Create: `github/ai-workflow/policies/phase-prerequisites.yaml`

- [ ] **Step 1: Create quick-task policy**

```yaml
# github/ai-workflow/policies/quick-task.yaml
schema: policy/v1
policy: quick-task
version: "1.0.0"

max_files: 3
requires_pre_write_scope_lock: true

risky_boundaries:
  - auth
  - persistence
  - api_contract
  - config
  - security
  - migrations
  - database
  - secrets

on_scope_mismatch: escalate
on_risky_boundary_discovered: escalate
on_unlisted_file_needed: escalate

escalation_produces:
  - QuickTaskRecord (state: escalated)
  - EscalationSeed

post_escalation_allowed_diff:
  - QuickTaskRecord path
  - EscalationSeed path
```

- [ ] **Step 2: Create planning-states policy**

```yaml
# github/ai-workflow/policies/planning-states.yaml
schema: policy/v1
policy: planning-states
version: "1.0.0"

states:
  ready:
    description: "All prerequisites met. Full gate enforcement applies."
    relaxes_enforcement_gates: false
    requires_reason: false

  degraded:
    description: "Prerequisite artifact absent or incomplete. Explicit skip recorded."
    relaxes_enforcement_gates: false
    requires_reason: true
    requires_degradation_reason_fields:
      - type
      - evidence
    requires_reviewer_attention: true
    allowed_degradation_types:
      - missing_index
      - ambiguous_scope
      - partial_retrieval
      - brownfield_uncertainty

  blocked:
    description: "Hard prerequisite missing. Command must not proceed."
    relaxes_enforcement_gates: false
    requires_reason: false
    behavior: hard_fail
```

- [ ] **Step 3: Create governance policy**

```yaml
# github/ai-workflow/policies/governance.yaml
schema: policy/v1
policy: governance
version: "1.0.0"

protected_governance_paths:
  - github/ai-workflow/manifest.yaml
  - github/ai-workflow/policies/**
  - github/ai-workflow/schemas/**
  - github/ai-workflow/validators/**
  - github/ai-workflow/commands/**
  - github/scripts/validate-artifact.sh

agent_modification_rule:
  description: "Agents may not modify governance paths during normal task execution."
  violation: hard_fail

governance_change_rules:
  label_required: governance-change
  requires_explicit_human_review: true
  requires_migration_note: true
  cannot_pass_normal_review_gate: true

upgrade_rules:
  new_governance_applies_to: new_artifacts_only
  in_flight_protection: revalidate_under_recorded_version
  migration_state: BLOCKED_FOR_MIGRATION
```

- [ ] **Step 4: Create phase-prerequisites policy**

```yaml
# github/ai-workflow/policies/phase-prerequisites.yaml
schema: policy/v1
policy: phase-prerequisites
version: "1.0.0"

# Rule: no command may proceed from chat context alone.
# Early discovery phases may be explicitly skipped (degraded).
# Execution and later phases may never be skipped.

commands:
  /quick-task:
    required_input: none
    absence_behavior: proceed
    notes: "Self-contained — creates QuickTaskRecord as first action"

  /brainstorm:
    required_input: none
    absence_behavior: proceed
    notes: "Entry point — no predecessor artifact required"

  /write-spec:
    required_input: BrainstormArtifact
    absence_behavior: degraded
    skip_allowed: true
    skip_reason_required: true

  /write-plan:
    required_input: SpecArtifact
    absence_behavior: degraded
    skip_allowed: true
    skip_reason_required: true

  /execute-plan:
    required_input: PlanArtifact
    absence_behavior: blocked
    skip_allowed: false

  /verify:
    required_input: PlanArtifact
    absence_behavior: blocked
    skip_allowed: false
    also_requires: execution_complete_marker

  /review:
    required_input: VerificationArtifact
    absence_behavior: blocked
    skip_allowed: false

skip_reason_schema:
  skipped_artifact: string  # artifact type that was skipped
  reason: string
  risk_acknowledged: true
```

- [ ] **Step 5: Verify all policy files are valid YAML**

```bash
for f in github/ai-workflow/policies/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add github/ai-workflow/policies/
git commit -m "feat: add v1 policy files (quick-task, planning-states, governance, phase-prerequisites)"
```

---

### Task 3: Artifact schemas

**Files:**
- Create: `github/ai-workflow/schemas/QuickTaskRecord.yaml`
- Create: `github/ai-workflow/schemas/EscalationSeed.yaml`
- Create: `github/ai-workflow/schemas/VerificationArtifact.yaml`
- Create: `github/ai-workflow/schemas/ReviewArtifact.yaml`

- [ ] **Step 1: Create QuickTaskRecord schema**

```yaml
# github/ai-workflow/schemas/QuickTaskRecord.yaml
schema: QuickTaskRecord/v1
version: "1.0.0"

required_fields:
  - task_id          # string — matches artifacts/tasks/<task_id>/
  - classification   # string — description of task type
  - allowed_files    # list[string] — declared scope before first write
  - risky_boundary_check:
      performed: boolean
      result: clean | risky
      signals: list[string]
  - verification_command  # string — how to locally verify the change
  - state            # locked | escalated | complete

validated_under:
  manifest_version: string
  policy_version: string
  schema_version: string
  validator_version: string
  validated_at: timestamp

state_transitions:
  locked:
    description: "Pre-write gate passed. Agent may edit declared files only."
    next: escalated | complete
  escalated:
    description: "Scope or boundary violation detected. Execution stopped."
    next: terminal
    allowed_diff: [QuickTaskRecord path, EscalationSeed path]
  complete:
    description: "Post-write gate passed. Diff matched allowed_files."
    next: terminal
```

- [ ] **Step 2: Create EscalationSeed schema**

```yaml
# github/ai-workflow/schemas/EscalationSeed.yaml
schema: EscalationSeed/v1
version: "1.0.0"

required_fields:
  - schema_version     # "EscalationSeed/v1"
  - task_id            # string
  - source_command     # "/quick-task"
  - source_record      # path to QuickTaskRecord
  - reason:
      type: risky_boundary | scope_expansion | uncertainty | verification_not_local
      description: string
  - summary            # string — human-readable explanation
  - attempted_scope:
      files: list[string]
  - discovered_scope:
      files: list[string]
  - risk_signals       # list[string]
  - recommended_next_command  # "/brainstorm"
  - suggested_prompt   # string — seed for /brainstorm

validated_under:
  manifest_version: string
  policy_version: string
  schema_version: string
  validated_at: timestamp
```

- [ ] **Step 3: Create VerificationArtifact schema**

```yaml
# github/ai-workflow/schemas/VerificationArtifact.yaml
schema: VerificationArtifact/v1
version: "1.0.0"

required_fields:
  - schema_version       # "VerificationArtifact/v1"
  - task_id              # string
  - source_plan          # path — e.g. artifacts/tasks/TASK-123/plan.yaml with @rev annotation
  - command_run          # string — MUST exactly match PlanArtifact.verification.command
  - exit_code            # integer
  - output_excerpt       # string — pasted terminal output (not a summary)
  - result               # PASS | FAIL

validation_rule:
  command_run_must_match: PlanArtifact.verification.command
  mismatch_behavior: FAIL
  result_must_be_from_execution: true  # agent may not self-declare result

validated_under:
  manifest_version: string
  policy_version: string
  schema_version: string
  validator_version: string
  validated_at: timestamp
```

- [ ] **Step 4: Create ReviewArtifact schema**

```yaml
# github/ai-workflow/schemas/ReviewArtifact.yaml
schema: ReviewArtifact/v1
version: "1.0.0"

required_fields:
  - schema_version         # "ReviewArtifact/v1"
  - task_id                # string
  - source_verification    # path to VerificationArtifact
  - agent_review:
      result: PASS | FAIL
      findings: list[string]   # BLOCKER/SUGGESTION items
  - human_authorization:
      status: approved | rejected | pending
      reviewer: string         # required when status != pending
      reviewed_at: timestamp   # required when status != pending
      comment: string
  - final_result           # APPROVED | REJECTED | PENDING

validation_rules:
  final_result_approved_requires: human_authorization.status == approved
  agent_only_artifact_blocks_review_gate: true

validated_under:
  manifest_version: string
  policy_version: string
  schema_version: string
  validator_version: string
  validated_at: timestamp
```

- [ ] **Step 5: Verify all schema files are valid YAML**

```bash
for f in github/ai-workflow/schemas/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "PASS: $f" || echo "FAIL: $f"
done
```
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add github/ai-workflow/schemas/
git commit -m "feat: add artifact schemas (QuickTaskRecord, EscalationSeed, VerificationArtifact, ReviewArtifact)"
```

---

### Task 4: Update refs/schema.md

**Files:**
- Modify: `github/refs/schema.md`

- [ ] **Step 1: Add validated_under to schema.md**

After the `Amendment` interface, add a new section:

```typescript
## Governance Binding

interface ValidatedUnder {
  manifest_version: string;  // from manifest.yaml
  policy_version: string;    // policy file version used at validation time
  schema_version: string;    // artifact schema version
  validator_version: string;
  validated_at: string;      // ISO 8601 timestamp
}
```

- [ ] **Step 2: Add planning_state to ProblemRecord or BrainstormArtifact section**

Add a new section for planning state:

```typescript
## Planning State

type PlanningStateType = 'ready' | 'degraded' | 'blocked';

interface DegradationReason {
  type: 'missing_index' | 'ambiguous_scope' | 'partial_retrieval' | 'brownfield_uncertainty';
  evidence: string;
}

interface PlanningState {
  state: PlanningStateType;
  degradation_reason?: DegradationReason;  // required when state == 'degraded'
  impact?: string;
  blocked_items?: string[];
  required_reviewer_attention?: string[];
}
```

Note: planning_state is owned by BrainstormArtifact. State 'degraded' requires degradation_reason. State 'degraded' relaxes no enforcement gates — it is a confidence/audit signal only.

- [ ] **Step 3: Add verification field to PlanArtifact section**

In the existing PlanArtifact description, document the new required field:

```typescript
## Verification Contract

interface VerificationContract {
  command: string;          // exact command to run — declared at planning time
  expected_signal: string;  // e.g. "exit_code_0"
}

// Added to PlanArtifact.execution:
// verification: VerificationContract
```

Rule: verification.command is set by the planner and is immutable after PlanArtifact is locked. /verify executes this command and records output — it does not choose the proof.

- [ ] **Step 4: Add artifact storage model section**

```markdown
## Artifact Storage Model

Artifacts are stored at deterministic paths keyed by task_id:

```
.github/ai-workflow/artifacts/tasks/
  <task_id>/
    brainstorm.yaml
    spec.yaml
    plan.yaml
    quick-task.yaml
    escalation-seed.yaml
    verification.yaml
    review.yaml
```

Rules:
- Every phase command requires explicit task_id as argument.
- Phase commands read from the declared path only — no search, no heuristics.
- Missing artifact at expected path = BLOCKED (not degraded, not search-and-guess).
- Multiple artifacts claiming the same task_id = BLOCKED.
```

- [ ] **Step 5: Update schema definition version**

Change the frontmatter from `schema_definition: "v2.1"` to `schema_definition: "v2.2"` and add a changelog entry.

- [ ] **Step 6: Verify schema.md is still valid markdown**

```bash
python3 -c "
content = open('github/refs/schema.md').read()
assert 'ValidatedUnder' in content
assert 'PlanningState' in content
assert 'VerificationContract' in content
assert 'Artifact Storage Model' in content
assert 'v2.2' in content
print('PASS')
"
```
Expected: `PASS`

- [ ] **Step 7: Commit**

```bash
git add github/refs/schema.md
git commit -m "feat: extend schema.md v2.2 — add validated_under, planning_state, verification contract, storage model"
```

---

### Task 5: Shell validators

**Files:**
- Create: `github/ai-workflow/validators/preflight-quick-task.sh`
- Create: `github/ai-workflow/validators/post-write-quick-task.sh`
- Create: `github/ai-workflow/validators/phase-prerequisite.sh`
- Create: `github/ai-workflow/validators/review-gate.sh`

- [ ] **Step 1: Create preflight-quick-task.sh**

```bash
#!/usr/bin/env zsh
# preflight-quick-task.sh <quick-task-record-path>
# Pre-write gate: validates QuickTaskRecord before first file edit.
# EXIT 0 = pass (agent may proceed). EXIT 1 = fail (agent must not write files).

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: preflight-quick-task.sh <quick-task-record-path>"
  exit 1
fi

record=$1
typeset -a failures

add_fail() { failures+=("$1") }

[[ -f "$record" ]] || { echo "FAIL: record not found: $record"; exit 1; }

# Required fields
rg -q 'task_id:' "$record"       || add_fail "QuickTaskRecord.task_id — missing"
rg -q 'classification:' "$record" || add_fail "QuickTaskRecord.classification — missing"
rg -q 'allowed_files:' "$record"  || add_fail "QuickTaskRecord.allowed_files — missing"
rg -q 'verification_command:' "$record" || add_fail "QuickTaskRecord.verification_command — missing"
rg -q 'risky_boundary_check:' "$record" || add_fail "QuickTaskRecord.risky_boundary_check — missing"

# State must be 'locked'
rg -q 'state:[[:space:]]*locked' "$record" || add_fail "QuickTaskRecord.state — must be 'locked' before first write"

# validated_under must be present
rg -q 'validated_under:' "$record" || add_fail "QuickTaskRecord.validated_under — missing"

# risky_boundary_check result must be 'clean'
rg -q 'result:[[:space:]]*clean' "$record" || add_fail "QuickTaskRecord.risky_boundary_check.result — must be 'clean' to proceed (use escalate for risky)"

# allowed_files must not be empty
if rg -q 'allowed_files:[[:space:]]*\[\]' "$record"; then
  add_fail "QuickTaskRecord.allowed_files — must declare at least one file"
fi

# Max files check — read count from allowed_files list
file_count=$(rg -o '^\s+-\s+\S+' "$record" | wc -l | tr -d ' ')
if (( file_count > 3 )); then
  add_fail "QuickTaskRecord.allowed_files — exceeds max_files: 3 (policy: quick-task.yaml)"
fi

if (( ${#failures[@]} > 0 )); then
  for f in "${failures[@]}"; do echo "FAIL: $f"; done
  exit 1
fi

echo "PASS: QuickTaskRecord pre-write gate cleared"
```

- [ ] **Step 2: Create post-write-quick-task.sh**

```bash
#!/usr/bin/env zsh
# post-write-quick-task.sh <quick-task-record-path>
# Post-write gate: validates actual git diff against declared allowed_files.
# EXIT 0 = pass. EXIT 1 = fail (scope violation).

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: post-write-quick-task.sh <quick-task-record-path>"
  exit 1
fi

record=$1
typeset -a failures

[[ -f "$record" ]] || { echo "FAIL: record not found: $record"; exit 1; }

# Get declared allowed_files from record (lines starting with "  - ")
allowed_files=(${(@f)$(rg -A100 'allowed_files:' "$record" | rg '^\s+-\s+(.+)' -o --replace '$1' || true)})

# Get actual changed files from git diff (unstaged + staged, exclude the record itself)
record_basename=$(basename "$record")
changed_files=(${(@f)$(git diff --name-only HEAD 2>/dev/null || git diff --name-only 2>/dev/null || true)})

# Check each changed file is in allowed_files (or is the record/seed itself)
for cf in $changed_files; do
  cf_base=$(basename "$cf")
  # Allow QuickTaskRecord and EscalationSeed to be written
  if [[ "$cf_base" == "quick-task.yaml" || "$cf_base" == "escalation-seed.yaml" ]]; then
    continue
  fi
  # Check if file is in allowed list (basename or full path match)
  found=false
  for af in $allowed_files; do
    if [[ "$cf" == "$af" || "$(basename $cf)" == "$(basename $af)" ]]; then
      found=true
      break
    fi
  done
  if [[ "$found" == "false" ]]; then
    add_fail "scope violation — $cf not in QuickTaskRecord.allowed_files"
  fi
done

if (( ${#failures[@]} > 0 )); then
  for f in "${failures[@]}"; do echo "FAIL: $f"; done
  echo "ACTION: update QuickTaskRecord.state to 'escalated' and write EscalationSeed"
  exit 1
fi

echo "PASS: diff matches declared scope"
```

- [ ] **Step 3: Create phase-prerequisite.sh**

```bash
#!/usr/bin/env zsh
# phase-prerequisite.sh <command> <task_id>
# Checks that the required input artifact exists for a phase command.
# EXIT 0 = present (proceed). EXIT 1 = absent (blocked or degraded).

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: phase-prerequisite.sh <command> <task_id>"
  exit 1
fi

command_name=$1
task_id=$2
artifacts_base="$(git rev-parse --show-toplevel)/.github/ai-workflow/artifacts/tasks"
task_dir="$artifacts_base/$task_id"

check_artifact() {
  local name=$1
  local path="$task_dir/$name"
  if [[ ! -f "$path" ]]; then
    echo "BLOCKED: required artifact missing — $path"
    echo "Command '$command_name' requires $name for task $task_id"
    exit 1
  fi
  echo "FOUND: $path"
}

case "$command_name" in
  "/quick-task")
    echo "PASS: /quick-task has no predecessor artifact requirement"
    ;;
  "/brainstorm")
    echo "PASS: /brainstorm is an entry point — no predecessor artifact required"
    ;;
  "/write-spec")
    if [[ ! -f "$task_dir/brainstorm.yaml" ]]; then
      echo "DEGRADED: BrainstormArtifact missing for task $task_id"
      echo "Allowed to proceed if skip_reason is recorded in spec.yaml"
      exit 2  # exit 2 = degraded (allowed with skip_reason)
    fi
    echo "PASS: brainstorm.yaml found"
    ;;
  "/write-plan")
    if [[ ! -f "$task_dir/spec.yaml" ]]; then
      echo "DEGRADED: SpecArtifact missing for task $task_id"
      echo "Allowed to proceed if skip_reason is recorded in plan.yaml"
      exit 2
    fi
    echo "PASS: spec.yaml found"
    ;;
  "/execute-plan")
    check_artifact "plan.yaml"
    ;;
  "/verify")
    check_artifact "plan.yaml"
    # Check execution marker (amendments with step-completed entries)
    if ! rg -q 'type:[[:space:]]*step-completed' "$task_dir/plan.yaml" 2>/dev/null; then
      echo "BLOCKED: no step-completed amendments found in plan.yaml — execution may not be complete"
      exit 1
    fi
    echo "PASS: plan.yaml found and execution marker present"
    ;;
  "/review")
    check_artifact "verification.yaml"
    ;;
  *)
    echo "UNKNOWN: command '$command_name' not in prerequisite table — proceeding"
    ;;
esac
```

- [ ] **Step 4: Create review-gate.sh**

```bash
#!/usr/bin/env zsh
# review-gate.sh <review-artifact-path> <verification-artifact-path> <plan-artifact-path>
# Enforces: human_authorization required, verification command integrity.
# EXIT 0 = pass. EXIT 1 = fail (gate blocked).

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: review-gate.sh <review-artifact> <verification-artifact> <plan-artifact>"
  exit 1
fi

review=$1
verification=$2
plan=$3
typeset -a failures

add_fail() { failures+=("$1") }

for f in "$review" "$verification" "$plan"; do
  [[ -f "$f" ]] || { echo "FAIL: artifact not found: $f"; exit 1; }
done

# Rule 1: final_result APPROVED requires human_authorization.status == approved
final_result=$(rg -o 'final_result:[[:space:]]*\K\S+' "$review" | head -1 || true)
human_status=$(rg -o 'status:[[:space:]]*\K(approved|rejected|pending)' "$review" | head -1 || true)

if [[ "$final_result" == "APPROVED" && "$human_status" != "approved" ]]; then
  add_fail "ReviewArtifact.final_result is APPROVED but human_authorization.status is not 'approved' — agent cannot self-approve"
fi

# Rule 2: reviewer field required when not pending
if [[ "$human_status" != "pending" ]]; then
  rg -q 'reviewer:[[:space:]]*\S' "$review" || add_fail "ReviewArtifact.human_authorization.reviewer — required when status is $human_status"
  rg -q 'reviewed_at:[[:space:]]*\S' "$review" || add_fail "ReviewArtifact.human_authorization.reviewed_at — required when status is $human_status"
fi

# Rule 3: VerificationArtifact.command_run must match PlanArtifact.verification.command
plan_cmd=$(rg -o 'command:[[:space:]]*\K.+' "$plan" | head -1 | tr -d '"' | sed 's/^[[:space:]]*//' || true)
verify_cmd=$(rg -o 'command_run:[[:space:]]*\K.+' "$verification" | head -1 | tr -d '"' | sed 's/^[[:space:]]*//' || true)

if [[ -n "$plan_cmd" && -n "$verify_cmd" && "$plan_cmd" != "$verify_cmd" ]]; then
  add_fail "VerificationArtifact.command_run ('$verify_cmd') does not match PlanArtifact.verification.command ('$plan_cmd')"
fi

# Rule 4: governance-change detection — check if any governance path was modified
governed_patterns=(
  "\.github/ai-workflow/manifest"
  "\.github/ai-workflow/policies/"
  "\.github/ai-workflow/schemas/"
  "\.github/ai-workflow/validators/"
  "github/scripts/validate-artifact"
)
changed=$(git diff --name-only HEAD 2>/dev/null || true)
for pattern in $governed_patterns; do
  if echo "$changed" | rg -q "$pattern"; then
    add_fail "governance path modified — change must be labeled 'governance-change' and cannot pass normal review gate"
  fi
done

if (( ${#failures[@]} > 0 )); then
  for f in "${failures[@]}"; do echo "FAIL: $f"; done
  exit 1
fi

echo "PASS: review gate cleared"
```

- [ ] **Step 5: Make validators executable**

```bash
chmod +x github/ai-workflow/validators/*.sh
ls -la github/ai-workflow/validators/
```
Expected: all four `.sh` files with `x` bit set.

- [ ] **Step 6: Smoke-test preflight validator rejects missing state field**

```bash
# Create a minimal invalid record missing the state field
cat > /tmp/test-quick-task-invalid.yaml << 'EOF'
task_id: TEST-001
classification: "bug-fix"
allowed_files:
  - src/utils.ts
verification_command: "npm test"
risky_boundary_check:
  performed: true
  result: clean
  signals: []
validated_under:
  manifest_version: "1.0.0"
  policy_version: "1.0.0"
  schema_version: "1.0.0"
  validator_version: "1.0.0"
  validated_at: "2026-05-02T00:00:00Z"
EOF
zsh github/ai-workflow/validators/preflight-quick-task.sh /tmp/test-quick-task-invalid.yaml
```
Expected: `FAIL: QuickTaskRecord.state — must be 'locked' before first write`

- [ ] **Step 7: Smoke-test preflight validator passes valid record**

```bash
cat > /tmp/test-quick-task-valid.yaml << 'EOF'
task_id: TEST-001
classification: "bug-fix"
allowed_files:
  - src/utils.ts
verification_command: "npm test"
risky_boundary_check:
  performed: true
  result: clean
  signals: []
state: locked
validated_under:
  manifest_version: "1.0.0"
  policy_version: "1.0.0"
  schema_version: "1.0.0"
  validator_version: "1.0.0"
  validated_at: "2026-05-02T00:00:00Z"
EOF
zsh github/ai-workflow/validators/preflight-quick-task.sh /tmp/test-quick-task-valid.yaml
```
Expected: `PASS: QuickTaskRecord pre-write gate cleared`

- [ ] **Step 8: Commit**

```bash
git add github/ai-workflow/validators/
git commit -m "feat: add shell validators (preflight-quick-task, post-write-quick-task, phase-prerequisite, review-gate)"
```

---

### Task 6: Update quick-task command and planning skill

**Files:**
- Modify: `github/prompts/quick-task.prompt.md`
- Modify: `github/skills/planning/SKILL.md`

- [ ] **Step 1: Rewrite quick-task.prompt.md**

Replace the entire file content with:

```markdown
---
agent: agent
description: Direct-to-plan bypass for bugfixes, config changes, and simple tasks — gated by pre-write scope lock
---

> **Phase: Plan (Quick Task)** | Skill: planning | Requires: task_id argument

You are in **quick-task phase**. Before touching any file, you must pass the pre-write gate.

**Usage:** `/quick-task <task_id>`

---

## Two-Gate Model

### Gate 1 — Pre-write (run BEFORE any file edit)

1. Read `.github/ai-workflow/policies/quick-task.yaml`.
2. Classify the task: file count, risky boundary check against `risky_boundaries` list.
3. Write `.github/ai-workflow/artifacts/tasks/<task_id>/quick-task.yaml` with:
   - `task_id`, `classification`, `allowed_files`, `risky_boundary_check`, `verification_command`
   - `state: locked`
   - `validated_under` (read versions from manifest.yaml)
4. Run the preflight validator:

```bash
zsh .github/ai-workflow/validators/preflight-quick-task.sh \
  .github/ai-workflow/artifacts/tasks/<task_id>/quick-task.yaml
```

**If FAIL:** Do not edit any files. Fix the QuickTaskRecord or escalate.
**If PASS:** Proceed to edit only the files in `allowed_files`.

---

### Mid-execution rule

If you discover during execution that you need to touch an unlisted file or a risky boundary:
- **STOP immediately.** Do not continue.
- Update QuickTaskRecord state to `escalated`.
- Write EscalationSeed to `.github/ai-workflow/artifacts/tasks/<task_id>/escalation-seed.yaml`.
- Do not write any other files.

---

### Gate 2 — Post-write (run AFTER edits, before claiming done)

```bash
zsh .github/ai-workflow/validators/post-write-quick-task.sh \
  .github/ai-workflow/artifacts/tasks/<task_id>/quick-task.yaml
```

**If FAIL:** Scope violation detected. Update state to `escalated`, write EscalationSeed, stop.
**If PASS:** Update QuickTaskRecord `state` to `complete`. Task is done.

---

## Escalation handoff

If escalated, inform the engineer:
> "Quick task escalated. EscalationSeed written to `artifacts/tasks/<task_id>/escalation-seed.yaml`.
> Run `/brainstorm <task_id>` to continue with full workflow."

**No verbal scope additions.** Only the `allowed_files` in the locked QuickTaskRecord is executable scope.
```

- [ ] **Step 2: Update planning/SKILL.md to add verification field**

Add a new section after `## Output Artifact`:

```markdown
## Verification Contract (required)

Every PlanArtifact must include a `verification` field under `execution`:

```yaml
execution:
  verification:
    command: "<exact runnable command>"
    expected_signal: "exit_code_0"
```

Rules:
- The command is declared at planning time, not at verification time.
- It must be runnable locally without side effects.
- It must be specific enough to prove plan requirements are met.
- `/verify` will execute this exact command — it may not substitute a different one.
- If the command must change after the plan is locked, create a PlanArtifact revision first.
```

Also add a `## Task Identity` section:

```markdown
## Task Identity

Every plan is written for an explicit task_id:

```bash
/write-plan <task_id>
```

Output artifact path:
```
.github/ai-workflow/artifacts/tasks/<task_id>/plan.yaml
```

The planner reads the SpecArtifact from:
```
.github/ai-workflow/artifacts/tasks/<task_id>/spec.yaml
```

If spec.yaml is absent, record `skip_reason` in the plan header and set `planning_state: degraded`.
```

- [ ] **Step 3: Verify both files are valid markdown**

```bash
python3 -c "
import os
for f in ['github/prompts/quick-task.prompt.md', 'github/skills/planning/SKILL.md']:
    assert os.path.exists(f), f'missing: {f}'
    content = open(f).read()
    assert len(content) > 100, f'suspiciously short: {f}'
print('PASS')
"
```
Expected: `PASS`

- [ ] **Step 4: Commit**

```bash
git add github/prompts/quick-task.prompt.md github/skills/planning/SKILL.md
git commit -m "feat: add two-gate model to quick-task prompt and verification contract to planning skill"
```

---

### Task 7: Update execute-plan, verify, and review commands

**Files:**
- Modify: `github/prompts/execute-plan.prompt.md`
- Modify: `github/prompts/verify.prompt.md`
- Modify: `github/prompts/review.prompt.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/review/SKILL.md`

- [ ] **Step 1: Update execute-plan.prompt.md**

Read the current file, then add the mandatory artifact read rule and task_id requirement at the top:

```markdown
---
agent: agent
description: Execute a locked plan artifact — reads PlanArtifact from task path, no verbal additions
---

> **Phase: Execute** | Skill: execution | Requires: task_id argument

**Usage:** `/execute-plan <task_id>`

## Mandatory pre-execution checks

1. Run phase-prerequisite check:

```bash
zsh .github/ai-workflow/validators/phase-prerequisite.sh /execute-plan <task_id>
```

If BLOCKED: do not proceed. Artifact is missing.

2. Read PlanArtifact from disk:
```
.github/ai-workflow/artifacts/tasks/<task_id>/plan.yaml
```

**This is the only authoritative source.** Chat history, in-context plans, and verbal additions are non-authoritative. If the engineer says "also do X" and X is not in plan.yaml: stop and ask them to create a plan revision first.

3. Read and follow `.github/skills/execution/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.
```

- [ ] **Step 2: Update verify.prompt.md**

```markdown
---
agent: agent
description: Prove every plan requirement is met — reads verification command from PlanArtifact, records execution output
---

> **Phase: Verify** | Skill: verification | Requires: task_id argument

**Usage:** `/verify <task_id>`

## Mandatory pre-verification checks

1. Run phase-prerequisite check:

```bash
zsh .github/ai-workflow/validators/phase-prerequisite.sh /verify <task_id>
```

If BLOCKED: do not proceed.

2. Read `.github/ai-workflow/artifacts/tasks/<task_id>/plan.yaml`.
3. Extract `execution.verification.command` from the plan.
4. Read and follow `.github/skills/verification/SKILL.md`.

**The verification command comes from the plan — you do not choose it.**
```

- [ ] **Step 3: Update review.prompt.md**

```markdown
---
agent: agent
description: Critical review before merge — drafts ReviewArtifact, requires human authorization for APPROVED
---

> **Phase: Review** | Skill: review | Requires: task_id argument

**Usage:** `/review <task_id>`

## Mandatory pre-review checks

1. Run phase-prerequisite check:

```bash
zsh .github/ai-workflow/validators/phase-prerequisite.sh /review <task_id>
```

If BLOCKED: VerificationArtifact is missing — do not proceed.

2. Read artifacts:
   - `.github/ai-workflow/artifacts/tasks/<task_id>/verification.yaml`
   - `.github/ai-workflow/artifacts/tasks/<task_id>/plan.yaml`

3. Read and follow `.github/skills/review/SKILL.md`.
Also read `.github/skills/conventions/SKILL.md` for repo context.

**The agent drafts ReviewArtifact. The agent may not set final_result: APPROVED.**
Human authorization is required.
```

- [ ] **Step 4: Update verification/SKILL.md — read command from plan, record execution**

Add to the `## Before Generating Anything` section:

```markdown
## Mandatory: Read verification command from plan

Before running any tests:

1. Read `.github/ai-workflow/artifacts/tasks/<task_id>/plan.yaml`.
2. Extract `execution.verification.command`.
3. This is the command you will run — you may not substitute a different command.
4. If the command is absent from the plan: BLOCKED. Ask the engineer to add it via plan revision.

## VerificationArtifact output

After running the command, write `.github/ai-workflow/artifacts/tasks/<task_id>/verification.yaml`:

```yaml
schema_version: "VerificationArtifact/v1"
task_id: <task_id>
source_plan: "artifacts/tasks/<task_id>/plan.yaml"
command_run: "<exact command from plan>"
exit_code: <integer>
output_excerpt: |
  <pasted terminal output>
result: PASS | FAIL
validated_under:
  manifest_version: "<from manifest.yaml>"
  policy_version: "1.0.0"
  schema_version: "1.0.0"
  validator_version: "1.0.0"
  validated_at: "<ISO 8601>"
```

Rule: `command_run` must exactly match `plan.execution.verification.command`. If you change the command for any reason, update the plan artifact first via revision.
```

- [ ] **Step 5: Update review/SKILL.md — add ReviewArtifact with human_authorization**

Add to the end of review/SKILL.md:

```markdown
## ReviewArtifact output

After completing review findings, write `.github/ai-workflow/artifacts/tasks/<task_id>/review.yaml`:

```yaml
schema_version: "ReviewArtifact/v1"
task_id: <task_id>
source_verification: "artifacts/tasks/<task_id>/verification.yaml"
agent_review:
  result: PASS | FAIL
  findings:
    - "BLOCKER: [file:line] [description]"
    - "SUGGESTION: [file:line] [description]"
human_authorization:
  status: pending
  reviewer: ""
  reviewed_at: ""
  comment: ""
final_result: PENDING
validated_under:
  manifest_version: "<from manifest.yaml>"
  policy_version: "1.0.0"
  schema_version: "1.0.0"
  validator_version: "1.0.0"
  validated_at: "<ISO 8601>"
```

**The agent sets `final_result: PENDING` and `human_authorization.status: pending`.**

Instruct the engineer:
> "ReviewArtifact drafted at `artifacts/tasks/<task_id>/review.yaml`.
> To approve: set `human_authorization.status: approved`, add your name and timestamp.
> Then run: `zsh .github/ai-workflow/validators/review-gate.sh <review.yaml> <verification.yaml> <plan.yaml>`"

The agent may not set `final_result: APPROVED`. Only the engineer sets this after human review.
```

- [ ] **Step 6: Verify all modified files exist and are non-empty**

```bash
python3 -c "
import os
files = [
  'github/prompts/execute-plan.prompt.md',
  'github/prompts/verify.prompt.md',
  'github/prompts/review.prompt.md',
  'github/skills/verification/SKILL.md',
  'github/skills/review/SKILL.md',
]
for f in files:
    assert os.path.exists(f), f'missing: {f}'
    assert os.path.getsize(f) > 200, f'suspiciously short: {f}'
print('PASS')
"
```
Expected: `PASS`

- [ ] **Step 7: Commit**

```bash
git add github/prompts/execute-plan.prompt.md \
        github/prompts/verify.prompt.md \
        github/prompts/review.prompt.md \
        github/skills/verification/SKILL.md \
        github/skills/review/SKILL.md
git commit -m "feat: wire task_id, mandatory artifact reads, and human-authorized review into phase commands and skills"
```

---

### Task 8: Update validate-artifact.sh for validated_under

**Files:**
- Modify: `github/scripts/validate-artifact.sh`

- [ ] **Step 1: Add validated_under check to validate-artifact.sh**

After the existing `schema_version` check (line ~23), add:

```bash
# validated_under check — all artifacts must record governance binding
if ! rg -q '^validated_under:' "$artifact"; then
  add_fail "artifact.validated_under — required governance binding field missing"
fi
```

- [ ] **Step 2: Add governance path protection check**

At the end of the file, before the final failure check, add:

```bash
# Governance path protection: flag if a governance file is being validated as a normal artifact
governed_paths=(
  "ai-workflow/manifest"
  "ai-workflow/policies/"
  "ai-workflow/schemas/"
  "ai-workflow/validators/"
)
for gp in $governed_paths; do
  if [[ "$artifact" == *"$gp"* ]]; then
    add_fail "governance path detected — $artifact must not be validated via normal task flow"
  fi
done
```

- [ ] **Step 3: Test that existing valid artifact still passes**

Create a minimal v2 artifact with validated_under and verify it passes:

```bash
cat > /tmp/test-plan-valid.yaml << 'EOF'
schema_version: 2
problem:
  id: "P001"
  classification: bug-fix
  summary: "test"
  scope: []
  acceptance_signals: []
validated_under:
  manifest_version: "1.0.0"
  policy_version: "1.0.0"
  schema_version: "2.1.0"
  validator_version: "1.0.0"
  validated_at: "2026-05-02T00:00:00Z"
EOF
zsh github/scripts/validate-artifact.sh /tmp/test-plan-valid.yaml
```
Expected: exits 0 (PASS, may have other non-validated_under failures for missing fields, but not the validated_under check)

- [ ] **Step 4: Test that artifact without validated_under fails**

```bash
cat > /tmp/test-plan-no-governance.yaml << 'EOF'
schema_version: 2
problem:
  id: "P001"
  classification: bug-fix
  summary: "test"
  scope: []
  acceptance_signals: []
EOF
zsh github/scripts/validate-artifact.sh /tmp/test-plan-no-governance.yaml 2>&1 | grep validated_under
```
Expected: output contains `validated_under`

- [ ] **Step 5: Commit**

```bash
git add github/scripts/validate-artifact.sh
git commit -m "feat: add validated_under and governance path checks to validate-artifact.sh"
```

---

### Task 9: Update ARCHITECTURE.md

**Files:**
- Modify: `github/ARCHITECTURE.md`

- [ ] **Step 1: Add V1 Enforcement Gates section to ARCHITECTURE.md**

Add a new section after the existing `## V2 Artifact Model` section:

```markdown
## V1 Enforcement Gates

_Status: implemented — closes 10 scope-bypass paths identified in architecture audit (2026-05-02)._

The ten constraints below are now enforced by file-based mechanisms (validators, schemas, policies).
They are not conventions — they are enforceable through the CI-authoritative validators.

| # | Constraint | Mechanism |
|---|-----------|-----------|
| 1 | Pre-write quick-task gate | `validators/preflight-quick-task.sh` — runs before first file edit |
| 2 | Typed escalation handoff | `EscalationSeed/v1` schema; post-escalation diff limited to artifacts only |
| 3 | Degraded relaxes no gates | `policies/planning-states.yaml`: `relaxes_enforcement_gates: false` |
| 4 | CI-authoritative validators | `policies/governance.yaml` protected paths; agent-run is preflight only |
| 5 | Mandatory artifact read at phase entry | `validators/phase-prerequisite.sh`; prompts prohibit verbal additions |
| 6 | Plan-defined verification | `PlanArtifact.execution.verification.command` — set at plan time, immutable |
| 7 | Phase prerequisite table | `policies/phase-prerequisites.yaml`; execution+ commands hard-blocked |
| 8 | Human-authorized review | `ReviewArtifact/v1`: `human_authorization` required for `final_result: APPROVED` |
| 9 | Version-bound governance | `validated_under` field in all artifacts; upgrades not retroactive |
| 10 | Deterministic artifact storage | `artifacts/tasks/<task_id>/` — no search heuristics, path is authoritative |

### Authority Order

```
artifact schema (refs/schema.md, ai-workflow/schemas/)
> verification/review gates (validators/review-gate.sh, validators/preflight-quick-task.sh)
> phase semantics (policies/phase-prerequisites.yaml)
> runtime layout (ai-workflow/manifest.yaml)
> skill text (skills/**SKILL.md)
> command UX (prompts/*.prompt.md)
```

### What CI must enforce

CI is the authoritative gate. Agent-run validators are preflight convenience only.

CI must run on every PR:
1. `validate-artifact.sh` on all artifact files changed in the PR
2. `review-gate.sh` before merge approval
3. Governance path detection: any change to `protected_governance_paths` must be labeled `governance-change`
```

- [ ] **Step 2: Verify ARCHITECTURE.md contains the new section**

```bash
rg "V1 Enforcement Gates" github/ARCHITECTURE.md && echo "PASS" || echo "FAIL"
```
Expected: `PASS`

- [ ] **Step 3: Commit**

```bash
git add github/ARCHITECTURE.md
git commit -m "docs: add V1 Enforcement Gates section to ARCHITECTURE.md"
```

---

## Self-Review

### Spec coverage check

The 10 audit constraints map to tasks as follows:

| Constraint | Task |
|-----------|------|
| 1. Pre-write quick-task gate | Task 5 (preflight-quick-task.sh) + Task 6 (quick-task.prompt.md) |
| 2. Typed escalation handoff | Task 3 (EscalationSeed schema) + Task 6 (quick-task.prompt.md escalation section) |
| 3. Degraded relaxes no gates | Task 2 (planning-states.yaml) |
| 4. CI-authoritative validators | Task 2 (governance.yaml) + Task 5 (validators) |
| 5. Mandatory artifact read | Task 7 (execute-plan/verify/review prompts) |
| 6. Plan-defined verification | Task 4 (schema.md) + Task 6 (planning SKILL.md) + Task 7 (verification SKILL.md) |
| 7. Phase prerequisite table | Task 2 (phase-prerequisites.yaml) + Task 5 (phase-prerequisite.sh) |
| 8. Human-authorized review | Task 3 (ReviewArtifact schema) + Task 7 (review SKILL.md) |
| 9. Version-bound governance | Task 3 (validated_under in schemas) + Task 8 (validate-artifact.sh) |
| 10. Deterministic artifact storage | Task 1 (manifest.yaml + artifacts dir) + Tasks 6-7 (task_id in all prompts) |

All 10 constraints covered.

### No placeholders

All YAML, shell, and Markdown content is fully specified inline — no "TBD" or "fill in later".

### Type consistency

`task_id` used consistently across QuickTaskRecord, EscalationSeed, VerificationArtifact, ReviewArtifact, and all phase prompts. `validated_under` field structure is identical across all artifact schemas.
