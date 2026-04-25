---
name: execution
description: Enforces disciplined plan-driven implementation. Automatically selects inline or sub-agent-per-phase execution based on plan size. Presents review checkpoints between phases. Use when executing an implementation plan.
---

> **IRON LAW:** No step executed without reading the plan first. No deviations without asking.

## Metadata

- **Name:** execution
- **Description:** Implements the plan exactly as written — step by step, with tests after each step and engineer review checkpoints between phases.
- **Phase:** 5 — Execute
- **Inputs:** Plan file path
- **Outputs:** Committed implementation code with a green full test suite; codebase ready for `/verify`

## When To Use

When an approved implementation plan exists. Do not write any code before reading the plan. If no plan exists, run `/write-plan` first. Use `/quick-task` only for trivial changes where a plan is consciously skipped.

## Inputs

- Plan file path (full path to the plan created in phase 4)

---

You are in execute phase. Implement the plan exactly as written — nothing more, nothing less.

## Step 1: Read the Plan and Decide Mode

1. Read the plan file in full.
2. Read `.github/skills/conventions/SKILL.md` for the test command and commit format.
   Keep the raw text — you will embed it in subagent prompts if using phased mode.
3. Check the `> **Execution mode:**` line in the plan. Three valid values:
   - `inline` — execute all steps in this session
   - `phased-inline` — execute phases sequentially in this session with hard gates between phases
   - `phased-subagent` — dispatch each phase to a fresh sub-agent
   If no `Execution mode:` annotation is found (legacy plan): count total files in the plan.
   Use `inline` if ≤5 files, `phased-inline` if 6–12 files, `phased-subagent` if >12 files.
4. Announce your mode:
   - **inline:** "2 files total. Using **inline mode** — executing all steps now."
   - **phased-inline:** "8 files across 3 phases. Using **phased-inline mode** — I'll execute phases sequentially in this session with a review gate between each."
   - **phased-subagent:** "14 files across 4 phases. Using **sub-agent mode** — I'll dispatch each phase to a fresh subagent and pause for your review before proceeding."
5. **Version detection:** Read the plan file's `schema_version` frontmatter. Store as PLAN_VERSION.
   - `schema_version: 2` → PLAN_VERSION = 2. Use v2 typed paths throughout this skill.
   - Absent → PLAN_VERSION = 1. All existing paths apply unchanged.
   If PLAN_VERSION = 2: run `/validate-artifact [plan-path]` silently. BLOCK if validation fails.

## Step 1.5: Context Packet Auto-Trigger (PLAN_VERSION = 2 only)

For each phase about to execute, before any step runs, check both conditions:
1. `plan.execution.mode` = `'phased-inline'` or `'phased-subagent'`
2. Total FileRef count across `phases[*].id=N .steps[*].files` ≥ 4

If both hold: silently invoke the context-packet skill for this phase (do not ask the engineer — run it as an internal step). Announce the result: "Context packet auto-triggered for Phase [N]: [N] files across [N] modules. Coverage: [level]."

If conditions are not met (inline mode, or < 4 files): announce: "Phase [N]: [N] file(s) — below auto-trigger threshold. Proceeding with codebase search protocol."

For PLAN_VERSION = 1: no change — context packet is triggered manually via `/context-packet` command.

## Step 1b: Coverage Confidence Announcement (all modes)

Read `Coverage confidence:` from the context packet (if loaded in Step 2a/2b/2c below) or check plan `## Intelligence Context` block.

Announce at session/phase start:
- `high`: "Context: high coverage — file reads restricted to context packet. I will not load files outside it."
- `medium`: "Context: medium coverage — one-hop expansion allowed for files referenced by loaded modules."
- `low`: "Context: low coverage — full codebase search available. I will note gaps as encountered."

If no context packet and no `## Intelligence Context` block: treat as `low`. Announce: "No context packet found. Context: low coverage — proceeding with full codebase search."

## Step 2a: Inline Execution (`Execution mode: inline`)

**Context packet check (run before any steps):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-1-context.md` (inline plans use a single phase; try `phase-1` first, then `phase-2` if not found).
3. If found: read the full context packet. Note the `Coverage confidence` field. Enforce based on level:
   - `high`: **Prohibited** from reading files outside the context packet. If a step requires a file read outside the packet, stop and say: "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH. Should I expand context or rephrase the step to work within the packet?"
   - `medium`: Controlled one-hop expansion allowed — may read files referenced by packet modules; do not scan broadly.
   - `low`: Expansion required. The Codebase Search Protocol is available without restriction.
   Use `## Relevant Decisions` and `## Module Context` to frame understanding before touching any code.
4. If not found: treat as `low` coverage. Note: "No context packet found — proceeding with full codebase search." The Codebase Search Protocol is available without restriction.

**Inline checkpoint discipline:**
- Count total steps in the plan. If ≥6: group steps by file (all steps on one file form one group, or by natural dependency boundary).
- After each group completes, show a **soft checkpoint** (informational — no gate, proceed automatically):
  ```
  — [group name, e.g. "RateLimiter.java"] — [N steps complete]
  Tests: [PASS / FAIL — one-line summary]
  ```
- After all steps complete: show a **hard checkpoint** in the same format as the phased checkpoint below (files changed, Stage 1, Stage 2, test output, finishing options). This is the only gate in inline mode.
- For inline plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.

Work through all steps sequentially:
1. Execute each step in order. Do not skip any.
   Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary (as defined in `## Relevant Decisions` in the context packet, if loaded): confirm the change does not conflict with any recorded decision. If it conflicts: stop immediately. Say: "This change conflicts with a recorded decision in the context packet: '[exact decision text]'. Should I revise the approach or proceed with an explicit override?" Do not continue without the engineer's response.
   When a step requires reading existing code to understand a module or class, follow the **Codebase Search Protocol** in this skill.
2. After each step: run the test command. Do not proceed if any test fails.
2a. **V2 only (PLAN_VERSION = 2):** When a step's verify command passes, append a `step-completed` amendment to the plan file's `amendments:` YAML array. Set `id: A{N}` where N = count of existing amendments + 1 (first amendment is A1; numbers never reused). Example:
    ```yaml
    - id: "A3"
      step_id: "P1.S2"
      phase: 1
      type: step-completed
      description: "Write TokenValidator class — verify passed: 3 tests, 0 failures"
      added_by: execution
    ```
3. Before doing anything not in the plan, stop and ask:
   "This isn't in the plan — should I add it before proceeding?"
4. If deviation is necessary, state it explicitly, get confirmation, then append to the plan file:
   - Add `## Amendments` at the end of the plan file if the section does not exist.
   - Append: `- [YYYY-MM-DD] Phase [N] (or Step [N] for inline): [what changed from the plan and why it was necessary]`
5. **REQUIRED:** Follow `.github/skills/tdd/SKILL.md` — RED -> GREEN -> REFACTOR for any step that introduces new production logic.
6. **REQUIRED:** Follow `.github/skills/debugging/SKILL.md` — reproduce -> isolate -> hypothesise -> verify -> fix when tests fail and cause is not immediately obvious.
7. Commit at the end: `[ticket-id]: implement [feature name]`
8. When you encounter an unexpected constraint, system behavior, or implementation detail not in the spec or plan: append to the plan file:
   - Add `## Discoveries` at the end of the plan file if the section does not exist.
   - Append: `- [YYYY-MM-DD] [Brief description of the constraint or behavior discovered]`

After all steps:
1. Run the full test suite. Apply the **Verification Gate** (see below) before claiming green.
2. Output the execution reflection blocks in order:

   **--- Context Quality Review ---**
   ```
   Coverage: [High / Medium / Low]

   Issues encountered:
   - Missing context (files not in packet, modules not in knowledge base)?
   - Irrelevant context loaded?
   - Misleading assumptions in the packet or knowledge signals?

   Would a context packet have helped? [Yes / No / N/A — packet was used]
   ```

   **--- Knowledge Candidates ---**
   ```
   List ONLY if meaningful (max 5):
   - New pattern discovered
   - Constraint not documented in knowledge base
   - Repeated confusion or ambiguity encountered
   - Fix or workaround that required reasoning
   ```
   Not auto-saved — candidates for future indexing only. If ≥3 strong candidates: recommend running `/index knowledge --incremental`.

   **Plan stability:** [Stable (no amendments) / Minor drift (1–2 amendments, no core logic change) / Major drift (core approach changed or multiple phases amended)]

3. Present the finishing options:

> **All steps complete. Full suite green.**
>
> How would you like to finish?
> 1. **Merge to main** — I'll merge this branch locally
> 2. **Push and raise PR** — I'll push and create a PR
> 3. **Keep branch as-is** — No merge, no push
>
> Regardless of choice: **Start a new chat. Use `/verify`.**

Wait for the engineer's choice. Do not auto-merge or auto-push.

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

### Verification Gate

Before claiming any of these: "step complete", "phase complete", "all tests pass", "full suite green" — run this gate:

1. **IDENTIFY:** What exact command proves the claim?
2. **RUN:** Execute it now — fresh execution, not cached output.
3. **READ:** Read the full output including exit code.
4. **CLAIM:** State the claim with the pasted evidence.

Reject these: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.

## Step 2b: Phased-Inline Execution (`Execution mode: phased-inline`)

Execute phases sequentially in the current session. No sub-agents. UX is identical to phased-subagent — same phase start format, same checkpoint format, same gate discipline.

For each phase:

**Announce phase start:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase [N] of [M] — [Phase name] — [N files] / [N steps]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Context packet check (before each phase):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: load it. Enforce coverage confidence behavior (see Step 1b).
4. If not found: treat as `low` confidence. Note: "No context packet for phase [N]. Proceeding with full codebase search."

**Execute all steps** in the phase using inline execution rules (see Step 2a).

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

**Gate is hard:** do not proceed to the next phase without explicit `continue` from the engineer.

**On receiving `continue` (between phases only — not after the final phase):**
Output the context reset block before announcing the next phase:

```
--- Context Reset ---

Completed Phase: [N]

Completed steps (from step-completed amendments, phase=[N]):
[For each Amendment where type='step-completed' AND phase=N, in id order:
  - [amendment.step_id]: [amendment.description]]

Changes from plan (from non-step-completed amendments, phase=[N]):
[For each Amendment where type ∈ {step-added, step-removed, verify-override, decision-conflict, scope-change} AND phase=N:
  - [amendment.type]: [amendment.description]
  OR "none" if no such amendments exist for phase N]

Next phase scope ([phases[*].id=N+1 .name]):
[One bullet per path in phases[*].id=N+1 .steps[*].files[*].path]

Discard: all prior phase execution details, test outputs, and debug/retry logs.
Next phase relies ONLY on: plan file, this block, and the auto-loaded context packet.
```

_Rule 3: this block is generated exclusively from (1) step-completed amendments for phase N, (2) other amendments for phase N, and (3) next phase StepNode file paths. No open-ended session synthesis._

Treat the conversation above this block as non-authoritative. Proceed as if starting fresh.

**On test failure:** "Phase [N] failed — [test name or compliance finding]. Use `/debug`. Type `retry phase [N]` when fixed." No auto-retry.

**Amendment and discovery tracking:** identical to inline mode — append to plan file under `## Amendments` or `## Discoveries`.

**After all phases complete** — run the full test suite in this session. Then output the execution reflection blocks (Context Quality Review, Knowledge Candidates, Plan Stability) and finishing options in the same format as inline mode (see Step 2a).

## Step 2c: Sub-Agent Execution (`Execution mode: phased-subagent`)

Work through phases in order. For each phase:

### Dispatch the subagent

**Announce phase start before dispatching:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase [N] of [M] — [Phase name] — [N files] / [N steps]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Before dispatching — context packet check:**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: copy the full file content for embedding in the subagent prompt (CONTEXT_PACKET_CONTENT).
4. If not found: set CONTEXT_PACKET_CONTENT = `No context packet available. Use the Codebase Search Protocol for any module lookups during this phase.`

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

**Sub-agent availability check:**
Attempt to initiate the `@Implementation Agent` sub-session. If it cannot be initiated (sub-agent feature unavailable, session error, or IDE limitation):

1. Emit:
   ```
   ⚠️ Execution Mode Change Detected
   Planned: phased-subagent
   Actual: phased-inline (fallback — sub-agents unavailable)
   ```
2. Output: "Please type `acknowledged` to continue with fallback mode."
3. Block all further execution until the engineer types `acknowledged`.
4. Append to the plan file immediately after the `> **Execution mode:**` line:
   `> **Execution mode override:** phased-inline (fallback — sub-agents unavailable) [YYYY-MM-DD]`
5. Switch to **phased-inline execution (Step 2b)** for this and all remaining phases. Do not attempt further sub-agent dispatches this session.

Spin up a new `@Implementation Agent` sub-session with the following fully self-contained prompt.
The sub-session has NO access to the parent session — embed everything it needs.
Copy and complete the prompt below exactly, replacing bracketed placeholders with actual values from the plan:

```
You are implementing Phase [N]: [phase name] as part of ticket [ticket-id].

--- CONVENTIONS ---
Test: [test command from conventions/SKILL.md]
Commit: [commit format from conventions/SKILL.md]
Lint: [lint command from conventions/SKILL.md, or "none"]
Ticket: [ticket format from conventions/SKILL.md]
--- END CONVENTIONS ---
[--- INJECTED: [section name] ---
[section content from conventions/SKILL.md — only present when keyword-triggered; omit block entirely if no injection]

--- CONTEXT PACKET ---
[Paste CONTEXT_PACKET_CONTENT here — either the full phase-[N]-context.md content or the "No context packet available" message]
--- END CONTEXT PACKET ---

FILES TO CHANGE IN THIS PHASE:
[List files from the phase block in the plan]

STEPS:
[Paste the exact numbered steps from the phase block]

RULES:
1. Execute steps in order. Do not skip any.
2. Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary: check ## Relevant Decisions in the CONTEXT PACKET (if available). If your change conflicts with a recorded decision: stop. Return the conflict to the parent session — do not proceed without acknowledgment.
3. After each step, run the test command from CONVENTIONS.
4. If any test fails: stop immediately and return the failure output. Do not proceed.
5. Do not make changes not listed in the steps above. If something looks wrong, report back.
6. Follow TDD for new logic (RED→GREEN→REFACTOR); use systematic debugging for failures (reproduce→isolate→hypothesise→verify→fix).
7. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
8. Amendments: append to `## Amendments` in plan file — `- [YYYY-MM-DD] Phase [N]: [change and reason]`. Discoveries: append to `## Discoveries` — `- [YYYY-MM-DD] [description]`.

RETURN when done:
- List every file you changed (path + created/modified)
- Full test output (paste — do not summarise)
- Any deviations or failures encountered
- Decisions & Assumptions: list only cases where multiple valid implementations existed, the plan or codebase was ambiguous, or behavior was inferred rather than specified. Max 5 bullets. Omit this field entirely if execution was straightforward with no judgment calls.
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

**Wait for the engineer's response. Do not auto-continue.**

### If the engineer raises concerns

Discuss and resolve. Do not start the next phase until the engineer types `continue`.

### If the subagent reports a test failure

> "Phase [N] failed — [test name] failing. Use `/debug` to diagnose.
> Once fixed, type `retry phase [N]` and I'll re-run this phase from the start."

**Retry tracking (in-session, per phase):**
Maintain a retry counter for each phase, initialized to 0 when the phase starts. On `retry phase [N]`: increment the counter for phase N, then re-dispatch. On `continue` to phase N+1: the counter for phase N is no longer relevant.

If the retry counter for phase [N] reaches 3 (i.e., this would be the 3rd retry attempt): do NOT re-dispatch. Output the phase failure state and stop:

```
Phase [N] — EXECUTION BLOCKED

This phase has failed 3 consecutive times.
Last failure: [Stage 1 finding or test failure output from the most recent attempt]

Choose one:
1. Amend plan — review and correct the steps in Phase [N], then type `resume phase [N]`
2. Abort execution — type `abort` to stop here

`retry phase [N]` is no longer accepted for this phase.
```

Wait for the engineer's response. Accept only:
- `resume phase [N]` — re-dispatch the phase once (reset counter to 0; if it fails again, re-enter failure state immediately)
- `abort` — stop execution and output the handoff block marking execution as incomplete

Do not accept `retry phase [N]` or `continue` while in this state.

### After all phases complete

Run the full test suite in the current session (not a subagent):

> "All phases complete. Running full suite to confirm no regressions..."
> [run test command]

Apply the **Verification Gate** (see above) before claiming the suite is green.

Then output the execution reflection blocks in order:

**--- Context Quality Review ---**
```
Coverage: [High / Medium / Low]

Issues encountered:
- Missing context (files not in packet, modules not in knowledge base)?
- Irrelevant context loaded?
- Misleading assumptions in the packet or knowledge signals?

Would a context packet have helped? [Yes / No / N/A — packet was used]
```

**--- Knowledge Candidates ---**
```
List ONLY if meaningful (max 5):
- New pattern discovered
- Constraint not documented in knowledge base
- Repeated confusion or ambiguity encountered
- Fix or workaround that required reasoning
```
Not auto-saved — candidates for future indexing only. If ≥3 strong candidates: recommend running `/index knowledge --incremental`.

**Plan stability:** [Stable (no amendments) / Minor drift (1–2 amendments, no core logic change) / Major drift (core approach changed or multiple phases amended)]

Then present the finishing options:

> **All phases complete. Full suite green.**
>
> How would you like to finish?
> 1. **Merge to main** — I'll merge this branch locally
> 2. **Push and raise PR** — I'll push and create a PR
> 3. **Keep branch as-is** — No merge, no push
>
> Regardless of choice: **Start a new chat. Use `/verify`.**

Wait for the engineer's choice. Do not auto-merge or auto-push.

---

## Output Format

- All plan steps executed in order
- Tests passing after each step
- Commits per phase (phased mode) or single commit (inline mode)
- Final: full test suite green, codebase ready for verification

## Dependencies

- `.github/skills/conventions/SKILL.md` — for test command and commit format
- Plan file (path provided as input)
- `.github/skills/tdd/SKILL.md` — referenced for new logic steps
- `.github/skills/debugging/SKILL.md` — referenced for failing tests

## Handoff

Next: `/verify [spec-file-path]` in a new chat.

Apply context hygiene before closing this chat.
