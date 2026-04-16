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
3. Check the `> **Execution mode:**` line in the plan.
   If no `Execution mode:` annotation is found (legacy plan): count total files in the plan.
   Use inline if ≤3 files, phased if >3 files.
4. Announce your mode:
   - **inline:** "2 files total. Using **inline mode** — executing all steps now."
   - **phased:** "11 files across 4 phases. Using **sub-agent mode** — I'll execute one phase at a time, commit, and pause for your review before each next phase."

## Step 2a: Inline Execution (`Execution mode: inline`)

**Context packet check (run before any steps):**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Check for `[context-packets-path]/[ticket-id]/phase-1-context.md` (inline plans use a single phase; try `phase-1` first, then `phase-2` if not found).
3. If found: read the full context packet. Note the `Coverage confidence` field. Use `## Relevant Decisions` and `## Module Context` to frame your understanding before touching any code. Do not load additional module or knowledge pages from the index — the packet is the full context budget for this plan.
4. If not found: proceed without pre-loaded context. The Codebase Search Protocol remains available on demand throughout execution.

Work through all steps sequentially:
1. Execute each step in order. Do not skip any.
   Before making any change that affects a public interface, a dependency's behavior, or a constraint boundary (as defined in `## Relevant Decisions` in the context packet, if loaded): confirm the change does not conflict with any recorded decision. If it conflicts: stop immediately. Say: "This change conflicts with a recorded decision in the context packet: '[exact decision text]'. Should I revise the approach or proceed with an explicit override?" Do not continue without the engineer's response.
   When a step requires reading existing code to understand a module or class, follow the **Codebase Search Protocol** in this skill.
2. After each step: run the test command. Do not proceed if any test fails.
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
2. Present the finishing options:

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

## Step 2b: Sub-Agent Execution (`Execution mode: phased`)

Work through phases in order. For each phase:

### Dispatch the subagent

**Before dispatching — context packet check:**
1. Read `Context Packets:` path from `.github/skills/conventions/SKILL.md`.
2. Read `[context-packets-path]/[ticket-id]/phase-[N]-context.md` if it exists.
3. If found: copy the full file content for embedding in the subagent prompt (CONTEXT_PACKET_CONTENT).
4. If not found: set CONTEXT_PACKET_CONTENT = `No context packet available. Use the Codebase Search Protocol for any module lookups during this phase.`

Spin up a new `@Implementation Agent` sub-session with the following fully self-contained prompt.
The sub-session has NO access to the parent session — embed everything it needs.
Copy and complete the prompt below exactly, replacing bracketed placeholders with actual values from the plan:

```
You are implementing Phase [N]: [phase name] as part of ticket [ticket-id].

--- CONVENTIONS ---
[Paste the full raw text content of conventions/SKILL.md here]
--- END CONVENTIONS ---

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
6. **REQUIRED:** Follow TDD for any step creating new logic: write the failing test FIRST (RED), then implement (GREEN). No production code without a failing test.
7. **REQUIRED:** If a test fails and the cause is not obvious, follow systematic debugging: reproduce -> isolate -> hypothesise -> verify -> fix. Do not guess.
8. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
9. If a deviation from the plan is necessary and engineer-approved: append to the plan file — add `## Amendments` section at the end if missing, then append: `- [YYYY-MM-DD] Phase [N]: [what changed and why it was necessary]`
10. If you discover an unexpected constraint or system behavior: append to the plan file — add `## Discoveries` section at the end if missing, then append: `- [YYYY-MM-DD] [brief description of what you discovered]`

RETURN when done:
- List every file you changed (path + created/modified)
- Full test output (paste — do not summarise)
- Any deviations or failures encountered
```

### Present the review checkpoint

After the subagent returns, run a two-stage review before presenting to the engineer.

**Stage 1: Spec Compliance**
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

> **Phase [N] complete — [Phase name]**
>
> **Files changed:** `[file1]` (created), `[file2]` (modified)
>
> **Test output:**
> ```
> [Paste full output from subagent — do not summarise]
> ```
>
> **Please review:**
> [Copy the exact "Engineer review prompt" text from the plan for this phase]
>
> Type `continue` to proceed to Phase [N+1], or describe any concerns.

**Wait for the engineer's response. Do not auto-continue.**

### If the engineer raises concerns

Discuss and resolve. Do not start the next phase until the engineer types `continue`.

### If the subagent reports a test failure

> "Phase [N] failed — [test name] failing. Use `/debug` to diagnose.
> Once fixed, type `retry phase [N]` and I'll re-run this phase from the start."

On `retry phase [N]`: re-dispatch the same phase. Do not restart from Phase 1.

### After all phases complete

Run the full test suite in the current session (not a subagent):

> "All phases complete. Running full suite to confirm no regressions..."
> [run test command]

Apply the **Verification Gate** (see above) before claiming the suite is green.

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

Next phase: `/verify`

Start a new chat. Recommended: **Standard**. Use `/verify` with the spec file path to prove every requirement is met.

Apply context hygiene summary, then proceed.
