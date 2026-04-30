---
ticket: WORKFLOW-UPLIFT-001
phase: spec
created: 2026-04-30
status: draft
schema_version: 1
---

# Spec: Model C2 — Simple Capability Uplift

## Problem Statement

The current workflow system enforces phase discipline and artifact integrity well, but has
four compounding problems that degrade real-world usefulness:

1. **Context bloat** — root instructions carry ceremony (handoff format, V1 compatibility)
   that consumes context on every session regardless of relevance.
2. **Structural permissiveness** — agents write code wherever convenient. File placement,
   package creation, and abstraction decisions are unconstrained. Structural debt accumulates
   silently because every existing gate (Stage 1, Stage 2) checks compliance and quality, not
   architecture.
3. **Repeated search** — agents re-discover codebase structure across sessions because there
   is no persistent exploration record and no session-level budget.
4. **Execution verbosity** — full test/lint/build output hits the context window on every run.
   No compact pass/fail signaling exists.

## Design Goals

Two axes, sequenced by dependency:

**Phase 1 — Context efficiency + foundation cleanup:**
Reduce root instruction size, eliminate V1 compatibility, add compact backpressure, add
caveman communication mode, define the sub-agent task contract.

**Phase 2 — Structural discipline:**
Generate an architecture map from the codebase index, add structural constraints to the
plan artifact, add a placement protocol for execution, add Stage 3 (structural integrity)
to the stage-review gate.

## Non-Negotiable Constraints

Preserved without exception:
- No success claim without evidence (test output pasted or script-verified)
- No code without a plan or explicit conscious-skip notation
- Human-readable artifacts in version control
- File-based state — no hidden runtime memory
- New chat at phase boundary
- Stage 1 and Stage 2 gates intact
- Slash command interface unchanged (Phase 1 + Phase 2 are additive only)
- Sub-agent execution capability preserved

Not in scope for this spec (Phase 3+):
- Merging skills (brainstorm+spec-writing, verify+review, index-codebase+index-knowledge)
- Slash command removals or renames
- Context packet mechanics simplification
- Explored-modules session file
- Module exploration budget enforcement
- Confidence-level enforcement change in context-packet-load

---

## Phase 1: Context Efficiency + Foundation Cleanup

### P1-1: `scripts/run-silent.sh`

**What:** A shell wrapper that swallows successful command output and surfaces only failures.

**Interface:**
```bash
# Usage: source run-silent.sh, then:
run_silent <command> [args...]

# On success: prints ✓ to stdout, returns exit 0
# On failure: prints full captured output to stdout, returns original exit code
```

**Implementation:**
```bash
run_silent() {
  local out
  out=$("$@" 2>&1)
  local code=$?
  if [ $code -eq 0 ]; then
    printf "✓\n"
  else
    printf "%s\n" "$out"
  fi
  return $code
}
```

**Integration:** `conventions/SKILL.md` template gains a new field:
```
Test command (silent): run-silent.sh [test command from Test command: field]
```
`setup/SKILL.md` must populate this field during repo init using the detected test command.

The silent form is the default during TDD loops and between-step verification. The full form
is used when debugging a failure.

**Acceptance:** Running `run_silent <passing command>` prints only `✓`. Running
`run_silent <failing command>` prints full output. Exit codes are preserved.

---

### P1-2: `skills/caveman/SKILL.md`

**What:** A triggerable skill that switches the agent into ultra-compressed communication
mode for execution loops. Reduces filler while preserving technical precision.

**Trigger:** User types `/caveman` or "caveman mode" during execution, or agent activates
it automatically when entering a TDD loop (see phase prohibition below).

**Compression rules:**
- No introductory sentences ("I will now...", "Let me check...")
- No summary at the end of each message ("I have completed...")
- Status updates: one line maximum (`✓ Step 3 done. Next: add index.`)
- File paths: abbreviated to last two segments unless ambiguous
- Test results: `✓ 47 passed` or `✗ 2 failed — see below`
- Phase checkpoints: still required in full; caveman does not apply to checkpoint output

**Phase prohibition — where caveman MUST NOT be active:**
- Brainstorming and spec convergence
- Planning structural analysis
- Stage-review findings (Stage 2 and Stage 3 findings must be precise, not compressed)
- Any output that becomes a durable artifact

**Deactivation:** User types `/no-caveman` or leaves execution phase.

**File structure:** Single `SKILL.md` under 80 lines. No companion files.

**Acceptance:** In caveman mode, a five-step TDD loop produces status updates of one line
each. Phase checkpoint output is unchanged. Stage 3 findings are unchanged.

---

### P1-3: `protocols/handoff.md` — extracted from root instructions

**What:** Move the handoff block specification out of `copilot-instructions.md` into a
dedicated protocol file. The root instruction is replaced with a single pointer.

**Content moving to `protocols/handoff.md`:**
- The full handoff block template (Phase complete / Summary / Artifacts / Next)
- All rules governing the block (every field filled, no template brackets, etc.)
- Handoff file write mechanics (path derivation, create-or-append logic, read-back confirmation)
- `log.md` append rule
- `artifact-index.md` append rule
- Failure signal when write cannot be confirmed

**What stays in `copilot-instructions.md`:**
A single line: `Phase completion: follow protocols/handoff.md`

**Target size of `copilot-instructions.md` after extraction:** Under 50 lines.
Content retained: Priority order (4 lines), Hard rules (4 lines), Drift control (7 lines),
Conscious skip protocol (5 lines), Context hygiene pointer (1 line), phase completion
pointer (1 line).

**Acceptance:** `copilot-instructions.md` is under 50 lines. The handoff block is
reproduced identically in `protocols/handoff.md`. Agent behavior at phase boundaries is
unchanged.

---

### P1-4: V1 compatibility removal

**What:** Delete all V1 compatibility code from the six core skills.

**Skills affected and what is removed:**

| Skill | Removed |
|---|---|
| `spec-writing/SKILL.md` | Version gate block; V1 prose extraction steps; V1 YAML parsing |
| `planning/SKILL.md` | V1 plan format reading; V1 prose-parsed file lists |
| `execution/SKILL.md` | V1 execution mode detection; V1 phase file parsing |
| `stage-review.md` | `### V1` subsection in Stage 1; prose `**Files in this phase:**` parsing |
| `review/SKILL.md` | Version gate; V1 spec section extraction |
| `validate-artifact/SKILL.md` | V1 artifact handling (or remove skill entirely — see P1-5) |

**Rule:** In-flight V1 tickets do not survive this change. There are few active users; this
is the right time to cut.

**Acceptance:** No skill file contains the string "PLAN_VERSION = 1", "BRAINSTORM_VERSION = 1",
"schema_version: 1" (in a check context), or "V1" in a section heading. Skills compile to
correct behavior on V2 artifacts only.

---

### P1-5: `scripts/validate-artifact.sh` — replaces validate-artifact skill

**What:** A deterministic shell script that validates a V2 artifact against schema invariants
and referential integrity rules. Replaces `skills/validate-artifact/SKILL.md`.

**Interface:**
```
Usage: validate-artifact.sh <artifact-path>

Exit 0: PASS (no output, or "PASS" if --verbose)
Exit 1: FAIL, with itemized violations to stdout:
  FAIL: problem.id — missing required field
  FAIL: steps[P1.S2].requirement_ids[0] — R99 not in requirements[*].id
  FAIL: decisions[D1].id — duplicate across decisions[]
```

**Checks implemented:**
- Required fields present on each primitive (ProblemRecord, DecisionRecord, Requirement, StepNode)
- `id` format compliance (`/^[A-Z]+-[0-9]+$/`, `/^D[0-9]+$/`, `/^R[0-9]+$/`, `/^P[0-9]+\.S[0-9]+$/`)
- Referential integrity: `step.requirement_ids[i]` exists in `requirements[*].id`
- Referential integrity: `requirement.source_decision` exists in `decisions[*].id`
- Duplicate ID detection across each primitive array
- `depends_on` references resolve to existing StepNode IDs with phase ≤ current step

**Not checked by script (remain LLM-judged):**
- Semantic correctness of descriptions
- Whether `chosen ∉ rejected[*].option` (string equality check is too fragile for script)
- Immutability (upstream fields unchanged from parent artifact)

`skills/validate-artifact/SKILL.md` is removed. Consuming skills that previously invoked
the skill now call `validate-artifact.sh` instead. Silent invocation behavior is preserved:
on PASS, no output; on FAIL, emit the BLOCK message and stop.

**Acceptance:** Script correctly identifies all referential integrity violations in a
manually constructed invalid artifact. Script passes on a known-good V2 artifact.

---

### P1-6: `protocols/subagent-task.md`

**What:** A short protocol (under 30 lines) embedded in every sub-agent dispatch prompt by
the parent agent. Defines scope boundary and mandatory output format.

**Content:**

```
# Sub-Agent Task Protocol

You are executing one bounded task. You have no authority over the plan, structural
constraints, or decisions. The parent agent evaluates your output.

## Scope Rules
- Execute only the task given. Do not expand scope.
- Do not write to plan, spec, or convention files.
- Do not make structural or architectural decisions — report findings only.
- If the task is ambiguous, report ambiguity in your output rather than guessing.

## Output Format (mandatory — no other format accepted)
SUBAGENT RESULT
Task: [one-line restatement of what was asked]
Files inspected: [list, or "none"]
Relevant findings: [concrete facts: paths, signatures, patterns, counts]
Negative findings: [what was searched but not found]
Recommended next action: [one line for the parent agent]
Confidence: high | medium | low
```

**When to dispatch a sub-agent (decision rule for parent agent):**

Use when: repo is large AND search requires multiple reads that would pollute parent context
AND the result can be summarized in the output format above AND the task is exploratory
but clearly bounded.

Do not use when: files are already in context, task requires product judgment, task
requires structural authority, or delegation cost exceeds context saving.

**Acceptance:** Every sub-agent invocation in a phased-subagent execution session returns
output matching the mandatory format. Parent agent never accepts freeform sub-agent output.

---

### P1-6b: Move `skills/SCHEMA.md` to `refs/schema.md`

**What:** Relocate the schema definition file out of the skills directory (where agent-loaded
files live) into a new `refs/` directory (human-readable references not loaded by agents).
Create `refs/` if it does not exist.

**Why now:** The schema file is a reference document, not a triggerable skill. It does not
belong in `skills/`. Relocating it in Phase 1 allows the folder layout to be correct from
the start of implementation, and avoids skills referencing it from an incorrect location
after Phase 2 adds `refs/schema.md` as the structural authority for `structural_constraints`.

**Changes:**
- Create `refs/` directory
- Move `skills/SCHEMA.md` → `refs/schema.md` (content unchanged)
- Update all references in skills and protocols from `skills/SCHEMA.md` to `refs/schema.md`

**Acceptance:** `skills/SCHEMA.md` does not exist. `refs/schema.md` exists with identical
content. All skill files that referenced the old path now reference `refs/schema.md`.

---

### P1-7: Static agent file evaluation

**What:** Evaluate `agents/design.agent.md`, `agents/implementation.agent.md`,
`agents/review.agent.md` for removal.

**Decision rule:** If the agent file's content is fully captured by the skill it routes to
(persona statement, behavioral rules, tool list), the file is indirection and is removed.
The prompt dispatcher already routes to the correct skill; the agent file adds a layer
with no behavioral delta.

**Expected outcome:** All three files are removed. The personas in the brainstorming,
execution, and review skills already establish the behavioral context. If any agent file
contains non-redundant tool configuration or behavioral rules not present in the skills,
those rules are moved to the appropriate skill before the file is deleted.

**Acceptance:** Removing the `agents/` directory does not change agent behavior on any
existing command. Validated by running `/brainstorm`, `/execute-plan`, and `/review` on
a test ticket and confirming identical behavior.

---

## Phase 2: Structural Discipline

Phase 2 depends on Phase 1 being complete. Stage 3 depends on `architecture.md` existing
for the target repo — if the file is absent, Stage 3 skips with a logged signal rather
than blocking.

### P2-1: Structural fields in `conventions/SKILL.md` template

**What:** Add a new `## Architecture` section to the conventions template. `setup/SKILL.md`
detects and populates these fields during repo init.

**New fields:**
```
## Architecture
Layer map:          .github/index/architecture.md
Forbidden packages: []            # e.g. [utils, helpers, common, shared]
Simplicity mode:    true
```

**`setup/SKILL.md` detection logic:**
- `Layer map:` — always set to `.github/index/architecture.md` (the generated path)
- `Forbidden packages:` — detect any existing `utils/`, `helpers/`, `common/` directories;
  list them as already-frozen patterns; leave array empty if none found
- `Simplicity mode:` — always `true` on init; engineer changes to `false` only if the
  repo explicitly requires architectural experimentation

**Acceptance:** Running `/setup` on a repo without the Architecture section populates all
three fields. Running it on a repo that already has the section leaves existing values
unchanged.

---

### P2-2: `index/architecture.md` — new output from `/index codebase`

**What:** `index-codebase/SKILL.md` generates `architecture.md` alongside `index.md` and
module pages. This file is the structural authority read by planning and Stage 3.

**Format:**
```markdown
# Architecture Map
generated: YYYY-MM-DD

## Layers
| Layer | Package pattern | Responsibility | Allowed dependencies |
|---|---|---|---|
| [name] | [path glob] | [one line] | [layer names only, or "none"] |

## Placement Heuristics
- New [component type] → [target package]
- New [component type] → prefer modifying [existing file pattern] before creating new

## Existing Anti-Patterns (frozen — do not add to)
- [path]: [why it is an anti-pattern] — [file count]

## Extension Points
- New [feature type]: follow pattern in [path to canonical example]
```

**Generation logic:**
- Layers are inferred from the module dependency graph already built by `index-codebase`.
  A layer is a group of modules with consistent dependency direction (modules in layer A
  never depend on modules in layer B that depend back on A).
- Placement heuristics are derived from the most common package for each responsibility
  type already present in the codebase.
- Anti-patterns are flagged when a module's observed location contradicts its inferred
  layer (e.g., a service-responsibility class found in a `utils/` directory).
- Extension points are the most recently modified files per layer — likely active patterns.

**When `architecture.md` cannot be reliably inferred** (e.g., first run on a flat repo
with no clear layering): generate a minimal file with a single "Unknown" layer and a note:
`# Architecture Map — insufficient structure detected. Engineer should populate manually.`

**Acceptance:** Running `/index codebase` on a layered repo produces a non-trivial
`architecture.md` with at least two layers and at least one placement heuristic.
Running it on a flat repo produces the minimal file without error.

---

### P2-3: `structural_constraints` block in `PlanArtifact`

**What:** An optional block added to `refs/schema.md` (formerly `skills/SCHEMA.md`) and
produced by the planning skill during structural analysis.

**Schema (added to PlanArtifact, optional field):**
```typescript
interface StructuralConstraints {
  layers_touched:        string[];   // layer names from architecture.md
  forbidden_new_packages: string[];  // package names — adds to conventions list for this plan
  simplicity_mode:       boolean;    // inherits from conventions; false = justify explicitly
  follows_pattern?:      string;     // path to canonical file for this plan's new code
  packaging_rationale?:  string;     // required when any new package is created
}
```

**Non-breaking:** Field is optional. Plans without it are valid. Stage 3 uses
`architecture.md` as sole reference when the block is absent.

**Authority rule:** When `structural_constraints` and `architecture.md` conflict (e.g., plan
allows a package that architecture.md forbids), the plan wins — the engineer approved it.
Stage 3 flags the deviation as a conscious override and requires `packaging_rationale` to
be non-empty. If `packaging_rationale` is absent, Stage 3 FAIL.

**Acceptance:** A plan with `structural_constraints` passes `validate-artifact.sh`.
A plan without the block also passes.

---

### P2-4: Planning structural analysis step

**What:** A new step added to `planning/SKILL.md` before any StepNode is written.

**Insertion point:** After "Intelligence Retrieval" and before "Before Writing a Single Step."

**Step content:**
```
## Structural Analysis (run before writing any StepNode)

1. Read .github/index/architecture.md.
   If absent: log "Architecture map not found — structural constraints will not be enforced
   for this plan. Consider running /index codebase." Proceed without the block.

2. For the scope in the BrainstormArtifact, identify which layers will be touched.
   List them in structural_constraints.layers_touched.

3. Check conventions Forbidden packages. Add any plan-specific additions to
   structural_constraints.forbidden_new_packages.

4. Identify one canonical example file for the primary new code this plan introduces.
   Set structural_constraints.follows_pattern to that path.

5. If any new package or directory will be created: set packaging_rationale explaining why
   the existing structure cannot accommodate the new component. If no new packages:
   set forbidden_new_packages to include any directories that should not be created
   during this plan's execution.

6. Write the structural_constraints block into the plan header before writing phases.
```

**Acceptance:** Plans produced after this change contain a `structural_constraints` block
when `architecture.md` is present. Plans produced without `architecture.md` do not contain
the block and log the warning.

---

### P2-5: `protocols/implementation-structure.md`

**What:** A short protocol (target: under 45 lines) read by `execution/SKILL.md` before
any step that creates a new file. Encodes the structural discipline rules for execution.

**Content:**

```markdown
# Protocol: Implementation Structure

**Purpose:** Prevent arbitrary file placement, unnecessary abstractions, and structural
violations during execution. Read before creating any new file.

**Non-goals:** Does not determine which files to create (plan's responsibility). Does not
run after the fact (Stage 3 responsibility). Does not apply to test files or generated
code.

---

## Rules (checked in order before creating any file)

1. **Prefer modify over create.** Check if an existing file in the target module can
   receive this change. Only create a new file if modification is genuinely insufficient.

2. **New file placement.** The file's package/directory must appear in:
   - `architecture.md` placement heuristics, OR
   - `structural_constraints.follows_pattern` neighbourhood, OR
   - an explicit entry in `structural_constraints` allowing it.
   If none of the above: STOP. Ask before creating.

3. **New package/directory.** Always a STOP. Check `structural_constraints.forbidden_new_packages`.
   If the package is listed or conventions Forbidden packages includes it: do not create.
   Escalate to engineer. If the plan's `packaging_rationale` covers it: proceed and note it
   in the phase checkpoint.

4. **New abstraction not in plan.** Any new helper class, utility function, base class, or
   interface not listed in the plan's StepNode files: STOP before writing. Describe the
   need and ask.

5. **Match neighbouring complexity.** New files should be approximately as complex as
   existing files in the same layer. A new file substantially larger than its neighbours
   (rough signal: >2× line count) requires a note in the phase checkpoint explaining why.

6. **Framework placement is not negotiable.** Spring controller → controllers/. Django
   view → views.py. Rails model → models/. Framework structure overrides convenience.
```

**Acceptance:** During a phased execution session, the agent stops and escalates before
creating a package not in the plan's `structural_constraints`. The escalation message
references this protocol.

---

### P2-6: Execution IRON LAW — simplicity constraint

**What:** An IRON LAW added to `execution/SKILL.md`, at the top of the file alongside the
existing plan-reading IRON LAW.

**Text:**
```
> **IRON LAW:** Small code. Existing place. Existing pattern. No new structure unless
> the plan says so. Before creating any file, read protocols/implementation-structure.md.
```

**Acceptance:** The law appears verbatim in the skill file. During execution, any new-file
creation is preceded by an explicit check against `implementation-structure.md`.

---

### P2-7: Stage 3 — Structural Integrity gate

**What:** A third gate added to `protocols/stage-review.md`. Runs only after Stage 1 PASS
and Stage 2 PASS.

**Inputs:**
- Actually-changed files (from `git diff --name-status HEAD~1`)
- Plan's `structural_constraints` block (if present)
- `index/architecture.md` (if present)
- Incidental files list from Stage 1 (source-code incidentals receive structural review;
  lock files and framework-generated files are exempt)
- Module pages for any newly created files (check responsibility overlap)

**Checks (in order — stop at first FAIL):**

1. **Placement** — each created file's path matches its layer in `architecture.md`
   placement heuristics, or is covered by `structural_constraints`. Exempt: files in
   `architecture.md` anti-pattern paths that were already there before this phase.

2. **Forbidden packages** — no new directory was created that appears in
   `structural_constraints.forbidden_new_packages` or conventions `Forbidden packages`,
   unless `packaging_rationale` is non-empty and covers it.

3. **Incidental source file review** — incidental files that are source code (not lock
   files or build artifacts) are checked for placement. An incidental source file in the
   wrong layer is a Stage 3 FAIL regardless of how it passed Stage 1.

4. **Duplicate abstraction** — any created file whose stated responsibility (from its
   class/function names) duplicates a responsibility already documented in the module pages
   is flagged.

**Output format (must stay compact):**
```
[Stage 3] Structural integrity: PASS

[Stage 3] Structural integrity: FAIL — src/utils/TokenParser.java: responsibility belongs
in existing AuthService; not sanctioned by structural_constraints
  (+ N additional findings — resolve highest-severity first)
```

**Graceful fallback when `architecture.md` absent:** Stage 3 skips checks 1 and 3, runs
only checks 2 and 4. Emits: `[Stage 3] Note: architecture.md not found — placement checks
skipped. Run /index codebase to enable full structural review.`

**On FAIL:** Engineer chooses one of:
- Fix the structural violation
- Update `structural_constraints` to sanction the deviation + add `packaging_rationale`
- Explicit conscious override: type "Conscious structural override: [reason]" — logged in
  the phase checkpoint, not silently accepted

**Acceptance:** Stage 3 FAIL is produced when a created file lands in a package not in
`architecture.md` and not in `structural_constraints`. Stage 3 PASS is produced when all
placement matches the architecture map. Stage 3 skips without error when `architecture.md`
is absent.

---

## Folder Layout After Phase 1 + Phase 2

```
.github/
├── copilot-instructions.md           # < 50 lines — hard rules + pointers only
├── skills/
│   ├── conventions/SKILL.md          # + Architecture section
│   ├── setup/SKILL.md                # + structural field population
│   ├── brainstorming/SKILL.md
│   ├── planning/SKILL.md             # + structural analysis step
│   ├── execution/SKILL.md            # + simplicity IRON LAW, + implementation-structure ref
│   ├── tdd/SKILL.md
│   ├── debugging/SKILL.md
│   ├── review/SKILL.md
│   ├── index-codebase/SKILL.md       # + architecture.md generation
│   ├── index-knowledge/SKILL.md
│   ├── context-packet/SKILL.md
│   ├── retrieval-protocol/SKILL.md
│   ├── cross-repo/SKILL.md
│   └── caveman/SKILL.md              # new
├── protocols/
│   ├── codebase-search.md
│   ├── stage-review.md               # + Stage 3
│   ├── context-packet-load.md
│   ├── phase-checkpoint.md
│   ├── verification-gate.md
│   ├── handoff.md                    # new — extracted from root
│   ├── implementation-structure.md   # new
│   └── subagent-task.md              # new
├── scripts/
│   ├── run-silent.sh                 # new
│   └── validate-artifact.sh          # new — replaces validate-artifact skill
├── refs/
│   ├── schema.md                     # moved from skills/SCHEMA.md
│   ├── workflow.md
│   └── cheat-sheet.md
├── prompts/
│   └── *.prompt.md                   # unchanged
└── index/                            # generated — never hand-edited
    ├── index.md
    ├── architecture.md               # new output from /index codebase
    ├── knowledge/
    └── modules/
```

`agents/` directory: removed after evaluation confirms files are persona-only indirection.
`skills/validate-artifact/` directory: removed after `validate-artifact.sh` is validated.
`skills/spec-writing/`, `skills/verification/`: Phase 3 merges — not in this spec.

---

## Acceptance Signals (Phase 1 complete)

- `copilot-instructions.md` is under 50 lines
- No skill file contains V1 parsing logic or V1 version gates
- `run-silent.sh` produces `✓` on a passing command, full output on a failing command
- `validate-artifact.sh` exits 0 on a valid V2 artifact, exits 1 with field-level messages on invalid
- `caveman/SKILL.md` exists and is under 80 lines
- `protocols/handoff.md` contains the full handoff block spec
- `protocols/subagent-task.md` exists and is under 30 lines
- `agents/` directory is absent or contains only files with non-redundant behavioral content
- `refs/schema.md` exists; `skills/SCHEMA.md` does not exist; no skill file references the old path

## Acceptance Signals (Phase 2 complete)

- Running `/index codebase` on a layered repo produces `index/architecture.md` with at
  least two layers and at least one placement heuristic
- `conventions/SKILL.md` template contains the `## Architecture` section
- A plan produced by `/plan` on a repo with `architecture.md` contains a
  `structural_constraints` block
- During execution, creating a file in a forbidden package triggers a stop-and-escalate
  before any file is written
- Stage 3 produces FAIL with a specific finding when a file lands outside its layer
- Stage 3 skips placement checks and logs the note when `architecture.md` is absent
- `simplicity IRON LAW` text appears verbatim in `execution/SKILL.md`
- `protocols/implementation-structure.md` exists and is under 45 lines

---

## Documentation Updates (parallel to Phase 1 + Phase 2)

`WORKFLOW.md`, `CHEAT-SHEET.md`, and `ARCHITECTURE.md` are the canonical human references
for the system. They must be updated in lockstep with the capability changes so the
engineer's mental model stays accurate. These updates are part of Phase 1 and Phase 2
respectively — a capability change is not complete until its reference documentation
reflects it.

**File location:** These three files remain at `github/` root in Phase 1 and Phase 2. They
are updated in-place. Moving them to `refs/` is a Phase 3 reorganisation concern, not in
scope here. The folder layout diagram in this spec shows the Phase 3+ target state for
reference; the Phase 1+2 deliverable is content updates only.

### ARCHITECTURE.md updates (Phase 1 + Phase 2)

`ARCHITECTURE.md` describes system mechanics. It must reflect the new folder layout,
the removal of the `agents/` directory, and the addition of the structural discipline layer.

**Phase 1 additions:**
- New `scripts/` section: describe `run-silent.sh` (what it does, when to use it) and
  `validate-artifact.sh` (what it replaces, what it checks)
- New `protocols/` entries: `handoff.md` (extracted from root instructions, purpose),
  `subagent-task.md` (sub-agent output contract, when invoked)
- Update `skills/` section: add `caveman/SKILL.md` entry; remove `validate-artifact/`
  entry
- Update root instruction section: note the size target (< 50 lines) and that handoff
  mechanics moved to `protocols/handoff.md`
- Update agent section: clarify the distinction between static persona files (removed)
  and runtime sub-agent execution (preserved in `execution/SKILL.md`). Describe the
  sub-agent decision rule and output format.
- Add `refs/` section: describe `schema.md` (moved from `skills/SCHEMA.md`),
  `workflow.md`, `cheat-sheet.md` as human-facing reference files not loaded by agents.

**Phase 2 additions:**
- New `Structural Discipline` section covering the three-layer model:
  - Layer 1 (Declare): `conventions/SKILL.md` Architecture section + plan
    `structural_constraints` block
  - Layer 2 (Inform): `index/architecture.md` — what it contains, how it is generated,
    who reads it
  - Layer 3 (Constrain): `protocols/implementation-structure.md` — when it is read,
    what it enforces
  - Layer 4 (Gate): Stage 3 in `protocols/stage-review.md` — when it runs, what it
    checks, PASS/FAIL format, graceful fallback
- Update `index/` section: add `architecture.md` as a generated output with a description
  of its format and the information it encodes (layers, placement heuristics,
  anti-patterns, extension points)
- Update `protocols/stage-review.md` entry: add Stage 3 description

### WORKFLOW.md updates (Phase 1 + Phase 2)

`WORKFLOW.md` is the end-to-end guide engineers read to understand what to run and when.

**Phase 1 additions:**
- Add `caveman` to the command table: "Compact execution mode — reduces status-update
  verbosity during TDD and execution loops. Type `/caveman` to activate, `/no-caveman`
  to deactivate. Not active during brainstorming, planning, or review."
- Add `scripts/` section: describe when to use `run-silent.sh` (wrap test commands in
  TDD loops), when to use `validate-artifact.sh` (debug V2 artifact validation errors)
- Update Session Hygiene section: note that V1 artifacts are no longer supported;
  all tickets must use V2 format (`schema_version: 2`)
- Update agent section: replace "Switch to @Design Agent / @Implementation Agent /
  @Review Agent" with "The correct skill is loaded automatically by the prompt dispatcher.
  Separate agent personas have been removed." Add a paragraph on sub-agent execution:
  when the execution skill uses sub-agents, what the engineer sees (compact SUBAGENT
  RESULT blocks), and that the parent agent owns all decisions.

**Phase 2 additions:**
- Add structural discipline to the workflow narrative: after planning, note that the
  plan now includes a `structural_constraints` block summarising which layers are touched
  and which packages are forbidden
- Add `/index codebase` output note: "Generates `index/architecture.md` in addition to
  the module index. Review this file after first-run to confirm layers are correctly
  inferred. Edit manually if the auto-generated structure is incomplete."
- Update Phase Overview table: add a `Structural Analysis` row inside the Plan phase
  ("Planning now includes a structural analysis step before writing StepNodes. No
  separate command required.")
- Update Execution Modes section: add a note that the simplicity IRON LAW applies in
  all modes. In phased-subagent mode, each sub-agent also reads
  `implementation-structure.md` before creating files.
- Update stage-review section: document Stage 3. Add a row to the gates table:
  `[Stage 3] Structural integrity: PASS / FAIL — placement, forbidden packages,
  incidental source files, duplicate abstractions. Skips if architecture.md absent.`

### CHEAT-SHEET.md updates (Phase 1 + Phase 2)

`CHEAT-SHEET.md` is the quick daily-use reference. Keep additions minimal — one line
per new capability.

**Phase 1 additions:**
- Add to Commands table: `/caveman` — activate compact execution mode
- Add to Commands table: `/no-caveman` — return to normal communication
- Add a `Scripts` section (2 rows):
  - `run-silent.sh <cmd>` — run a command; ✓ on pass, full output on fail
  - `validate-artifact.sh <path>` — validate a V2 artifact; exit 0 = PASS, exit 1 = FAIL with violations
- Remove: any reference to V1 artifact format
- Remove: any reference to `@Design Agent`, `@Implementation Agent`, `@Review Agent`

**Phase 2 additions:**
- Add to Commands table: `/index codebase` — now also generates `index/architecture.md`
- Add a `Structural Constraints` section (4 rows):
  - `index/architecture.md` — layer map generated by `/index codebase`; read by planning + Stage 3
  - `conventions: Forbidden packages` — packages that must not be created; enforced during execution
  - `structural_constraints` block in plan — per-ticket override; requires `packaging_rationale` for new packages
  - `Conscious structural override` — typed by engineer to bypass Stage 3 FAIL; logged in checkpoint
- Add to Stage Review table: `[Stage 3] Structural integrity` — placement + forbidden packages + incidental source + duplication

### Acceptance (documentation)

- `ARCHITECTURE.md` contains a `Structural Discipline` section after Phase 2
- `ARCHITECTURE.md` sub-agent section accurately describes the decision rule and output format
- `WORKFLOW.md` command table includes `/caveman` and documents Stage 3
- `CHEAT-SHEET.md` `Scripts` section lists both scripts with their interfaces
- No reference to V1 format, static agent files, or the old 9-step flow remains in any
  of the three documents without a deprecation or removal note

---

## Open Questions (resolved before implementation begins)

**OQ1 — Architecture map seeding:** When `index-codebase` cannot confidently infer layers
(flat repo, mixed structure), should it generate a skeletal `architecture.md` that the
engineer populates, or block generation and emit an instruction? **Decision:** Generate the
skeletal file with a prominent `# Manual population required` header. Do not block. This
allows Stage 3 to activate partially even on under-specified repos.

**OQ2 — Stage 3 authority conflict:** When `structural_constraints` and `architecture.md`
conflict, the plan wins — but `packaging_rationale` must be non-empty. **Decision:**
Specified above in P2-3. No further open question.

**OQ3 — Incidental file exemptions:** Lock files, build artifacts, and IDE files (`.idea/`,
`.DS_Store`, `*.lock`) are exempt from Stage 3 structural review. Source files that pass
Stage 1 as incidental are not exempt — they receive full Stage 3 placement review.
**Decision:** Specified above in P2-7. The incidental exemption list is `conventions/SKILL.md`
`Incidental file patterns:` — patterns already in that list that are clearly non-source
(lock files, generated code markers) are exempt. Anything else is reviewed.

**OQ4 — Simplicity signal for Stage 3 complexity check:** The >2× line count heuristic is
a signal, not a gate. Stage 3 does not FAIL on complexity alone — it flags in the phase
checkpoint for engineer awareness. A FAIL requires a placement, package, or duplication
violation. **Decision:** Complexity flagging is informational only; not a FAIL trigger.
This avoids false positives on legitimately large files.
