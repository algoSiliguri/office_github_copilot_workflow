# Workflow System Structural Clarity — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve legibility, modularity, and determinism of the `github/` workflow system through structural changes only — no behavioral changes.

**Architecture:** (1) Extract 5 shared protocols from `skills/execution/SKILL.md` into a new `github/protocols/` directory; (2) restructure v1/v2 branching in `execution`, `context-packet`, and `planning` skills to use isolated `### V2` / `### V1` subsections; (3) add `Non-goals:` to every skill's `## Metadata` block; (4) make 3 targeted additions to `copilot-instructions.md`.

**Tech Stack:** Plain Markdown files. No build system. Verification via `grep` and file reads.

---

## All Files Changed

**Phase 1 — Protocol files (all new):**
- `github/protocols/codebase-search.md` — Phase 1: new protocol file
- `github/protocols/verification-gate.md` — Phase 1: new protocol file
- `github/protocols/stage-review.md` — Phase 1: new protocol file
- `github/protocols/phase-checkpoint.md` — Phase 1: new protocol file
- `github/protocols/context-packet-load.md` — Phase 1: new protocol file

**Phase 2 — execution/SKILL.md:**
- `github/skills/execution/SKILL.md` — Phase 2: Non-goals + protocol references + v1/v2 isolation

**Phase 3 — context-packet/SKILL.md:**
- `github/skills/context-packet/SKILL.md` — Phase 3: Non-goals + v1/v2 isolation

**Phase 4 — planning/SKILL.md:**
- `github/skills/planning/SKILL.md` — Phase 4: Non-goals + v1/v2 isolation

**Phase 5 — Non-goals (12 remaining skills):**
- `github/skills/setup/SKILL.md`
- `github/skills/brainstorming/SKILL.md`
- `github/skills/spec-writing/SKILL.md`
- `github/skills/verification/SKILL.md`
- `github/skills/review/SKILL.md`
- `github/skills/debugging/SKILL.md`
- `github/skills/tdd/SKILL.md`
- `github/skills/index-codebase/SKILL.md`
- `github/skills/index-knowledge/SKILL.md`
- `github/skills/validate-artifact/SKILL.md`
- `github/skills/retrieval-protocol/SKILL.md`
- `github/skills/cross-repo/SKILL.md`

**Phase 6 — copilot-instructions.md:**
- `github/copilot-instructions.md` — Phase 6: 3 targeted additions

---

## Phase 1: Protocol Files

**Files in this phase:**
- Create: `github/protocols/codebase-search.md`
- Create: `github/protocols/verification-gate.md`
- Create: `github/protocols/stage-review.md`
- Create: `github/protocols/phase-checkpoint.md`
- Create: `github/protocols/context-packet-load.md`

> **Execution mode note:** All 5 files are independent creates. Write all 5 before verifying.

- [ ] **Step 1: Create `github/protocols/codebase-search.md`**

Source: `github/skills/execution/SKILL.md` — "Codebase Search Protocol" section (lines 160–190). Write this file exactly:

```markdown
# Protocol: Codebase Search

**Purpose:** Locate a specific code element using semantic search with bounded fallback to grep, capped at 2 searches per query.

**Inputs:** A specific, formulated query (what to find — class name, method name, or constant).

**Outputs:** The location of the requested code element, or a "not found" report after exhausting the search budget.

**Non-goals:** Does not modify code. Does not perform broad module exploration. Does not set or read context packet coverage.

---

**Step 0: Knowledge state check (run before every module exploration):**
Identify the module name for the file or area you are about to explore. Then evaluate in order — first match wins:

1. Context packet is loaded AND this module appears explicitly by name in `## Module Context` → **no signal** — proceed directly to step 1. (Exact name match only — do not infer coverage.)
2. `[KNOWLEDGE_PATH]/[module].md` exists → emit, then proceed to step 1:
   ```
   Context reuse signal:
   This module has prior structured knowledge:
   - <1-line summary from the file's ## Summary section>
   ```
3. Neither condition above is met → emit, then proceed to step 1:
   ```
   Context reuse signal:
   No prior structured knowledge available for this module.
   This exploration is not reusable unless captured in the knowledge system.
   ```

Signal is informational only — never blocks execution. Emit one signal (or none) per module per exploration.

1. **Formulate a specific query**: name exactly what you're looking for. Bad: "find auth code". Good: "UserAuthService class" or "JWT token validation method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears in the first page**: use it and stop.
4. **If zero results or all irrelevant**: try once more with a synonym or the exact class/method name as a literal string. Maximum 2 `semantic_search` calls per question.
5. **Fallback after 2 failed searches**: use `grep_search` with the exact class name, method name, or unique constant.
6. **Stop when found**: do not continue searching once you have what you need for the current step.
```

- [ ] **Step 2: Create `github/protocols/verification-gate.md`**

Source: `github/skills/execution/SKILL.md` — "Verification Gate" section (lines 192–201). Write this file exactly:

```markdown
# Protocol: Verification Gate

**Purpose:** Ensure no success claim is made without a fresh command execution and pasted terminal output as evidence.

**Inputs:** The claim being made (e.g., "tests pass"). The exact command that proves it.

**Outputs:** A verified assertion with pasted terminal output, or a blocked claim if evidence is absent.

**Non-goals:** Does not determine which command to run (orchestrator responsibility). Does not retry on failure. Does not interpret what the output means.

---

Before claiming any of these: "step complete", "phase complete", "all tests pass", "full suite green" — run this gate:

1. **IDENTIFY:** What exact command proves the claim?
2. **RUN:** Execute it now — fresh execution, not cached output.
3. **READ:** Read the full output including exit code.
4. **CLAIM:** State the claim with the pasted evidence.

Reject these: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.
```

- [ ] **Step 3: Create `github/protocols/stage-review.md`**

Source: Stage 1 and Stage 2 logic from `github/skills/execution/SKILL.md` Steps 2b (lines 225–236) and 2c (lines 424–444). This file absorbs the two v1/v2 Stage 1 forks that currently exist in execution — they are removed from execution after Phase 2. Write this file exactly:

```markdown
# Protocol: Stage Review

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

---

## Stage 1: Spec Compliance

### V2 (PLAN_VERSION = 2)

- `plan_listed` = all `files[*].path` values from `phases[*].id=N .steps[*].files` (typed array, no text parsing)
- `actually_changed` = paths in `git diff --name-status HEAD~1` with status `A` (added), `M` (modified), or `R` (renamed). Paths with status `D` (deleted): check these against plan_listed separately — a `D` path not in plan_listed and not covered by a `step-removed` amendment = Stage 1 FAIL.
- Classify each path in `actually_changed`:
  - Present in `plan_listed` → expected
  - Absent from `plan_listed` AND status is NOT `D` AND path matches a pattern in `conventions/SKILL.md: Incidental file patterns` AND path is not in any StepNode across any phase → `incidental` (logged in checkpoint under `Incidental files:`, NOT a failure)
  - Absent from `plan_listed` AND does not meet all incidental conditions → `unlisted` → Stage 1 FAIL
- Stage 1 PASS: all `actually_changed` paths are expected or incidental.

### V1 (PLAN_VERSION = 1)

Compile two lists: **Plan listed** — all files from this phase's `**Files in this phase:**` section in the plan; **Actually changed** — all files modified during this phase's steps.

Stage 1 PASS: all actually-changed files appear in plan-listed. Any unlisted file = Stage 1 FAIL.

## Stage 2: Code Quality

Stage 2 runs only after Stage 1 passes (same for both V2 and V1). Check:
- Code follows conventions from `.github/skills/conventions/SKILL.md`
- Tests test behaviour, not implementation details
- No obvious issues (missing error handling the spec required, wrong return types, etc.)

Stage 2 result is one line: PASS or FAIL with finding (what + where). No explanation, no suggestion.

**On failure (phased-subagent mode):** send the subagent back to fix. Re-run only Stage 2.
**On failure (phased-inline mode):** stop for engineer review before proceeding.

Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section. Stage 2 remains one line. No explanation, no suggestion in either.
```

- [ ] **Step 4: Create `github/protocols/phase-checkpoint.md`**

Source: checkpoint output templates from `github/skills/execution/SKILL.md` Steps 2b (lines 239–286) and 2c (lines 446–498). The two templates are identical except for the optional `Decisions & Assumptions:` field (subagent mode only). This protocol defines them once. Write this file exactly:

```markdown
# Protocol: Phase Checkpoint

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

---

Output this block exactly:

```
Phase [N] complete — [Phase name]

Files changed:
  + [file] (created)
  ~ [file] (modified)

[Stage 1] Spec compliance: PASS

Plan listed:
- <file1>
- <file2>

Actually changed:
- <file1>
- <file2>
OR
[Stage 1] Spec compliance: FAIL

Plan listed:
- <file1>

Actually changed:
- <file1>
- <fileX>

Unlisted:
- <fileX>

[Stage 2] Code quality: PASS
OR
[Stage 2] Code quality: FAIL — [finding: what + where]

Test output:
[pasted output]

Plan changes this phase:
- none OR
- [1-line summary of any ## Amendments entry tagged Phase [N] written during this phase]

[Decisions & Assumptions:
[bullets from sub-agent — or "None" if the sub-agent omitted the field]
(present in phased-subagent mode only — omit this block entirely in phased-inline mode)]

Review:
[exact questions from plan's Engineer review prompt for this phase]

Type `continue` for Phase [N+1], or describe a concern.
```

Rules:
- Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section.
- Stage 2 remains one line (PASS or FAIL with finding). No explanation, no suggestion in either.
- The `Decisions & Assumptions:` block is present only when the orchestrator is in phased-subagent mode and the subagent provided the field. Omit entirely in phased-inline mode or when the subagent omitted the field.
```

- [ ] **Step 5: Create `github/protocols/context-packet-load.md`**

Source: context packet check blocks from `github/skills/execution/SKILL.md` Steps 2a (lines 72–81), 2b (lines 217–221), and 2c (lines 337–343). All three copies are near-identical; minor variations are noted in Subagent note. Write this file exactly:

```markdown
# Protocol: Context Packet Load

**Purpose:** Load a pre-assembled context packet for a given ticket+phase, and declare the coverage-based access restrictions the caller must enforce.

**Inputs:** Ticket ID, phase number, context packets path (from conventions).

**Outputs:**
- Packet content (full file text, or a null signal if not found)
- Coverage confidence level: `high`, `medium`, or `low`
- Enforcement rules per level (declared in this protocol; applied by the caller)

**Non-goals:** Does not assemble the packet (context-packet skill responsibility). Does not perform code search (codebase-search protocol responsibility). Does not interpret the packet content — callers decide how to use it.

**Subagent note:** In phased-subagent mode (Step 2c), the caller embeds the packet content in the subagent prompt rather than applying enforcement in the parent session. The protocol's output (content + confidence + rules) is the same; usage differs by mode. The enforcement rules declared by this protocol apply inside the subagent.

---

1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-[N]-context.md`. For inline plans (Step 2a), try `phase-1` first, then `phase-2` if not found.
3. If found: read the full context packet. Note the `Coverage confidence` field. Enforcement rules per level:
   - `high`: **Prohibited** from reading files outside the context packet. If a step requires a file read outside the packet, stop and say: "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH. Should I expand context or rephrase the step to work within the packet?"
   - `medium`: Controlled one-hop expansion allowed — may read files referenced by packet modules; do not scan broadly.
   - `low`: Expansion required. The Codebase Search Protocol is available without restriction.
   Use `## Relevant Decisions` and `## Module Context` to frame understanding before touching any code.
4. If not found: treat as `low` coverage. Note: "No context packet found — proceeding with full codebase search." The Codebase Search Protocol is available without restriction.
```

- [ ] **Step 6: Verify all 5 protocol files exist**

Run: `ls github/protocols/`

Expected output (5 files):
```
codebase-search.md
context-packet-load.md
phase-checkpoint.md
stage-review.md
verification-gate.md
```

- [ ] **Step 7: Verify each protocol has Non-goals**

Run: `grep -l "Non-goals" github/protocols/*.md | wc -l`

Expected: `5`

- [ ] **Step 8: Commit**

```bash
git add github/protocols/
git commit -m "workflow-structural-clarity: add protocols/ directory with 5 extracted protocol files"
```

**Test after this phase:** N/A (no executable tests — verification is structural).

**Engineer review prompt:**
- Does each protocol file contain exactly Purpose, Inputs, Outputs, Non-goals, and protocol steps — no implementation logic beyond what was in the source skill?
- Does `stage-review.md` contain both `### V2 (PLAN_VERSION = 2)` and `### V1 (PLAN_VERSION = 1)` subsections under Stage 1?
- Does `phase-checkpoint.md` call out the `Decisions & Assumptions:` field as optional/subagent-only?

---

## Phase 2: Update `execution/SKILL.md`

**Files in this phase:**
- Modify: `github/skills/execution/SKILL.md`

This is the most invasive phase. Make each edit as a targeted find/replace. Read the current file before starting. Do not change any behavioral content — only structure and references.

> **Order matters:** Apply edits top-to-bottom in the file. Earlier edits shift line numbers for later edits.

- [ ] **Step 1: Read the current file**

Read `github/skills/execution/SKILL.md` in full. Confirm you see "Codebase Search Protocol" and "Verification Gate" sections, and the v1/v2 inline annotations like "(PLAN_VERSION = 2)".

- [ ] **Step 2: Add Non-goals to Metadata block**

Find this exact text:
```
- **Outputs:** Committed implementation code with a green full test suite; codebase ready for `/verify`
```

Replace with:
```
- **Outputs:** Committed implementation code with a green full test suite; codebase ready for `/verify`
- **Non-goals:** Does not verify spec completeness (verification skill's job); does not raise a PR; does not assemble context packets
```

- [ ] **Step 3: Reformat Step 1 version gate**

Find this exact text:
```
5. **Version detection:** Read the plan file's `schema_version` frontmatter. Store as PLAN_VERSION.
   - `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed paths throughout this skill.
   - Absent → PLAN_VERSION = 1. All existing paths apply unchanged.
   If PLAN_VERSION = 2: run `/validate-artifact [plan-path]` silently. BLOCK if validation fails.
```

Replace with:
```
5. **Version gate:** Read the plan file's `schema_version` frontmatter. Store as PLAN_VERSION.

### V2 (PLAN_VERSION = 2)
PLAN_VERSION = 2. Use v2 typed paths throughout this skill. Run `/validate-artifact [plan-path]` silently. BLOCK if validation fails.

### V1 (PLAN_VERSION = 1)
PLAN_VERSION = 1. All existing paths apply unchanged. No validation required.
```

- [ ] **Step 4: Isolate Step 1.5 into V2/V1 subsections**

Find this exact text:
```
## Step 1.5: Context Packet Auto-Trigger (PLAN_VERSION = 2 only)

For each phase about to execute, before any step runs, check both conditions:
1. `plan.execution.mode` = `'phased-inline'` or `'phased-subagent'`
2. Total FileRef count across `phases[*].id=N .steps[*].files` ≥ 4

If both hold: silently invoke the context-packet skill for this phase (do not ask the engineer — run it as an internal step). Announce the result: "Context packet auto-triggered for Phase [N]: [N] files across [N] modules. Coverage: [level]."

If conditions are not met (inline mode, or < 4 files): announce: "Phase [N]: [N] file(s) — below auto-trigger threshold. Proceeding with codebase search protocol."

For PLAN_VERSION = 1: no change — context packet is triggered manually via `/context-packet` command.
```

Replace with:
```
## Step 1.5: Context Packet Auto-Trigger

### V2 (PLAN_VERSION = 2)
For each phase about to execute, before any step runs, check both conditions:
1. `plan.execution.mode` = `'phased-inline'` or `'phased-subagent'`
2. Total FileRef count across `phases[*].id=N .steps[*].files` ≥ 4

If both hold: silently invoke the context-packet skill for this phase (do not ask the engineer — run it as an internal step). Announce the result: "Context packet auto-triggered for Phase [N]: [N] files across [N] modules. Coverage: [level]."

If conditions are not met (inline mode, or < 4 files): announce: "Phase [N]: [N] file(s) — below auto-trigger threshold. Proceeding with codebase search protocol."

### V1 (PLAN_VERSION = 1)
Not applicable — skip this step. Context packet is triggered manually via `/context-packet` command.
```

- [ ] **Step 5: Replace Step 2a context packet check with protocol reference**

Find this exact text:
```
**Context packet check (run before any steps):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-1-context.md` (inline plans use a single phase; try `phase-1` first, then `phase-2` if not found).
3. If found: read the full context packet. Note the `Coverage confidence` field. Enforce based on level:
   - `high`: **Prohibited** from reading files outside the context packet. If a step requires a file read outside the packet, stop and say: "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH. Should I expand context or rephrase the step to work within the packet?"
   - `medium`: Controlled one-hop expansion allowed — may read files referenced by packet modules; do not scan broadly.
   - `low`: Expansion required. The Codebase Search Protocol is available without restriction.
   Use `## Relevant Decisions` and `## Module Context` to frame understanding before touching any code.
4. If not found: treat as `low` coverage. Note: "No context packet found — proceeding with full codebase search." The Codebase Search Protocol is available without restriction.
```

Replace with:
```
**Context packet check (run before any steps):**
Read `.github/protocols/context-packet-load.md` and follow it exactly.
```

- [ ] **Step 6: Isolate Step 2a amendment tracking into V2/V1 subsections**

Find this exact text:
```
2a. **V2 only (PLAN_VERSION = 2):** When a step's verify command passes, append a `step-completed` amendment to the plan file's `amendments:` YAML array. Set `id: A{N}` where N = count of existing amendments + 1 (first amendment is A1; numbers never reused). Example:
    ```yaml
    - id: "A3"
      step_id: "P1.S2"
      phase: 1
      type: step-completed
      description: "Write TokenValidator class — verify passed: 3 tests, 0 failures"
      added_by: execution
    ```
```

Replace with:
```
**Amendment tracking:**

### V2 (PLAN_VERSION = 2)
When a step's verify command passes, append a `step-completed` amendment to the plan file's `amendments:` YAML array. Set `id: A{N}` where N = count of existing amendments + 1 (first amendment is A1; numbers never reused). Example:
```yaml
- id: "A3"
  step_id: "P1.S2"
  phase: 1
  type: step-completed
  description: "Write TokenValidator class — verify passed: 3 tests, 0 failures"
  added_by: execution
```

### V1 (PLAN_VERSION = 1)
Not applicable — skip this step.
```

- [ ] **Step 7: Replace Codebase Search Protocol section with reference**

Find this exact text (the entire section, from the section heading through the last sentence):
```
## Codebase Search Protocol

When you need to find existing code before implementing a step — understanding a class, finding where a behavior is handled, locating a configuration value:

**Step 0: Knowledge state check (run before every module exploration):**
Identify the module name for the file or area you are about to explore. Then evaluate in order — first match wins:

1. Context packet is loaded AND this module appears explicitly by name in `## Module Context` → **no signal** — proceed directly to step 1. (Exact name match only — do not infer coverage.)
2. `[KNOWLEDGE_PATH]/[module].md` exists → emit, then proceed to step 1:
   ```
   Context reuse signal:
   This module has prior structured knowledge:
   - <1-line summary from the file's ## Summary section>
   ```
3. Neither condition above is met → emit, then proceed to step 1:
   ```
   Context reuse signal:
   No prior structured knowledge available for this module.
   This exploration is not reusable unless captured in the knowledge system.
   ```

Signal is informational only — never blocks execution. Emit one signal (or none) per module per exploration.

1. **Formulate a specific query**: name exactly what you're looking for. Bad: "find auth code". Good: "UserAuthService class" or "JWT token validation method".
2. **Run `semantic_search`** with the specific query.
3. **If a relevant result appears in the first page**: use it and stop.
4. **If zero results or all irrelevant**: try once more with a synonym or the exact class/method name as a literal string. Maximum 2 `semantic_search` calls per question.
5. **Fallback after 2 failed searches**: use `grep_search` with the exact class name, method name, or unique constant.
6. **Stop when found**: do not continue searching once you have what you need for the current step.

Apply this protocol any time a step requires understanding existing code before modifying it.
```

Replace with:
```
## Codebase Search Protocol

Read `.github/protocols/codebase-search.md` and follow it exactly.
```

- [ ] **Step 8: Replace Verification Gate section with reference**

Find this exact text:
```
### Verification Gate

Before claiming any of these: "step complete", "phase complete", "all tests pass", "full suite green" — run this gate:

1. **IDENTIFY:** What exact command proves the claim?
2. **RUN:** Execute it now — fresh execution, not cached output.
3. **READ:** Read the full output including exit code.
4. **CLAIM:** State the claim with the pasted evidence.

Reject these: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.
```

Replace with:
```
### Verification Gate

Read `.github/protocols/verification-gate.md` and follow it exactly.
```

- [ ] **Step 9: Replace Step 2b context packet check with reference**

Find this exact text (in Step 2b):
```
**Context packet check (before each phase):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: load it. Enforce coverage confidence behavior (see Step 1b).
4. If not found: treat as `low` confidence. Note: "No context packet for phase [N]. Proceeding with full codebase search."
```

Replace with:
```
**Context packet check (before each phase):**
Read `.github/protocols/context-packet-load.md` and follow it exactly.
```

- [ ] **Step 10: Replace Step 2b Stage 1 + checkpoint with protocol references**

Find this exact text (the two-stage review + checkpoint template in Step 2b):
```
**Run two-stage review** (same as Step 2c sub-agent review below) before showing the checkpoint.

**Stage 1 — Spec compliance:**

**V2 (PLAN_VERSION = 2):**
- `plan_listed` = all `files[*].path` values from `phases[*].id=N .steps[*].files` (typed array, no text parsing)
- `actually_changed` = paths in `git diff --name-status HEAD~1` with status `A` (added), `M` (modified), or `R` (renamed). Paths with status `D` (deleted): check these against plan_listed separately — a `D` path not in plan_listed and not covered by a `step-removed` amendment = Stage 1 FAIL.
- Classify each path in `actually_changed`:
  - Present in `plan_listed` → expected
  - Absent from `plan_listed` AND status is NOT `D` AND path matches a pattern in `conventions/SKILL.md: Incidental file patterns` AND path is not in any StepNode across any phase → `incidental` (logged in checkpoint under `Incidental files:`, NOT a failure)
  - Absent from `plan_listed` AND does not meet all incidental conditions → `unlisted` → Stage 1 FAIL
- Stage 1 PASS: all `actually_changed` paths are expected or incidental.

**V1 (PLAN_VERSION = 1):** Compile two lists: **Plan listed** — all files from this phase's `**Files in this phase:**` section in the plan; **Actually changed** — all files modified during this phase's steps.

**Phase checkpoint (show after both stages pass):**
```
Phase [N] complete — [Phase name]

Files changed:
  + [file] (created)
  ~ [file] (modified)

[Stage 1] Spec compliance: PASS

Plan listed:
- <file1>
- <file2>

Actually changed:
- <file1>
- <file2>
OR
[Stage 1] Spec compliance: FAIL

Plan listed:
- <file1>

Actually changed:
- <file1>
- <fileX>

Unlisted:
- <fileX>

[Stage 2] Code quality: PASS
OR
[Stage 2] Code quality: FAIL — [finding: what + where]

Test output:
[pasted output]

Plan changes this phase:
- none OR
- [1-line summary of any ## Amendments entry tagged Phase [N] written during this phase]

Review:
[exact questions from plan's Engineer review prompt for this phase]

Type `continue` for Phase [N+1], or describe a concern.
```

Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section. Stage 2 remains one line (PASS or FAIL with finding). No explanation, no suggestion in either.
```

Replace with:
```
**Run stage review:**
Read `.github/protocols/stage-review.md` and follow it exactly. Use the loaded plan's PLAN_VERSION (stored in Step 1) to select the correct version block.

**Present the phase checkpoint:**
Read `.github/protocols/phase-checkpoint.md` and follow it exactly. Omit the `Decisions & Assumptions:` field (phased-inline mode — that field is subagent-only).
```

- [ ] **Step 11: Replace Step 2c context packet check with reference**

Find this exact text (in Step 2c dispatch section):
```
**Before dispatching — context packet check:**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: copy the full file content for embedding in the subagent prompt (CONTEXT_PACKET_CONTENT).
4. If not found: set CONTEXT_PACKET_CONTENT = `No context packet available. Use the Codebase Search Protocol for any module lookups during this phase.`
```

Replace with:
```
**Before dispatching — context packet check:**
Read `.github/protocols/context-packet-load.md` and follow it. In phased-subagent mode: instead of applying enforcement in the parent session, capture CONTEXT_PACKET_CONTENT for embedding in the subagent prompt. If no packet found: set CONTEXT_PACKET_CONTENT = `No context packet available. Use the Codebase Search Protocol for any module lookups during this phase.`
```

- [ ] **Step 12: Isolate Step 2c conventions injection into V2/V1 subsections**

Find this exact text:
```
**Before building the sub-agent prompt — conventions injection:**

**V2 (PLAN_VERSION = 2) — lean injection from risk_signals[]:**

```
Fixed (always injected):
  test_command   ← conventions.Test command
  commit_format  ← conventions.Commit Message Format
  lint_command   ← conventions.Lint command (or "none")

Risk-signal sections (per phase):
  For each signal ∈ union of step.risk_signals[] across all steps in this phase:
    → exact header match against conventions section headers (case-insensitive)
    → include matched section; skip silently if no match found
```

No step-text scan. `StepNode.risk_signals[]` is the sole injection signal source.

**V1 (PLAN_VERSION = 1) — keyword text-scan:**
Scan each step's text for keyword patterns (error/exception/validate → `## Error Handling`; endpoint/request/API → `## API Conventions`; migration/schema/database → `## Data Conventions`; exact framework name match → that section). If `conventions/SKILL.md` does not contain a matching section: no injection.
```

Replace with:
```
**Before building the sub-agent prompt — conventions injection:**

### V2 (PLAN_VERSION = 2)
Lean injection from risk_signals[]:

```
Fixed (always injected):
  test_command   ← conventions.Test command
  commit_format  ← conventions.Commit Message Format
  lint_command   ← conventions.Lint command (or "none")

Risk-signal sections (per phase):
  For each signal ∈ union of step.risk_signals[] across all steps in this phase:
    → exact header match against conventions section headers (case-insensitive)
    → include matched section; skip silently if no match found
```

No step-text scan. `StepNode.risk_signals[]` is the sole injection signal source.

### V1 (PLAN_VERSION = 1)
Keyword text-scan: scan each step's text for keyword patterns (error/exception/validate → `## Error Handling`; endpoint/request/API → `## API Conventions`; migration/schema/database → `## Data Conventions`; exact framework name match → that section). If `conventions/SKILL.md` does not contain a matching section: no injection.
```

- [ ] **Step 13: Replace Step 2c Stage 1/2 review + checkpoint with protocol references**

Find this exact text (Step 2c two-stage review + checkpoint):
```
### Present the review checkpoint

After the subagent returns, run a two-stage review before presenting to the engineer.

**Stage 1: Spec Compliance**
Compile two lists from the sub-agent's return:
- **Plan listed** — all files from the `FILES TO CHANGE IN THIS PHASE:` section of the dispatch prompt
- **Actually changed** — all files the sub-agent reports changing in its return output

Check:
- Implementation matches plan steps — every listed step was executed
- All listed files were changed
- No unlisted files were changed

If Stage 1 fails: send the subagent back to fix. Re-run Stage 1 before proceeding.

**Stage 2: Code Quality**
Only runs after Stage 1 passes. Check:
- Code follows conventions from `.github/skills/conventions/SKILL.md`
- Tests test behaviour, not implementation details
- No obvious issues (missing error handling the spec required, wrong return types, etc.)

If Stage 2 fails: send the subagent back to fix. Re-run only Stage 2.

**After both stages pass**, show the engineer:

```
Phase [N] complete — [Phase name]

Files changed:
  + [file1] (created)
  ~ [file2] (modified)

[Stage 1] Spec compliance: PASS

Plan listed:
- <file1>
- <file2>

Actually changed:
- <file1>
- <file2>
OR
[Stage 1] Spec compliance: FAIL

Plan listed:
- <file1>

Actually changed:
- <file1>
- <fileX>

Unlisted:
- <fileX>

[Stage 2] Code quality: PASS
OR
[Stage 2] Code quality: FAIL — [finding: what + where]

Test output:
[Paste full output from subagent — do not summarise]

Plan changes this phase:
- none OR
- [1-line summary of any ## Amendments entry tagged Phase [N] in the sub-agent's return]

Decisions & Assumptions:
[bullets from sub-agent — or "None" if the sub-agent omitted the field]

Review:
[Copy the exact "Engineer review prompt" text from the plan for this phase]

Type `continue` for Phase [N+1], or describe a concern.
```

Stage 1 always shows Plan listed and Actually changed. On PASS, the lists match. On FAIL, include the Unlisted section. Stage 2 remains one line (PASS or FAIL with finding). No explanation, no suggestion in either.
```

Replace with:
```
### Present the review checkpoint

After the subagent returns, run stage review: read `.github/protocols/stage-review.md` and follow it exactly. Use the loaded plan's PLAN_VERSION (stored in Step 1) to select the correct version block.

If Stage 1 fails: send the subagent back to fix. Re-run Stage 1 before proceeding.
If Stage 2 fails: send the subagent back to fix. Re-run only Stage 2.

**After both stages pass**, present the phase checkpoint: read `.github/protocols/phase-checkpoint.md` and follow it exactly. Include the `Decisions & Assumptions:` field (sourced from the subagent's return — write "None" if the subagent omitted the field).
```

- [ ] **Step 14: Verify execution/SKILL.md — no embedded protocol logic remains**

Run: `grep -n "PLAN_VERSION" github/skills/execution/SKILL.md`

Expected: lines containing only `### V2 (PLAN_VERSION = 2)` or `### V1 (PLAN_VERSION = 1)` — no inline `(PLAN_VERSION = 2 only)` annotations mid-sentence.

Run: `grep -c "protocols/" github/skills/execution/SKILL.md`

Expected: at least `6` (one reference per call site for each of the 5 protocols, with context-packet-load referenced 3×).

- [ ] **Step 15: Commit**

```bash
git add github/skills/execution/SKILL.md
git commit -m "workflow-structural-clarity: refactor execution/SKILL.md — protocol references + v1/v2 isolation"
```

**Test after this phase:** N/A (structural verification only).

**Engineer review prompt:**
- Do all 5 protocol references (`codebase-search.md`, `verification-gate.md`, `stage-review.md`, `phase-checkpoint.md`, `context-packet-load.md`) appear in `execution/SKILL.md`?
- Are there any remaining inline `(PLAN_VERSION = 2 only)` annotations that were not converted to `### V2` / `### V1` subsections?
- Does the Non-goals line appear in the `## Metadata` block?
- Is the embedded Stage 1 v1/v2 fork completely removed from both Step 2b and Step 2c (it now lives only in `stage-review.md`)?

---

## Phase 3: Update `context-packet/SKILL.md`

**Files in this phase:**
- Modify: `github/skills/context-packet/SKILL.md`

- [ ] **Step 1: Read the current file**

Read `github/skills/context-packet/SKILL.md` in full. Confirm you see the inline `**V2 (PLAN_VERSION = 2):**` / `**V1 (PLAN_VERSION = 1):**` annotations in Steps 2, 3, 6.5, and 7.

- [ ] **Step 2: Add Non-goals to Metadata block**

Find this exact text:
```
- **Outputs:** `[context-packets-path]/[ticket-id]/phase-[N]-context.md`
```

Replace with:
```
- **Outputs:** `[context-packets-path]/[ticket-id]/phase-[N]-context.md`
- **Non-goals:** Does not write code; does not modify plans or specs; does not build the codebase or knowledge index
```

- [ ] **Step 3: Reformat Step 1 version detection as explicit gate block**

Find this exact text:
```
**Version detection:** After reading the plan file, check its `schema_version` frontmatter. Store as PLAN_VERSION.
- `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed-field paths in Steps 2, 3, 6.5, and 7.
- Absent → PLAN_VERSION = 1. Use existing prose extraction paths.
```

Replace with:
```
**Version gate:** After reading the plan file, check its `schema_version` frontmatter. Store as PLAN_VERSION.

### V2 (PLAN_VERSION = 2)
PLAN_VERSION = 2. Use v2 typed-field paths in Steps 2, 3, 6.5, and 7.

### V1 (PLAN_VERSION = 1)
PLAN_VERSION = 1. Use existing prose extraction paths.
```

- [ ] **Step 4: Isolate Step 2 phase file count into V2/V1 subsections**

Find this exact text:
```
3. **Phase file count:**
   - **V2 (PLAN_VERSION = 2):** Locate the phase entry where `phases[*].id = N`. Count total `FileRef` entries across `phases[N-1].steps[*].files` (all steps in that phase).
   - **V1 (PLAN_VERSION = 1):** Find the section `## Phase [N]:` and count files listed in its `**Files in this phase:**` block.
   Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."
```

Replace with:
```
3. **Phase file count:**

### V2 (PLAN_VERSION = 2)
Locate the phase entry where `phases[*].id = N`. Count total `FileRef` entries across `phases[N-1].steps[*].files` (all steps in that phase).
Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."

### V1 (PLAN_VERSION = 1)
Find the section `## Phase [N]:` and count files listed in its `**Files in this phase:**` block.
Are there ≥ 4 files? If < 4 → stop: "Phase [N] has [count] files. Context packets are generated for phases with ≥ 4 files only."
```

- [ ] **Step 5: Isolate Step 3 phase file manifest into V2/V1 subsections**

Find this exact text:
```
**V2 (PLAN_VERSION = 2):** Read `phases[*].id = N` entry. Collect all `steps[*].files[*].path` values across every step in that phase. Exclude paths where `operation: 'delete'` (deleted files have no module context to load). Store as PHASE_FILES. No text parsing required.

**V1 (PLAN_VERSION = 1):** From the plan's phase section, extract the exact list of files listed under `**Files in this phase:**`. Store as PHASE_FILES.
```

Replace with:
```
### V2 (PLAN_VERSION = 2)
Read `phases[*].id = N` entry. Collect all `steps[*].files[*].path` values across every step in that phase. Exclude paths where `operation: 'delete'` (deleted files have no module context to load). Store as PHASE_FILES. No text parsing required.

### V1 (PLAN_VERSION = 1)
From the plan's phase section, extract the exact list of files listed under `**Files in this phase:**`. Store as PHASE_FILES.
```

- [ ] **Step 6: Isolate Step 6.5 into V2/V1 subsections**

Find this exact text:
```
## Step 6.5: Select Decisions for Context Packet (PLAN_VERSION = 2 only)

Compute the set of decisions to include in `## Relevant Decisions`:

```
phase_req_ids  = union of step.requirement_ids for all steps where phases[*].id = N
decision_ids_A = { req.source_decision
                   for req in requirements
                   where req.id ∈ phase_req_ids AND req.source_decision != null }
decision_ids_B = { d.id for d in decisions where d.reversibility = 'low' }
included       = decisions where id ∈ (decision_ids_A ∪ decision_ids_B)
```

Store as SELECTED_DECISIONS. Skip entirely for PLAN_VERSION = 1 (all decisions from loaded module pages apply, existing behavior).
```

Replace with:
```
## Step 6.5: Select Decisions for Context Packet

### V2 (PLAN_VERSION = 2)
Compute the set of decisions to include in `## Relevant Decisions`:

```
phase_req_ids  = union of step.requirement_ids for all steps where phases[*].id = N
decision_ids_A = { req.source_decision
                   for req in requirements
                   where req.id ∈ phase_req_ids AND req.source_decision != null }
decision_ids_B = { d.id for d in decisions where d.reversibility = 'low' }
included       = decisions where id ∈ (decision_ids_A ∪ decision_ids_B)
```

Store as SELECTED_DECISIONS.

### V1 (PLAN_VERSION = 1)
Not applicable — skip this step. All decisions from loaded module pages apply (existing behavior).
```

- [ ] **Step 7: Isolate Step 7 coverage confidence into V2/V1 subsections**

Find this exact text:
```
**V2 (PLAN_VERSION = 2):** Apply the typed formula:

```
all_files  = all FileRef entries in phases[*].id=N steps
none_count = count of f in all_files where file-to-module mapping = UNKNOWN
total      = count of all_files

if none_count / total > 0.5  → CONFIDENCE = 'low'
if none_count > 0            → CONFIDENCE = 'medium'
else                         → CONFIDENCE = 'high'
```

**File path → module mapping rule (v2 only):**
```
candidates(path) = { m for m in codebase_index.modules
                       where any source_path ∈ m.source_paths is a prefix of path }

resolve(path):
  |candidates| = 1  → use that module
  |candidates| = 0  → UNKNOWN
  |candidates| > 1  → longest matching prefix wins;
                      tie → higher Reach score wins;
                      tie → alphabetically first module name (deterministic)
```

**V1 (PLAN_VERSION = 1):** Use existing rules (first match wins: unresolved majority → low, stale index → low, index age > 30 days → low, one or more unresolved → medium, all resolved + index ≤ 7 days + not stale → high).
```

Replace with:
```
### V2 (PLAN_VERSION = 2)
Apply the typed formula:

```
all_files  = all FileRef entries in phases[*].id=N steps
none_count = count of f in all_files where file-to-module mapping = UNKNOWN
total      = count of all_files

if none_count / total > 0.5  → CONFIDENCE = 'low'
if none_count > 0            → CONFIDENCE = 'medium'
else                         → CONFIDENCE = 'high'
```

**File path → module mapping rule (v2 only):**
```
candidates(path) = { m for m in codebase_index.modules
                       where any source_path ∈ m.source_paths is a prefix of path }

resolve(path):
  |candidates| = 1  → use that module
  |candidates| = 0  → UNKNOWN
  |candidates| > 1  → longest matching prefix wins;
                      tie → higher Reach score wins;
                      tie → alphabetically first module name (deterministic)
```

### V1 (PLAN_VERSION = 1)
Use existing rules (first match wins: unresolved majority → low, stale index → low, index age > 30 days → low, one or more unresolved → medium, all resolved + index ≤ 7 days + not stale → high).
```

- [ ] **Step 8: Verify — no inline V2/V1 annotations remain**

Run: `grep -n "PLAN_VERSION = 2):" github/skills/context-packet/SKILL.md`

Expected: zero results (all remaining `PLAN_VERSION` references should be inside `### V2` / `### V1` section headers only).

- [ ] **Step 9: Commit**

```bash
git add github/skills/context-packet/SKILL.md
git commit -m "workflow-structural-clarity: context-packet/SKILL.md — v1/v2 isolation + Non-goals"
```

**Engineer review prompt:**
- Does the `## Metadata` block contain the `Non-goals:` line?
- Does each of the 5 v1/v2 locations now have `### V2 (PLAN_VERSION = 2)` and `### V1 (PLAN_VERSION = 1)` subsections?
- Is the explicit `Not applicable — skip this step.` present under `### V1` in Step 6.5?

---

## Phase 4: Update `planning/SKILL.md`

**Files in this phase:**
- Modify: `github/skills/planning/SKILL.md`

- [ ] **Step 1: Read the current file**

Read `github/skills/planning/SKILL.md` in full. Confirm you see the inline `**V2 (SPEC_VERSION = 2):**` annotations in Intelligence Retrieval, Version Gate, Plan Structure, and Cross-Repo Injection sections.

- [ ] **Step 2: Add Non-goals to Metadata block**

Find this exact text:
```
- **Outputs:** Plan file at `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`
```

Replace with:
```
- **Outputs:** Plan file at `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`
- **Non-goals:** Does not write code; does not execute steps; does not validate spec against test evidence
```

- [ ] **Step 3: Reformat Version Gate section**

Find this exact text:
```
## Version Gate (run before any other step)

Read the spec file's `schema_version` frontmatter. Store as SPEC_VERSION.

- **`schema_version: 2`:** run `/validate-artifact [spec-path] [brainstorm-path]` silently (includes immutability check against brainstorm source). BLOCK if validation fails. Use v2 typed-field paths throughout this skill.
- **Absent or other:** SPEC_VERSION = 1. Use existing prose extraction throughout. Version gates do not apply.
```

Replace with:
```
## Version Gate (run before any other step)

Read the spec file's `schema_version` frontmatter. Store as SPEC_VERSION.

### V2 (SPEC_VERSION = 2)
Run `/validate-artifact [spec-path] [brainstorm-path]` silently (includes immutability check against brainstorm source). BLOCK if validation fails. Use v2 typed-field paths throughout this skill.

### V1 (SPEC_VERSION = 1 or absent)
SPEC_VERSION = 1. Use existing prose extraction throughout. Version gates do not apply.
```

- [ ] **Step 4: Isolate Intelligence Retrieval spec classification into V2/V1 subsections**

Find this exact text:
```
3. **V2 (SPEC_VERSION = 2):** Read `problem.classification` from the spec artifact as a typed field. Pass it directly to the retrieval protocol's classification parameter — no prose inference:
   - `new-feature` → retrieval priority: system › empirical › external
   - `modification` or `bug-fix` → retrieval priority: empirical › system › external
   d. **Decision Conflict Check:**
      - **V2 (SPEC_VERSION = 2):** Read `decisions[*].constraints[]` typed array from the spec artifact. Compare each constraint against `## Known Constraints` sections in loaded module pages. Flag where a spec constraint directly contradicts a module constraint.
      - **V1 (SPEC_VERSION = 1):** Read `## Decisions` from every loaded module page; compare against the spec's `## Architecture / Design Decisions` prose.
      Note (both versions): module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.
```

Replace with:
```
3. **Spec classification:**

### V2 (SPEC_VERSION = 2)
Read `problem.classification` from the spec artifact as a typed field. Pass it directly to the retrieval protocol's classification parameter — no prose inference:
- `new-feature` → retrieval priority: system › empirical › external
- `modification` or `bug-fix` → retrieval priority: empirical › system › external

### V1 (SPEC_VERSION = 1)
Not applicable — skip this step. Retrieval priority uses default ordering.

   d. **Decision Conflict Check:**

### V2 (SPEC_VERSION = 2)
Read `decisions[*].constraints[]` typed array from the spec artifact. Compare each constraint against `## Known Constraints` sections in loaded module pages. Flag where a spec constraint directly contradicts a module constraint.

Note: module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.

### V1 (SPEC_VERSION = 1)
Read `## Decisions` from every loaded module page; compare against the spec's `## Architecture / Design Decisions` prose.

Note: module pages are v1 prose. This check remains partially deterministic (typed spec input vs. prose module pages) until module pages adopt v2 typed decisions — acknowledged limitation in the design spec.
```

- [ ] **Step 5: Isolate Plan Structure output templates into V2/V1 subsections**

Find this exact text:
```
**V2 output template (SPEC_VERSION = 2):** Use this YAML PlanArtifact instead of the v1 Markdown template above. Carry all spec fields verbatim — do not re-derive.
```

Replace with:
```
### V2 (SPEC_VERSION = 2)
Use this YAML PlanArtifact instead of the V1 Markdown template above. Carry all spec fields verbatim — do not re-derive.
```

Then find the text immediately before the v1 template (the `## Plan Structure` section heading and prose up to the first code fence):

Find this exact text:
```
## Plan Structure

~~~markdown
```

Replace with:
```
## Plan Structure

### V1 (SPEC_VERSION = 1)

~~~markdown
```

- [ ] **Step 6: Isolate Cross-Repo Auto-Risk-Signal Injection into V2/V1 subsections**

Find this exact text:
```
## Cross-Repo Auto-Risk-Signal Injection (SPEC_VERSION = 2 only — runs after all StepNodes written)

If `[knowledge-path]/imports.md` exists and is readable, run once before writing the plan artifact:
```

Replace with:
```
## Cross-Repo Auto-Risk-Signal Injection

### V2 (SPEC_VERSION = 2)
If `[knowledge-path]/imports.md` exists and is readable, run once before writing the plan artifact:
```

Then find the last paragraph of the section:

Find this exact text:
```
- Injection is visible in the written plan artifact. Engineer may remove false-positive entries before approving.
- Only runs for SPEC_VERSION = 2. V1 planning is unchanged.
```

Replace with:
```
- Injection is visible in the written plan artifact. Engineer may remove false-positive entries before approving.

### V1 (SPEC_VERSION = 1)
Not applicable — skip this step.
```

- [ ] **Step 7: Verify — no inline V2/V1 annotations remain**

Run: `grep -n "SPEC_VERSION = 2):" github/skills/planning/SKILL.md`

Expected: zero results.

Run: `grep -n "Non-goals" github/skills/planning/SKILL.md`

Expected: at least `1` result in the Metadata block.

- [ ] **Step 8: Commit**

```bash
git add github/skills/planning/SKILL.md
git commit -m "workflow-structural-clarity: planning/SKILL.md — v1/v2 isolation + Non-goals"
```

**Engineer review prompt:**
- Does the `## Metadata` block contain the `Non-goals:` line?
- Does the `## Version Gate` section have `### V2` and `### V1` subsections?
- Does `## Plan Structure` now have a `### V1 (SPEC_VERSION = 1)` subsection header before the v1 template, and a `### V2 (SPEC_VERSION = 2)` subsection header before the YAML template?
- Does `## Cross-Repo Auto-Risk-Signal Injection` now have `### V2` and `### V1: Not applicable` subsections?

---

## Phase 5: Add Non-goals to Remaining 12 Skills

**Files in this phase:**
- Modify: `github/skills/setup/SKILL.md`
- Modify: `github/skills/brainstorming/SKILL.md`
- Modify: `github/skills/spec-writing/SKILL.md`
- Modify: `github/skills/verification/SKILL.md`
- Modify: `github/skills/review/SKILL.md`
- Modify: `github/skills/debugging/SKILL.md`
- Modify: `github/skills/tdd/SKILL.md`
- Modify: `github/skills/index-codebase/SKILL.md`
- Modify: `github/skills/index-knowledge/SKILL.md`
- Modify: `github/skills/validate-artifact/SKILL.md`
- Modify: `github/skills/retrieval-protocol/SKILL.md`
- Modify: `github/skills/cross-repo/SKILL.md`

> Each edit is a one-line insertion into the skill's `## Metadata` block. Find the `- **Outputs:**` line in each skill and insert the `- **Non-goals:**` line immediately after it. If a skill has no `- **Outputs:**` line, insert after `- **Inputs:**`.

- [ ] **Step 1: Add Non-goals to setup/SKILL.md**

Find:
```
- **Outputs:** `.github/skills/conventions/SKILL.md` fully populated with no placeholder text
```
Add after:
```
- **Non-goals:** Does not create plans, specs, or workflow artifacts; does not run tests; does not modify source files
```

- [ ] **Step 2: Add Non-goals to brainstorming/SKILL.md**

Find:
```
- **Outputs:** A brainstorm artifact file saved to `[brainstorms-path]/YYYY-MM-DD-[ticket-id]-brainstorm.md`
```
Add after:
```
- **Non-goals:** Does not write specs or plans; does not make implementation decisions; does not read the codebase
```

- [ ] **Step 3: Add Non-goals to spec-writing/SKILL.md**

Find:
```
- **Outputs:** Spec file at `[specs-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`
```
Add after:
```
- **Non-goals:** Does not read the codebase; does not create implementation steps; does not produce a plan
```

- [ ] **Step 4: Add Non-goals to verification/SKILL.md**

Read `github/skills/verification/SKILL.md` first to locate the `## Metadata` Outputs line. Then add after the Outputs line:
```
- **Non-goals:** Does not fix failures; does not write new tests; does not raise a PR
```

- [ ] **Step 5: Add Non-goals to review/SKILL.md**

Find:
```
- **Outputs:** A BLOCKER/SUGGESTION list, or "No blockers. Raise your PR." if clean
```
Add after:
```
- **Non-goals:** Does not modify code; does not approve or raise PRs; does not re-run tests
```

- [ ] **Step 6: Add Non-goals to debugging/SKILL.md**

Find:
```
- **Outputs:** Root cause identified + minimal fix applied + failing test now passing + no new regressions
```
Add after:
```
- **Non-goals:** Does not write new features; does not fix without root cause identification first
```

- [ ] **Step 7: Add Non-goals to tdd/SKILL.md**

Find:
```
- **Outputs:** A passing test + minimal implementation + clean refactored code, with no regressions
```
Add after:
```
- **Non-goals:** Does not apply to config or infrastructure files without testable behavior; does not write production code before a failing test
```

- [ ] **Step 8: Add Non-goals to index-codebase/SKILL.md**

Find:
```
- **Outputs:** `[codebase-index-path]/index.md` and `[codebase-index-path]/[module].md` per module
```
Add after:
```
- **Non-goals:** Does not modify source files or workflow artifacts; does not extract knowledge signals (index-knowledge's job)
```

- [ ] **Step 9: Add Non-goals to index-knowledge/SKILL.md**

Find:
```
- **Outputs:** `[knowledge-index-path]/index.md`, `[knowledge-index-path]/[topic].md` per topic, and updated `## Known Constraints` / `## Decisions` sections in module pages
```
Add after:
```
- **Non-goals:** Does not modify source files; does not rebuild the codebase index (index-codebase's job); does not resolve contradictions automatically
```

- [ ] **Step 10: Add Non-goals to validate-artifact/SKILL.md**

Find:
```
- **Outputs:** `PASS` (silent when invoked internally) or itemized `FAIL` list with field paths.
```
Add after:
```
- **Non-goals:** Does not validate v1 artifacts; does not perform semantic checks; does not auto-fix failures
```

- [ ] **Step 11: Add Non-goals to retrieval-protocol/SKILL.md**

Find:
```
- **Outputs:** A retrieval summary block (`## Intelligence Context`) and a set of loaded module/knowledge pages for use during planning
```
Add after:
```
- **Non-goals:** Does not run during brainstorm, spec, execution, or review phases; does not write any files
```

- [ ] **Step 12: Add Non-goals to cross-repo/SKILL.md**

Find the `## Metadata` block. After the last existing Metadata field (the file has `- **Phase:**` and `- **Inputs:**` and `- **Outputs:**`), add:
```
- **Non-goals:** Does not generate exports.md or imports.md automatically; does not enforce cross-repo contracts at execution time
```

- [ ] **Step 13: Verify all 12 skills have Non-goals**

Run: `grep -rl "Non-goals" github/skills/ | wc -l`

Expected: `15` (12 from this phase + 3 from phases 2–4).

- [ ] **Step 14: Commit**

```bash
git add github/skills/setup/SKILL.md github/skills/brainstorming/SKILL.md github/skills/spec-writing/SKILL.md github/skills/verification/SKILL.md github/skills/review/SKILL.md github/skills/debugging/SKILL.md github/skills/tdd/SKILL.md github/skills/index-codebase/SKILL.md github/skills/index-knowledge/SKILL.md github/skills/validate-artifact/SKILL.md github/skills/retrieval-protocol/SKILL.md github/skills/cross-repo/SKILL.md
git commit -m "workflow-structural-clarity: add Non-goals to all remaining skill Metadata blocks"
```

**Engineer review prompt:**
- Does `grep -rl "Non-goals" github/skills/ | wc -l` return exactly `15`?
- For each skill, is the `Non-goals:` line in the `## Metadata` block (not in any other section)?

---

## Phase 6: Update `copilot-instructions.md`

**Files in this phase:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Read the current file**

Read `github/copilot-instructions.md` in full. Confirm you see the Priority Order list (4 items), Drift Control (rules 1–6), and Conscious Skip Protocol.

- [ ] **Step 2: Add Drift Control rule 7**

Find this exact text:
```
6. Read relevant existing code before suggesting or making modifications
```

Replace with:
```
6. Read relevant existing code before suggesting or making modifications
7. Stay within phase scope — do not implement, refactor, or plan across multiple phases in a single response
```

- [ ] **Step 3: Add Priority Order note**

Find this exact text:
```
4. These instructions
```

Replace with:
```
4. These instructions

Note: phase-specific procedures are defined in the skill file for the active phase and take precedence over general behavior patterns described in these instructions.
```

- [ ] **Step 4: Tighten Conscious Skip Protocol**

Find this exact text:
```
3. Continue — this is a conscious override, not the default path
```

Replace with:
```
3. Continue — this is a conscious override, not the default path

Skipping a phase does not expand the current phase's scope — complete only the work defined for the active phase.
```

- [ ] **Step 5: Verify all 3 additions are present**

Run: `grep -c "Stay within phase scope" github/copilot-instructions.md`
Expected: `1`

Run: `grep -c "phase-specific procedures" github/copilot-instructions.md`
Expected: `1`

Run: `grep -c "does not expand the current phase" github/copilot-instructions.md`
Expected: `1`

- [ ] **Step 6: Verify no existing content was removed**

Run: `grep -c "Reproduce the bug before proposing" github/copilot-instructions.md`
Expected: `1`

Run: `grep -c "Context Hygiene" github/copilot-instructions.md`
Expected: `1`

- [ ] **Step 7: Commit**

```bash
git add github/copilot-instructions.md
git commit -m "workflow-structural-clarity: copilot-instructions.md — 3 targeted additions"
```

**Engineer review prompt:**
- Are all 3 additions present at their correct locations (rule 7 under Drift Control, note under Priority Order, scope guard under Conscious Skip)?
- Is the `## Context Hygiene` block untouched?
- Was any existing rule removed or modified?

---

## Testing Checklist (run after all phases complete)

- [ ] `ls github/protocols/` — 5 files listed, no extras
- [ ] `grep -rl "Non-goals" github/skills/ | wc -l` — returns `15`
- [ ] `grep -c "protocols/" github/skills/execution/SKILL.md` — at least `6`
- [ ] `grep -n "PLAN_VERSION = 2):" github/skills/execution/SKILL.md` — zero results
- [ ] `grep -n "PLAN_VERSION = 2):" github/skills/context-packet/SKILL.md` — zero results
- [ ] `grep -n "SPEC_VERSION = 2):" github/skills/planning/SKILL.md` — zero results
- [ ] `grep -c "Stay within phase scope" github/copilot-instructions.md` — returns `1`
- [ ] `grep -c "phase-specific procedures" github/copilot-instructions.md` — returns `1`
- [ ] `grep -c "does not expand the current phase" github/copilot-instructions.md` — returns `1`

## Rollback Plan

Revert all phase commits: `git revert HEAD~6` where 6 = number of phase commits.

Each phase is one commit, so partial rollback is possible: `git revert HEAD~N` to undo only the last N phases.
