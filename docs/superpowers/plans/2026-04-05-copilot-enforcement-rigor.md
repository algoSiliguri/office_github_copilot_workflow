# Copilot Enforcement Rigor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add enforcement density (iron laws, verification gates, two-stage review, escalation rules, granularity standards, no-placeholder rules, self-review loops, skill chaining, conditional entry, finishing workflow, drift control) to existing Copilot workflow skill files without adding new files or phases.

**Architecture:** All changes are additive sections or replacements within 7 existing skill files + 2 reference files. No new files created. Each task modifies one file, keeping changes reviewable in isolation.

**Tech Stack:** Markdown only. No build system, no tests, no deployable code.

---

## All Files Changed

- `github/skills/tdd/SKILL.md` — Task 1: Add iron law blockquote
- `github/skills/verification/SKILL.md` — Task 2: Add iron law blockquote
- `github/skills/debugging/SKILL.md` — Task 3: Add iron law + escalation section + TDD skill chaining in Step 5
- `github/skills/brainstorming/SKILL.md` — Task 4: Replace "Before Asking Anything" with "Entry Logic"
- `github/skills/spec-writing/SKILL.md` — Task 5: Add self-review loop before handoff
- `github/skills/planning/SKILL.md` — Task 6: Replace step granularity + add no-placeholder enforcement + add self-review loop
- `github/skills/execution/SKILL.md` — Task 7: Add iron law + verification gate + two-stage review + skill chaining + finishing workflow
- `github/WORKFLOW.md` — Task 8: Align guide text with all enforcement changes
- `github/copilot-instructions.md` — Task 9: Add Drift Control section

---

### Task 1: tdd/SKILL.md — Iron Law

**Files:**
- Modify: `github/skills/tdd/SKILL.md`

- [ ] **Step 1: Add iron law blockquote after frontmatter**

Insert immediately after line 4 (closing `---` of frontmatter), before `## Metadata`:

```markdown

> **IRON LAW:** No production code without a failing test first. No exceptions.

```

- [ ] **Step 2: Read file end-to-end to verify integration**

Read `github/skills/tdd/SKILL.md` from top to bottom. Confirm:
- Iron law blockquote is immediately after frontmatter, before `## Metadata`
- No duplicate content (the existing "Iron Law" reference on line 25 is different context — it stays)
- File reads naturally

- [ ] **Step 3: Commit**

```bash
git add github/skills/tdd/SKILL.md
git commit -m "feat: add iron law to tdd skill"
```

---

### Task 2: verification/SKILL.md — Iron Law

**Files:**
- Modify: `github/skills/verification/SKILL.md`

- [ ] **Step 1: Add iron law blockquote after frontmatter**

Insert immediately after line 5 (closing `---` of frontmatter), before `## Metadata`:

```markdown

> **IRON LAW:** No sign-off without pasted terminal output as evidence. No exceptions.

```

- [ ] **Step 2: Read file end-to-end to verify integration**

Read `github/skills/verification/SKILL.md`. Confirm:
- Iron law blockquote is immediately after frontmatter, before `## Metadata`
- Consistent with the existing "Hard Stop" section (complements, doesn't duplicate)
- File reads naturally

- [ ] **Step 3: Commit**

```bash
git add github/skills/verification/SKILL.md
git commit -m "feat: add iron law to verification skill"
```

---

### Task 3: debugging/SKILL.md — Iron Law + Escalation + Skill Chaining

**Files:**
- Modify: `github/skills/debugging/SKILL.md`

- [ ] **Step 1: Add iron law blockquote after frontmatter**

Insert immediately after line 3 (closing `---` of frontmatter), before `## Metadata`:

```markdown

> **IRON LAW:** No fixes without root cause investigation first. No exceptions.

```

- [ ] **Step 2: Add escalation section after Step 4**

Insert a new section between the existing Step 4 (Verify the Hypothesis) and Step 5 (Fix). Place it after line 59 (`If not confirmed: return to Step 3 with a new hypothesis.`):

```markdown

## Escalation

Track hypothesis count silently during this debugging session.

- **< 3 hypotheses tested:** Return to Step 3 with a new hypothesis.
- **>= 3 hypotheses tested:** STOP. Do not attempt a 4th hypothesis without engineer input.

Present to the engineer:

> **Escalation — 3 hypotheses exhausted**
>
> **Ruled out:**
> 1. [Hypothesis 1] — [why it was ruled out]
> 2. [Hypothesis 2] — [why it was ruled out]
> 3. [Hypothesis 3] — [why it was ruled out]
>
> **Current suspicion:** [what the evidence points to]
>
> This may be an architectural issue, not a local bug.
>
> How would you like to proceed?

Wait for engineer input before continuing.

```

- [ ] **Step 3: Add TDD skill chaining to Step 5**

In the existing Step 5 (Fix), insert at the beginning of the step body (after `## Step 5: Fix`):

```markdown

**REQUIRED:** Write a failing test that reproduces the bug BEFORE implementing the fix. Follow `.github/skills/tdd/SKILL.md` RED phase for this test.

```

So the full Step 5 reads:

```markdown
## Step 5: Fix

**REQUIRED:** Write a failing test that reproduces the bug BEFORE implementing the fix. Follow `.github/skills/tdd/SKILL.md` RED phase for this test.

Apply the minimal change that addresses the root cause.

Do not fix unrelated issues. Do not refactor while fixing.
```

- [ ] **Step 4: Read file end-to-end to verify integration**

Read `github/skills/debugging/SKILL.md`. Confirm:
- Iron law is after frontmatter, before `## Metadata`
- Escalation section sits between Step 4 and Step 5
- Step 5 starts with the REQUIRED TDD chaining reference
- Step numbering is still sequential (1-6)
- File reads naturally as a single coherent document

- [ ] **Step 5: Commit**

```bash
git add github/skills/debugging/SKILL.md
git commit -m "feat: add iron law, escalation rules, and TDD chaining to debugging skill"
```

---

### Task 4: brainstorming/SKILL.md — Conditional Entry Logic

**Files:**
- Modify: `github/skills/brainstorming/SKILL.md`

- [ ] **Step 1: Replace "Before Asking Anything" with "Entry Logic"**

Replace the entire `## Before Asking Anything` section (lines 31-49) with:

```markdown
## Entry Logic

1. Read `.github/skills/conventions/SKILL.md`.
2. Check the `## Active Context` block.
3. Do NOT explore files before understanding what the engineer is building.

**Active Context present and non-empty:**
Start with: "I see you're working on [context]. Let me ask about [specific aspect]."

**Active Context absent or empty:**
1. Ask exactly one seed question: *"In 1-2 sentences, what are you working on?"*
2. Write their answer into the `## Active Context` block in
   `.github/skills/conventions/SKILL.md`.
3. Then proceed with targeted questions.
```

- [ ] **Step 2: Read file end-to-end to verify integration**

Read `github/skills/brainstorming/SKILL.md`. Confirm:
- "Entry Logic" replaced "Before Asking Anything" — no remnants of old section
- 3 numbered steps are present
- Non-empty Active Context uses "I see you're working on..." phrasing
- Empty Active Context asks exactly one seed question
- No mention of file exploration in the entry logic itself (file exploration is allowed later, in the "When file exploration is needed" paragraph which is now removed — verify this is intentional per spec; the spec says "do NOT explore files before understanding what engineer is building" which is the entry logic concern)
- The "When file exploration is needed" and "Greenfield or new area" paragraphs from the old section are removed (they were part of the old "Before Asking Anything" section)
- File reads naturally

- [ ] **Step 3: Commit**

```bash
git add github/skills/brainstorming/SKILL.md
git commit -m "feat: replace brainstorming entry with conditional Active Context logic"
```

---

### Task 5: spec-writing/SKILL.md — Self-Review Loop

**Files:**
- Modify: `github/skills/spec-writing/SKILL.md`

- [ ] **Step 1: Add self-review section before handoff**

Insert a new section between the horizontal rule (line 76) and `## Output Format` (line 77). Place it after the line `more specific before accepting it.` and the `---`:

```markdown

## Self-Review (before handoff)

Before handing off to `/write-plan`, review the spec you just wrote. Fix issues inline — no separate review cycle.

1. **Placeholder scan:** Search for "TBD", "TODO", "implement later", `[placeholder]` syntax, or any vague language. Replace with specifics.
2. **Testability check:** For every requirement, can you write a failing test? If not, rewrite the requirement until you can.
3. **Internal consistency:** Do the requirements, architecture, and testing strategy all describe the same system? Flag contradictions.
4. **Scope check:** Does any requirement belong in a separate ticket? If so, remove it and note it as a follow-up.

```

- [ ] **Step 2: Read file end-to-end to verify integration**

Read `github/skills/spec-writing/SKILL.md`. Confirm:
- Self-review section appears after the spec content rules and before `## Output Format`
- 4 checks are present: placeholder scan, testability, internal consistency, scope
- "Fix issues inline" instruction is present
- File reads naturally

- [ ] **Step 3: Commit**

```bash
git add github/skills/spec-writing/SKILL.md
git commit -m "feat: add self-review loop to spec-writing skill"
```

---

### Task 6: planning/SKILL.md — Granularity + No Placeholders + Self-Review

**Files:**
- Modify: `github/skills/planning/SKILL.md`

- [ ] **Step 1: Replace step granularity rule**

In the `## Phase Quality Rules` section, replace rule 3 (line 44):

```
3. Each individual step within the phase takes ≤30 minutes
```

with:

```
3. Each individual step within the phase takes 2–5 minutes. A step is too large if it contains "and" — split it.
```

- [ ] **Step 2: Replace the plan quality bar time reference**

In the `## Plan Quality Bar` section, replace (line 57):

```
- A step that cannot be completed in under 30 minutes
```

with:

```
- A step that cannot be completed in 2–5 minutes
```

- [ ] **Step 3: Add granularity examples after Plan Quality Bar**

Insert after the "Accept these:" examples (after line 61, `- \`tests/auth/service_test.go — add test for nil user returning 401\``):

```markdown

### Correct Granularity

```
Phase 1, Steps:
1. Write failing test: `test_rate_limiter_returns_429_after_5_attempts`
2. Run test — expected: FAIL (RateLimiter class not found)
3. Create `src/ratelimit/RateLimiter.java` with stub `checkLimit()` method
4. Run test — expected: FAIL (assertion error, stub returns wrong value)
5. Implement `checkLimit()` with Redis counter logic
6. Run test — expected: PASS
7. Commit: "AUTH-456 phase 1: rate limiter core logic"
```

### Too Coarse

```
Phase 1, Steps:
1. Create RateLimiter class with Redis integration, add tests, and wire into LoginController
```

This is too coarse because it contains "and" — split into atomic steps.

```

- [ ] **Step 4: Add No Placeholders section**

Insert a new section after the Plan Structure section (after the closing `~~~` on line 113, before `---`):

```markdown

## No Placeholders

Every step contains either a code block showing the implementation or an exact command showing the verification. No exceptions.

Reject these patterns in any plan step:
- "TBD" / "TODO" / "implement later"
- "Add appropriate error handling" (vague — specify what error, what handling)
- "Similar to Step N" (subagents can't see other steps — repeat the content)
- "Follow existing patterns" (specify which pattern, which file)
- `[ClassName]` / `[methodName]` / `[path]` (placeholder syntax — use real names)

If you catch yourself writing any of these, stop and fill in the actual content.

```

- [ ] **Step 5: Add self-review section before handoff**

Insert before the `## Handoff` section (before line 127):

```markdown

## Self-Review (before handoff)

Before handing off to `/execute-plan`, review the plan you just wrote. Fix issues inline — no separate review cycle.

1. **Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps — add missing tasks.
2. **Placeholder scan:** Apply the No Placeholders checklist above. Fix any violations.
3. **Step independence:** Could a subagent execute each phase using only the steps in that phase, without seeing other phases? If not, add the missing context.
4. **Type consistency:** Do the types, method signatures, and property names used in later phases match what was defined in earlier phases? A function called `clearLayers()` in Phase 1 but `clearFullLayers()` in Phase 3 is a bug.

```

- [ ] **Step 6: Read file end-to-end to verify integration**

Read `github/skills/planning/SKILL.md`. Confirm:
- Phase Quality Rule 3 says "2–5 minutes" not "30 minutes"
- Plan Quality Bar time reference says "2–5 minutes"
- Correct Granularity example shows 7 atomic steps
- Too Coarse example shows a single combined step with "and"
- No Placeholders section lists all 5 rejection patterns
- "Similar to Step N" rejection includes the "subagents can't see other steps" explanation
- Self-review section has 4 checks: spec coverage, placeholder scan, step independence, type consistency
- "Fix issues inline" instruction is present
- Phase quality rules 1 (≤5 files) and 2 (logical unit) are unchanged
- File reads naturally

- [ ] **Step 7: Commit**

```bash
git add github/skills/planning/SKILL.md
git commit -m "feat: add 2-5min granularity, no-placeholder enforcement, and self-review to planning skill"
```

---

### Task 7: execution/SKILL.md — Iron Law + Verification Gate + Two-Stage Review + Skill Chaining + Finishing Workflow

**Files:**
- Modify: `github/skills/execution/SKILL.md`

This is the largest task — 5 changes to one file. Each step is still atomic.

- [ ] **Step 1: Add iron law blockquote after frontmatter**

Insert immediately after line 3 (closing `---` of frontmatter), before `## Metadata`:

```markdown

> **IRON LAW:** No step executed without reading the plan first. No deviations without asking.

```

- [ ] **Step 2: Add REQUIRED skill chaining to inline execution**

In `## Step 2a: Inline Execution`, replace lines 45-46:

```
5. Use `/tdd` for any step that introduces new production logic.
6. Use `/debug` for any failing test — diagnose before fixing.
```

with:

```
5. **REQUIRED:** Follow `.github/skills/tdd/SKILL.md` — RED -> GREEN -> REFACTOR for any step that introduces new production logic.
6. **REQUIRED:** Follow `.github/skills/debugging/SKILL.md` — reproduce -> isolate -> hypothesise -> verify -> fix when tests fail and cause is not immediately obvious.
```

- [ ] **Step 3: Add verification gate after inline execution**

Insert after the inline execution "After all steps" block (after line 53, `> **Session hygiene:** Start a new chat. Use \`/verify\`."`), before `## Step 2b`:

```markdown

### Verification Gate

Before claiming any of these: "step complete", "phase complete", "all tests pass", "full suite green" — run this gate:

1. **IDENTIFY:** What exact command proves the claim?
2. **RUN:** Execute it now — fresh execution, not cached output.
3. **READ:** Read the full output including exit code.
4. **CLAIM:** State the claim with the pasted evidence.

Reject these: "should pass", "probably works", "tests passed" (without output). Evidence is pasted terminal output — nothing else counts.

```

- [ ] **Step 4: Add REQUIRED skill chaining to phased execution subagent rules**

In the subagent prompt template inside `## Step 2b`, replace rules 5:

```
5. Use TDD for any step creating new logic: write the failing test first, then implement.
```

with:

```
5. **REQUIRED:** Follow TDD for any step creating new logic: write the failing test FIRST (RED), then implement (GREEN). No production code without a failing test.
6. **REQUIRED:** If a test fails and the cause is not obvious, follow systematic debugging: reproduce -> isolate -> hypothesise -> verify -> fix. Do not guess.
```

And renumber the old rule 6 to rule 7:

```
7. Commit when all steps pass: "[ticket-id] phase [N]: [phase name]"
```

- [ ] **Step 5: Replace single-stage review checkpoint with two-stage review**

Replace the `### Present the review checkpoint` section content. The current content (lines 94-110) shows a single review checkpoint. Replace with:

```markdown
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
```

- [ ] **Step 6: Add verification gate reference to phased execution**

Insert after the "After all phases complete" full suite run (after line 127, `> [run test command]`), before the "Then say:" line:

```markdown

Apply the **Verification Gate** (see above) before claiming the suite is green.

```

- [ ] **Step 7: Replace the session hygiene closing with finishing workflow**

Replace the final closing message in both inline and phased sections. For phased mode, replace the "Then say:" block (lines 129-130):

```
Then say: "Full suite green.
> **Session hygiene:** Start a new chat. Use `/verify`."
```

with:

```markdown
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
```

For inline mode, replace the similar closing (lines 52-53):

```
1. Run the full test suite.
2. Say: "All steps complete. Full suite green.
> **Session hygiene:** Start a new chat. Use `/verify`."
```

with:

```
1. Run the full test suite. Apply the **Verification Gate** before claiming green.
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
```

- [ ] **Step 8: Read file end-to-end to verify integration**

Read `github/skills/execution/SKILL.md`. Confirm:
- Iron law is after frontmatter, before `## Metadata`
- Inline execution has `**REQUIRED:**` references to TDD and debugging skills
- Verification Gate section exists between inline and phased execution
- Phased execution subagent rules include TDD and debugging as REQUIRED, numbered 1-7
- Two-stage review (Stage 1: Spec Compliance, Stage 2: Code Quality) replaces single checkpoint
- Stage 2 only runs after Stage 1 passes (explicitly stated)
- Finishing workflow with 3 options appears in both inline and phased modes
- Session hygiene reminder present in finishing workflow
- No auto-merge or auto-push
- File reads naturally as a single coherent document

- [ ] **Step 9: Commit**

```bash
git add github/skills/execution/SKILL.md
git commit -m "feat: add iron law, verification gate, two-stage review, skill chaining, and finishing workflow to execution skill"
```

---

### Task 8: WORKFLOW.md — Align Guide Text

**Files:**
- Modify: `github/WORKFLOW.md`

- [ ] **Step 1: Update Phase Review Checkpoints to describe two-stage review**

Replace the content of `## Phase Review Checkpoints` section (lines 216-232). Replace the numbered list (lines 220-223) with:

```markdown
1. **Stage 1 — Spec compliance:** Does the diff match the plan? All listed files changed, no unlisted changes.
2. **Stage 2 — Code quality:** Do tests test behaviour? Does the code follow conventions?
3. **Files changed** — exactly which files, created or modified
4. **Test output** — pasted directly from the subagent, not summarised
5. **Verification Gate** — all claims ("tests pass", "phase complete") backed by pasted terminal output
6. **Review prompt** — specific questions the planner wrote for this phase (not generic boilerplate)
7. **A gate** — type `continue` to proceed, or raise a concern
```

- [ ] **Step 2: Update End-to-End Example Phase 1 checkpoint**

In the AUTH-456 example (around line 173), update the Phase 1 checkpoint to show two-stage review. After the test output block and before `Type \`continue\``, add:

```markdown
>
> **Spec compliance:** All 3 planned files created. No unlisted changes. PASS.
> **Code quality:** Tests cover behaviour (not just happy path). Redis fallback returns false, not throws. PASS.
>
```

- [ ] **Step 3: Update Execution Modes section**

In `## Execution Modes Explained` (around line 203), add a note about step granularity after the table. Insert after line 209 (`| >3 files total | **Phased (sub-agent)** | ...`):

```markdown

**Step granularity:** Each individual step in the plan takes 2–5 minutes. A step that contains "and" is too coarse — it should be split.

```

- [ ] **Step 4: Update Cheat Sheet debugging entry**

Replace the "My test is failing mid-execution" entry (lines 267-268):

```
**"My test is failing mid-execution"**
→ Don't push through. The execution skill will say "Phase N failed — use `/debug`". Do that. Come back with `retry phase N` once it's fixed.
```

with:

```
**"My test is failing mid-execution"**
→ Don't push through. The execution skill will say "Phase N failed — use `/debug`". Do that. If 3 hypotheses are exhausted without finding root cause, `/debug` will escalate to you — this may be an architectural issue. Come back with `retry phase N` once it's fixed.
```

- [ ] **Step 5: Update End-to-End Example Step 6**

Replace the Step 6 ending (lines 195-198):

```
No blockers → raise your PR.
```

with:

```
No blockers → the execution skill presents your finishing options:
1. **Merge to main** locally
2. **Push and raise PR**
3. **Keep branch as-is**

Choose your path. Start a new chat for the next ticket.
```

- [ ] **Step 6: Read file end-to-end to verify integration**

Read `github/WORKFLOW.md`. Confirm:
- Phase Review Checkpoints describes two-stage review (spec compliance then code quality)
- Phase Review Checkpoints mentions Verification Gate
- AUTH-456 Phase 1 checkpoint shows both review stages
- Execution Modes references 2–5 minute step granularity
- Cheat Sheet debugging entry mentions 3-attempt escalation threshold
- End-to-End Example Step 6 shows structured finishing choice
- Quick Reference table is unchanged
- File reads naturally

- [ ] **Step 7: Commit**

```bash
git add github/WORKFLOW.md
git commit -m "feat: align WORKFLOW.md with enforcement rigor changes"
```

---

### Task 9: copilot-instructions.md — Drift Control

**Files:**
- Modify: `github/copilot-instructions.md`

- [ ] **Step 1: Add Drift Control section**

Insert between `## Hard Rules` (ends at line 14) and `## Conscious Skip Protocol` (line 16). Add:

```markdown

## Drift Control

Reinforcement rules for behaviors that demonstrably drift in practice.

1. Reproduce the bug before proposing a fix
2. Ask before guessing when information is missing
3. State uncertainty explicitly — never present guesses as facts
4. Do not fabricate APIs, file paths, or tool behaviors
5. Verify the solution works after implementing it
6. Read relevant existing code before suggesting or making modifications

```

- [ ] **Step 2: Read file end-to-end to verify integration**

Read `github/copilot-instructions.md`. Confirm:
- Drift Control section appears between Hard Rules and Conscious Skip Protocol
- Contains exactly 6 numbered rules matching the spec
- One-line rationale present in the section description
- File reads naturally

- [ ] **Step 3: Commit**

```bash
git add github/copilot-instructions.md
git commit -m "feat: add drift control rules to copilot-instructions"
```

---

## Final Verification

After all 9 tasks are complete:

- [ ] Read each of the 9 modified files once more and verify no content was accidentally deleted or duplicated
- [ ] Verify the spec's "Files NOT changed" list: `setup/SKILL.md`, `conventions/SKILL.md`, `review/SKILL.md`, all agents, all prompts — none were touched
- [ ] Count total added tokens is roughly ~1000 across all files (quick eyeball — each iron law is ~15 tokens, sections are 50-150 tokens each)
