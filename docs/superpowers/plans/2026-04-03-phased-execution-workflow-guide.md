# Phased Execution + Workflow Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update two skill files to support phased execution with sub-agent dispatch and review checkpoints, and create an engineer-facing workflow guide.

**Architecture:** Three files change. `planning/SKILL.md` gains phase grouping in its plan format. `execution/SKILL.md` gains an inline/sub-agent mode decision and a checkpoint protocol. `WORKFLOW.md` is a new usage guide that travels with the workflow.

**Tech Stack:** Markdown only. No build tools. Validated by reading the files.

---

## File Map

**Modified:**
- `github/skills/planning/SKILL.md` — add phase structure to plan format and phase quality rules
- `github/skills/execution/SKILL.md` — add inline/sub-agent mode decision, sub-agent dispatch protocol, review checkpoint

**Created:**
- `github/WORKFLOW.md` — engineer usage guide with concrete examples

---

## Task 1: Update `planning/SKILL.md`

**Files:**
- Modify: `github/skills/planning/SKILL.md`

- [ ] **Step 1: Overwrite `github/skills/planning/SKILL.md` with phased plan format**

Write the following content exactly:

```markdown
---
name: planning
description: Creates a phased implementation plan from a spec file by reading the actual codebase first. Generates concrete file-level steps with real paths — not placeholders. Use when ready to plan implementation after a spec is written and approved.
allowed-tools: read_file, list_dir, file_search, grep_search, semantic_search
---

You are in plan phase. Create a phased implementation plan grounded in the actual code.

## Before Writing a Single Step

1. Read the spec file in full — understand every requirement and constraint.
2. Explore the codebase:
   - `list_dir` to understand the project structure
   - `file_search` to find relevant files by name pattern
   - `semantic_search` to find code related to what you're building
   - `read_file` to understand existing patterns, interfaces, and naming conventions
3. Map what needs to change and where — real files, real line ranges.

Only write steps after you have seen the actual code.

## Phase Quality Rules

Group steps into phases. A phase MUST satisfy all three:
1. ≤5 files changed
2. Represents a logical unit that can be reviewed independently — ask: "If I showed only these changes to a reviewer, could they say yes or no without seeing the rest?"
3. Each individual step within the phase takes ≤30 minutes

Typical phase boundaries: by architectural layer (repository → service → controller), by feature area (auth module, notification module), or by change type (schema migration → model update → query update).

**Set execution mode** based on total files across ALL phases:
- ≤3 files total → `Execution mode: inline`
- >3 files total → `Execution mode: phased`

## Plan Quality Bar

Reject these in any step:
- A step that references `[ClassName].[ext]` or any placeholder path
- A step that says "add validation" or "implement feature" without showing where and how
- A step that cannot be completed in under 30 minutes

Accept these:
- `src/auth/service.go:45 — add nil check before calling user.GetProfile()`
- `tests/auth/service_test.go — add test for nil user returning 401`

Read `.github/skills/conventions/SKILL.md` for the test command, build command, and plans path.

Create the plan file at: `[plans-path]/YYYY-MM-DD-[ticket-id]-[feature-name].md`

## Plan Structure

~~~markdown
# Implementation Plan: [TICKET-ID] — [Feature Name]

> **Execution mode:** [inline | phased]

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
`[test command from conventions] [specific test class]`

**Engineer review prompt:**
- [Specific question about what to verify — written by the planner based on what could go wrong]
- [Another specific question]

---

## Phase 2: [Next logical unit]
[same structure]

---

## Testing Checklist (run after all phases complete)
- [ ] [test command] — full suite, no regressions
- [ ] Manual: [exact steps to verify end-to-end]

## Rollback Plan
- Revert all phase commits: `git revert HEAD~[N]` where N = number of phases
- [Any data migration to reverse, if applicable]
~~~

When plan is complete, say:
> "Plan written to `[path]`. Switch to @Implementation Agent, then use `/execute-plan`."
```

- [ ] **Step 2: Verify the file was written correctly**

Read `github/skills/planning/SKILL.md` and confirm:
- Contains `## Phase Quality Rules`
- Contains `Execution mode: inline` and `Execution mode: phased`
- Contains `## Phase 1:` in the plan structure template
- Contains `Engineer review prompt:`
- Does NOT contain the old `## Step-by-Step Implementation` section

- [ ] **Step 3: Commit**

```bash
cd /Users/koustavdas/Documents/Claude/Office
git add github/skills/planning/SKILL.md
git commit -m "feat: add phased plan format and execution mode to planning skill"
```

---

## Task 2: Update `execution/SKILL.md`

**Files:**
- Modify: `github/skills/execution/SKILL.md`

- [ ] **Step 1: Overwrite `github/skills/execution/SKILL.md` with phased execution logic**

Write the following content exactly:

```markdown
---
name: execution
description: Enforces disciplined plan-driven implementation. Automatically selects inline or sub-agent-per-phase execution based on plan size. Presents review checkpoints between phases. Use when executing an implementation plan.
---

You are in execute phase. Implement the plan exactly as written — nothing more, nothing less.

## Step 1: Read the Plan and Decide Mode

1. Read the plan file in full.
2. Read `.github/skills/conventions/SKILL.md` for the test command and commit format.
   Keep the raw text — you will embed it in subagent prompts if using phased mode.
3. Check the `> **Execution mode:**` line in the plan.
4. Announce your mode:
   - **inline:** "2 files total. Using **inline mode** — executing all steps now."
   - **phased:** "11 files across 4 phases. Using **sub-agent mode** — I'll execute one phase at a time, commit, and pause for your review before each next phase."

## Step 2a: Inline Execution (`Execution mode: inline`)

Work through all steps sequentially:
1. Execute each step in order. Do not skip any.
2. After each step: run the test command. Do not proceed if any test fails.
3. Before doing anything not in the plan, stop and ask:
   "This isn't in the plan — should I add it before proceeding?"
4. If deviation is necessary, state it explicitly and get confirmation.
5. Use `/tdd` for any step that introduces new production logic.
6. Use `/debug` for any failing test — diagnose before fixing.
7. Commit at the end: `[ticket-id]: implement [feature name]`

After all steps:
1. Run the full test suite.
2. Say: "All steps complete. Switch to @Review Agent, then use `/verify`."

## Step 2b: Sub-Agent Execution (`Execution mode: phased`)

Work through phases in order. For each phase:

### Dispatch the subagent

Call `run_subagent` with the following fully self-contained prompt.
The subagent has NO access to the parent session — embed everything it needs:

```
You are implementing Phase [N]: [phase name] as part of ticket [ticket-id].

--- CONVENTIONS ---
[Paste the full raw text content of conventions/SKILL.md here]
--- END CONVENTIONS ---

FILES TO CHANGE IN THIS PHASE:
[List files from the phase block in the plan]

STEPS:
[Paste the exact numbered steps from the phase block]

RULES:
1. Execute steps in order. Do not skip any.
2. After each step, run the test command from CONVENTIONS.
3. If any test fails: stop immediately and return the failure output. Do not proceed.
4. Do not make changes not listed in the steps above. If something looks wrong, report back.
5. Use TDD for any step creating new logic: write the failing test first, then implement.
6. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"

RETURN when done:
- List every file you changed (path + created/modified)
- Full test output (paste — do not summarise)
- Any deviations or failures encountered
```

### Present the review checkpoint

After the subagent returns, show the engineer:

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

Then say: "Full suite green. Switch to @Review Agent, then use `/verify`."
```

- [ ] **Step 2: Verify the file was written correctly**

Read `github/skills/execution/SKILL.md` and confirm:
- Contains `## Step 1: Read the Plan and Decide Mode`
- Contains `Step 2a: Inline Execution`
- Contains `Step 2b: Sub-Agent Execution`
- Contains `run_subagent` dispatch template with `--- CONVENTIONS ---` block
- Contains the review checkpoint format with `**Phase [N] complete**`
- Contains failure handling with `retry phase [N]`
- Does NOT contain the old `## Rules During Execution` section

- [ ] **Step 3: Commit**

```bash
cd /Users/koustavdas/Documents/Claude/Office
git add github/skills/execution/SKILL.md
git commit -m "feat: add phased sub-agent execution with review checkpoints to execution skill"
```

---

## Task 3: Create `github/WORKFLOW.md`

**Files:**
- Create: `github/WORKFLOW.md`

- [ ] **Step 1: Create `github/WORKFLOW.md`**

Write the following content exactly:

```markdown
# Workflow Guide: GitHub Copilot Superpowers

A structured development workflow for IntelliJ + GitHub Copilot that keeps process discipline without slowing you down.

**Core rule:** skills are the single source of truth. Improve a skill, every phase using it improves. No duplication.

**To adapt to a new repo:** copy `.github/` in full, then edit only `skills/conventions/SKILL.md`.

---

## Quick Reference

| Phase | When | Agent | Prompt | You get |
|---|---|---|---|---|
| Brainstorm | Starting a ticket | @Design Agent | `/brainstorm` | Aligned problem + success criteria |
| Spec | After brainstorm | @Design Agent | `/write-spec` | Spec file in `docs/specs/` |
| Plan | After spec approved | @Design Agent | `/write-plan` | Phased plan file in `docs/plans/` |
| Execute | After plan approved | @Implementation Agent | `/execute-plan` | Committed code, phase by phase |
| TDD | Inside execute, new logic | @Implementation Agent | `/tdd` | Red → green cycle |
| Debug | Inside execute, failing test | @Implementation Agent | `/debug` | Root cause identified and fixed |
| Verify | After all phases done | @Review Agent | `/verify` | Verification file with pasted test output |
| Review | After verification | @Review Agent | `/review` | BLOCKER / SUGGESTION list |

---

## Setup (one-time per repo)

1. Copy the `.github/` folder to the root of your repo
2. Open `skills/conventions/SKILL.md` and fill in your repo's values:
   - Ticket format (e.g. `PROJ-1234`)
   - Test command (e.g. `mvn test`, `pytest`, `go test ./...`)
   - Artifact paths for specs, plans, verifications
   - Commit message format
3. In IntelliJ: Settings → Tools → GitHub Copilot → enable Agent Mode, Custom Agents, Subagents, and Skills

That's it. Every other file is language-agnostic and requires no editing.

---

## End-to-End Example: "Add rate limiting to the login endpoint"

Ticket: `AUTH-456`

### Step 1 — Brainstorm

Open Copilot Chat. Type:
```
/brainstorm
```

The Design Agent reads the codebase silently, then opens the conversation:

> "I can see your login endpoint in `src/auth/LoginController.java`. It calls `AuthService.authenticate()` which does a DB lookup per attempt. No rate limiting exists today.
>
> What's driving this ticket — are you seeing brute-force attempts in production, or is this a compliance requirement?"

You answer. The agent asks one follow-up at a time — threshold values, per-IP vs per-user, lockout behaviour, what happens during a DDoS. When it has enough:

> "I think I understand enough to write a spec. Here's what we've aligned on:
>
> **Problem:** Login endpoint has no rate limiting; credential-stuffing attacks succeed silently.
> **Success criteria:** After 5 failed attempts from the same IP in 10 minutes, return 429. Successful login resets the counter.
> **Constraints:** Must not slow down the happy path. Redis already in the stack.
> **Key risks:** IP spoofing via X-Forwarded-For; Redis unavailability must not break login entirely.
>
> Does this capture it? If yes, use `/write-spec` and paste this summary as input."

### Step 2 — Spec

```
/write-spec
```
Paste the brainstorm summary + `AUTH-456`. The Design Agent creates:
`docs/specs/2026-04-03-AUTH-456-login-rate-limiting.md`

Review it. When happy, continue.

### Step 3 — Plan

```
/write-plan
```
Paste the spec path. The Design Agent explores the codebase, then writes:
`docs/plans/2026-04-03-AUTH-456-login-rate-limiting.md`

For this ticket: 9 files across 3 phases (Redis config, rate limiter service, controller integration). The plan is annotated `Execution mode: phased`.

Review the plan. Check phase boundaries make sense. When happy, continue.

### Step 4 — Execute

Switch to @Implementation Agent. Type:
```
/execute-plan
```
Paste the plan path.

The agent announces:
> "9 files across 3 phases. Using **sub-agent mode** — I'll execute one phase at a time, commit, and pause for your review."

**Phase 1 runs** (Redis config + RateLimiterRepository — 3 files). A subagent executes with fresh context. When done, you see:

> **Phase 1 complete — Redis infrastructure**
>
> **Files changed:** `src/config/RedisConfig.java` (created), `src/ratelimit/RateLimitRepository.java` (created), `tests/ratelimit/RateLimitRepositoryTest.java` (created)
>
> **Test output:**
> ```
> [BUILD SUCCESS]
> Tests run: 3, Failures: 0, Errors: 0
> ```
>
> **Please review:**
> - Does RedisConfig use the connection pool settings from application.properties?
> - Does RateLimitRepository degrade gracefully when Redis is unavailable (returns false, not throws)?
>
> Type `continue` to proceed to Phase 2, or describe any concerns.

You check the diff. Three focused files. You verify the Redis fallback. Type `continue`.

**Phase 2 and Phase 3** follow the same pattern. Each is a bounded, reviewable diff.

### Step 5 — Verify

Switch to @Review Agent. Type:
```
/verify
```
Paste the spec path. The agent maps each spec requirement to a test, runs them, pastes output. Creates `docs/verifications/2026-04-03-AUTH-456-login-rate-limiting.md`.

### Step 6 — Review

```
/review
```
Paste the verification file path + `git diff --name-only main`. The agent checks all 5 areas (spec coverage, verification evidence, test quality, security, deviations). Reports BLOCKERs and SUGGESTIONs.

No blockers → raise your PR.

---

## Execution Modes Explained

When you run `/execute-plan`, the Implementation Agent reads the plan and decides the execution mode automatically:

| Plan size | Mode | What happens |
|---|---|---|
| ≤3 files total | **Inline** | Agent executes all steps in the current chat session, one after another |
| >3 files total | **Phased (sub-agent)** | Agent dispatches each phase to a fresh subagent, then pauses for your review |

**You don't choose the mode.** It's set by the planner when writing the plan (based on file count) and read by the execution skill.

**Why sub-agents for larger plans?** Each subagent starts with a fresh, minimal context — just the phase steps and your repo conventions. No accumulated tool call history. This prevents Copilot timeouts on multi-folder changes.

---

## Phase Review Checkpoints

In phased mode, after each phase you see:

1. **Files changed** — exactly which files, created or modified
2. **Test output** — pasted directly from the subagent, not summarised
3. **Review prompt** — specific questions the planner wrote for this phase (not generic boilerplate)
4. **A gate** — type `continue` to proceed, or raise a concern

**What to look for at a checkpoint:**
- Does the diff match what the phase description said it would do?
- Do the tests cover the behaviour, not just the happy path?
- Does the review prompt raise anything you'd want to verify manually?

If something looks wrong: describe the concern. The agent will not proceed until you're satisfied.

---

## Skipping a Phase

Sometimes skipping is legitimate — a hotfix, a trivial rename, a PR with no new behaviour.

**How to skip consciously:**

1. State it explicitly when opening the chat: "Skipping brainstorm and spec because this is a one-line config change."
2. Note what artifact is missing: "No spec file for this change."
3. Continue with the next applicable phase.

**Never skip silently.** An undocumented skip is an undocumented assumption.

Hard rules that cannot be skipped regardless:
- No "done" without running tests — always paste actual output
- No PR without a verification file

---

## Cheat Sheet: Common Situations

**"I have a new feature to build"**
→ Start with `/brainstorm`. Don't skip to `/write-plan` — the brainstorm shapes what goes in the spec.

**"I have a bug to fix"**
→ `/debug` first (describe the failing behaviour). Once you have a root cause, `/write-plan` for the fix, then `/execute-plan`.

**"My test is failing mid-execution"**
→ Don't push through. The execution skill will say "Phase N failed — use `/debug`". Do that. Come back with `retry phase N` once it's fixed.

**"I got review comments on my PR"**
→ For each comment that changes code: create a mini-plan (even one phase, one file). Run `/execute-plan`. Run `/verify` again before updating the PR. Don't make ad-hoc edits without a test.

**"The plan has a step that's clearly wrong"**
→ Tell the Implementation Agent: "This isn't right — [reason]." Ask it to confirm before proceeding. If the plan needs updating, do it in the plan file first, then continue.

**"I'm in a different IDE / Copilot environment"**
→ Sub-agents may not be available. In that case: run `/execute-plan` once per phase, telling the agent which phase number to start from. Commit after each. The checkpoints still happen — manually.
```

- [ ] **Step 2: Verify the file was written correctly**

Read `github/WORKFLOW.md` and confirm:
- Contains `## Quick Reference` table
- Contains `## End-to-End Example`
- Contains `AUTH-456` as the concrete example throughout
- Contains `## Execution Modes Explained` table
- Contains `## Phase Review Checkpoints`
- Contains `## Cheat Sheet`

- [ ] **Step 3: Commit**

```bash
cd /Users/koustavdas/Documents/Claude/Office
git add github/WORKFLOW.md
git commit -m "docs: add engineer workflow guide with phased execution examples"
```

---

## Task 4: Final verification

- [ ] **Step 1: Confirm all three files exist**

```bash
ls /Users/koustavdas/Documents/Claude/Office/github/skills/planning/SKILL.md
ls /Users/koustavdas/Documents/Claude/Office/github/skills/execution/SKILL.md
ls /Users/koustavdas/Documents/Claude/Office/github/WORKFLOW.md
```

Expected: all three paths return without error.

- [ ] **Step 2: Confirm no language-specific terms leaked outside conventions/SKILL.md**

```bash
grep -r "mvn\|pytest\|npm test\|go test\|Spring Boot\|FastAPI\|AIB-" \
  /Users/koustavdas/Documents/Claude/Office/github \
  --exclude="*/conventions/SKILL.md"
```

Expected: no output (zero matches). The one exception is `UserRepository.java` used as an illustrative example in the plan template inside `planning/SKILL.md` — this is acceptable because it's in a comment block explaining structure, not a hard-coded convention. If this grep flags it, confirm the match is inside a fenced code block labelled as an example template, not a real path.

- [ ] **Step 3: Confirm execution skill references sub-agent dispatch correctly**

```bash
grep -c "run_subagent" /Users/koustavdas/Documents/Claude/Office/github/skills/execution/SKILL.md
```

Expected: at least 1 match.

- [ ] **Step 4: Confirm planning skill sets execution mode**

```bash
grep "Execution mode" /Users/koustavdas/Documents/Claude/Office/github/skills/planning/SKILL.md
```

Expected: two lines — one for `inline`, one for `phased`.
