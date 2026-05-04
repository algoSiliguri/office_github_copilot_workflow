# Design Spec: Phased Execution + Workflow Guide

**Date:** 2026-04-03
**Context:** Extends the GitHub Copilot IntelliJ workflow (built 2026-04-02) to solve two problems:
1. Copilot times out when a plan touches many files across folders in a single agent session
2. Engineers cannot easily verify correctness when 10+ files change at once

---

## 1. Problem Statement

The current `execution/SKILL.md` runs all plan steps inline in one Copilot chat session. For plans with many file changes across multiple folders, this causes:

- **Timeouts** — Copilot agent mode accumulates tool call history and context; large plans exhaust it
- **Unverifiable diffs** — an engineer seeing 12 files changed simultaneously cannot confidently say "this is correct"

The current `planning/SKILL.md` outputs a flat numbered list of steps with no phase grouping. There is no concept of logical units, checkpoints, or review gates.

---

## 2. Solution Approach

**Two skill updates. No new files (except the usage guide).**

1. `planning/SKILL.md` — plan format gains explicit phases. Each phase is a logical unit: ≤5 files, ≤1 hour of work, independently reviewable.
2. `execution/SKILL.md` — gains a mode decision (inline vs sub-agent) and a review checkpoint protocol between phases.

**Inline vs sub-agent rule (automatic, not a user choice):**
- ≤3 files total across the whole plan → inline execution (all steps in current session)
- >3 files total → sub-agent per phase (each phase dispatched via `run_subagent`)

**Why sub-agents solve timeouts:** each `run_subagent` call starts with a fresh, minimal context — just the phase steps and the conventions file. No accumulated tool call history from previous phases. The parent agent only orchestrates.

**Review checkpoint protocol (sub-agent mode only):** after each phase completes and commits, the parent agent presents:
- Files changed in the phase
- Pasted test output from the subagent
- The engineer review prompt from the plan (written by the planner, not generic boilerplate)
- A gate: `continue` to proceed, or raise concerns

---

## 3. Updated Plan Format (`planning/SKILL.md`)

### Phase quality rules (added to planning skill)

A phase must satisfy all three:
- ≤5 files changed
- Represents a logical unit that can be reviewed independently ("if I showed only these changes, could a reviewer say yes or no?")
- Each individual step within the phase takes ≤30 minutes

Typical phase boundaries: by architectural layer (repository → service → controller), by feature area (auth module, notification module), or by change type (schema migration → model update → query update).

### New plan file format

```markdown
# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased — set by planning skill based on total file count across all phases]

## All Files Changed
Every file created or modified across all phases:
- `[exact/path/to/file]` — Phase N: [what changes and why]

---

## Phase 1: [Logical unit name — e.g. "Repository layer"]

**Files in this phase:**
- `src/auth/UserRepository.java` — new interface
- `src/auth/UserRepositoryImpl.java` — new JPA implementation
- `tests/auth/UserRepositoryTest.java` — unit tests

**Steps:**
1. Create `src/auth/UserRepository.java`: define findById(Long id), findByEmail(String email) — follow interface pattern in src/common/BaseRepository.java
2. Create `src/auth/UserRepositoryImpl.java`: implement using JPA EntityManager (see src/common/BaseRepositoryImpl.java for pattern)
3. Create `tests/auth/UserRepositoryTest.java`: test findById returns Optional.empty() for unknown id; test findByEmail returns correct user

**Test after this phase:**
`mvn test -Dtest=UserRepositoryTest`

**Engineer review prompt:**
- Does the repository interface match the data model in the spec?
- Does the impl follow the existing JPA pattern in BaseRepositoryImpl?
- Are edge cases (null input, unknown id) tested?

---

## Phase 2: [Next logical unit — e.g. "Service layer"]
[same structure]

---

## Testing Checklist (full suite, run after all phases)
- [ ] [test command] — full suite, no regressions
- [ ] Manual: [exact steps to verify end-to-end]

## Rollback Plan
- Revert all phase commits: `git revert HEAD~[N]` (where N = number of phases committed)
- [Any data migration to reverse]
```

---

## 4. Updated Execution Logic (`execution/SKILL.md`)

### Step 1: Read and decide mode

1. Read the plan file in full.
2. Read `conventions/SKILL.md` for test command.
3. Count total files across all phases.
4. Announce mode:
   - ≤3 files: "2 files total. Using **inline mode** — executing all steps now."
   - >3 files: "11 files across 4 phases. Using **sub-agent mode** — I'll execute one phase at a time, commit, and pause for your review."

### Step 2a: Inline execution (≤3 files)

Unchanged from current behaviour: execute all steps sequentially, run tests after each step, commit at the end, proceed to verification.

### Step 2b: Sub-agent execution (>3 files)

For each phase:

1. **Dispatch** `run_subagent` with a fully self-contained prompt — the subagent has no access to parent session context:
   - The phase's steps and files only (not the entire plan)
   - The **raw text content** of `conventions/SKILL.md` read inline (not a file path reference — the subagent cannot read the parent's workspace files unless told to)
   - Instruction: "Execute these steps exactly. Run [test command from conventions] after each step. Stop and report back if any test fails. Commit with message: `[ticket-id] phase N: [phase name]`. Return: files changed, test output, any deviations."

2. **On subagent return**, present the review checkpoint:

   > **Phase N complete — [Phase name]**
   >
   > **Files changed:** `file1.java` (created), `file2.java` (modified)
   >
   > **Test output:**
   > ```
   > [pasted from subagent]
   > ```
   >
   > **Please review:**
   > [engineer review prompt from the plan — exact text]
   >
   > Type `continue` to proceed to Phase N+1, or describe any concerns.

3. **Wait for engineer input.** If concerns raised, discuss and resolve before proceeding. Do not auto-continue.

4. **After all phases**, run the full test suite inline (not in subagent):
   > "All phases complete. Running full suite..."
   Then: "All plan steps complete. Testing checklist done. Switch to @Review Agent, then use `/verify`."

### Step 2b: Subagent failure handling

If a subagent returns a test failure:
- Do not start the next phase
- Report: "Phase N failed — [test name] failing. Use `/debug` to diagnose before retrying this phase."
- After fix: re-dispatch the same phase (not from the start of all phases)

---

## 5. New File: `github/WORKFLOW.md`

A usage guide that travels with the workflow when copied to any repo.

### Structure

1. **What this is** — 3 sentences: the cycle, the core rule, how to adapt
2. **Quick reference** — table: phase → agent → prompt → output artifact
3. **Setup** — 3 steps: copy folder, rename to `.github/`, fill in `conventions/SKILL.md`
4. **End-to-end example** — one realistic ticket ("Add rate limiting to the login endpoint") showing exactly what the engineer types and what Copilot produces at each handoff
5. **Execution modes** — explains inline vs sub-agent in plain language; confirms engineer doesn't choose, it's automatic
6. **Phase review checkpoints** — what the engineer sees, what to check, how to raise a concern
7. **Skipping a phase** — when legitimate and how to do it consciously
8. **Cheat sheet** — "I have a bug" / "I need to add a feature" / "My test is failing mid-execution" / "I got review comments back"

---

## 6. Files Changed

| File | Change |
|---|---|
| `github/skills/planning/SKILL.md` | Replace flat step format with phased format; add phase quality rules |
| `github/skills/execution/SKILL.md` | Add mode decision, sub-agent dispatch protocol, review checkpoint, failure handling |
| `github/WORKFLOW.md` | New file — engineer usage guide |

All other files: no change.

---

## 7. Risks & Dependencies

- `run_subagent` must be enabled in IntelliJ Copilot settings (confirmed available in target environment per spec dated 2026-04-02)
- The subagent instruction must be self-contained — it cannot assume any context from the parent session. The phase steps + conventions content must be fully embedded in the dispatch call.
- If subagent support is unavailable (different environment): fall back to inline execution with manual phase boundaries — engineer runs `/execute-plan` once per phase, referencing phase number in the prompt.
