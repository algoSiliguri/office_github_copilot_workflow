# Spec: Copilot Workflow Enforcement Rigor — Approach B

## Problem Statement

The GitHub Copilot workflow system (`github/`) is structurally complete — 10 phases,
3 agents, 10 skills — but lacks the enforcement rigor that makes the superpowers
plugin resistant to AI drift. The system defines strong phases and agent roles but
leaves room for interpretation inside those phases. This is where drift emerges:
vague plan steps, unchecked completion claims, single-stage reviews, and no escalation
thresholds.

## Solution Approach

Add enforcement density to existing skills without adding new files, new phases, or
new concepts. Every change is a short, unambiguous addition to an existing skill file.
The workflow stays the same; the guardrails get sharper. Total cost: ~1000 tokens
across 7 skill files + 2 reference files.

## Requirements

### Iron Laws (Change 1)

- [ ] `skills/tdd/SKILL.md` opens with: `> **IRON LAW:** No production code without a failing test first. No exceptions.`
- [ ] `skills/debugging/SKILL.md` opens with: `> **IRON LAW:** No fixes without root cause investigation first. No exceptions.`
- [ ] `skills/verification/SKILL.md` opens with: `> **IRON LAW:** No sign-off without pasted terminal output as evidence. No exceptions.`
- [ ] `skills/execution/SKILL.md` opens with: `> **IRON LAW:** No step executed without reading the plan first. No deviations without asking.`
- [ ] Each iron law is placed immediately after frontmatter, before any other content.
- [ ] Each iron law is a blockquote (visually prominent, ~15 tokens each).

### Verification Gate (Change 2)

- [ ] `skills/execution/SKILL.md` contains a "Verification Gate" section after both inline and phased execution steps.
- [ ] The gate defines 4 steps: IDENTIFY (what command?), RUN (fresh execution), READ (full output + exit code), CLAIM (state with evidence).
- [ ] The gate explicitly lists which claims it applies to: "step complete", "phase complete", "all tests pass", "full suite green".
- [ ] The gate explicitly rejects: "should pass", "probably works", "tests passed" without output.

### Two-Stage Review (Change 3)

- [ ] `skills/execution/SKILL.md` phased execution review checkpoint is split into two stages.
- [ ] Stage 1 is "Spec Compliance": implementation matches plan steps, all listed files changed, no unlisted changes.
- [ ] Stage 2 is "Code Quality": follows conventions, tests test behaviour not implementation, no obvious issues.
- [ ] Stage 2 only runs after Stage 1 passes.
- [ ] If Stage 1 fails, subagent fixes and Stage 1 re-runs before Stage 2 begins.
- [ ] If Stage 2 fails, subagent fixes and only Stage 2 re-runs.
- [ ] The engineer review checkpoint (existing format) is presented after both stages pass.

### Escalation Rules (Change 4)

- [ ] `skills/debugging/SKILL.md` contains an "Escalation" section after Step 4 (Verify the Hypothesis).
- [ ] Hypothesis count is tracked silently during the debugging session.
- [ ] At < 3 hypotheses: return to Step 3 with new hypothesis.
- [ ] At >= 3 hypotheses: STOP. Present what's been ruled out, what's suspected, and ask engineer how to proceed.
- [ ] The stop message explicitly suggests "This may be an architectural issue, not a local bug."
- [ ] No 4th hypothesis attempted without engineer input.

### Plan Step Granularity (Change 5)

- [ ] `skills/planning/SKILL.md` replaces "each step takes <= 30 minutes" with "each step is 2-5 minutes".
- [ ] The rule states: "A step is too large if it contains 'and' — split it."
- [ ] A "Correct granularity" example is provided showing 7 atomic steps (write test, run test, create stub, run test, implement, run test, commit).
- [ ] A "Too coarse" counter-example is provided showing a single step that combines multiple actions.
- [ ] The phase quality rule "<=5 files changed" is preserved unchanged.
- [ ] The phase quality rule "represents logical unit reviewable independently" is preserved unchanged.

### No-Placeholder Enforcement (Change 6)

- [ ] `skills/planning/SKILL.md` contains a "No Placeholders" section with an explicit rejection list.
- [ ] Rejected patterns: "TBD" / "TODO" / "implement later", "Add appropriate error handling" (vague), "Similar to Step N" (cross-reference), "Follow existing patterns" (unspecified), `[ClassName]` / `[methodName]` / `[path]` (placeholder syntax).
- [ ] The rule states: "Every step contains either a code block showing the implementation or an exact command showing the verification. No exceptions."
- [ ] The "Similar to Step N" rejection explicitly explains why: "subagents can't see other steps."

### Self-Review Loops (Change 7)

- [ ] `skills/spec-writing/SKILL.md` contains a "Self-Review (before handoff)" section at the end, before the handoff instruction.
- [ ] Spec self-review checks: placeholder scan, testability check, internal consistency, scope check.
- [ ] The testability check asks: "For every requirement, can you write a failing test? If not, rewrite."
- [ ] `skills/planning/SKILL.md` contains a "Self-Review (before handoff)" section at the end, before the handoff instruction.
- [ ] Plan self-review checks: spec coverage (every requirement mapped), placeholder scan (apply No Placeholders checklist), step independence (subagent-executable without other phases), type consistency (signatures and names match across steps).
- [ ] Both self-reviews say "Fix issues inline" — no separate review cycle.

### Explicit Skill Chaining (Change 8)

- [ ] `skills/execution/SKILL.md` inline execution contains: `**REQUIRED:** Follow .github/skills/tdd/SKILL.md — RED -> GREEN -> REFACTOR` for steps creating new production logic.
- [ ] `skills/execution/SKILL.md` contains: `**REQUIRED:** Follow .github/skills/debugging/SKILL.md — reproduce -> isolate -> hypothesise -> verify -> fix` when tests fail and cause is not immediately obvious.
- [ ] `skills/debugging/SKILL.md` Step 5 (Fix) contains: `**REQUIRED:** Write a failing test that reproduces the bug BEFORE implementing the fix. Follow .github/skills/tdd/SKILL.md RED phase for this test.`
- [ ] Cross-references use `**REQUIRED:**` prefix (not "see" or "refer to").

### Conditional Entry in Brainstorming (Change 9)

- [ ] `skills/brainstorming/SKILL.md` "Before Asking Anything" section is replaced with an "Entry Logic" section.
- [ ] Entry Logic has 3 numbered steps: read conventions, check Active Context (non-empty → use as starting point; empty → seed question), do NOT explore files before understanding what engineer is building.
- [ ] Non-empty Active Context starts with: "I see you're working on [context]. Let me ask about [specific aspect]."
- [ ] Empty Active Context asks exactly one seed question: "In 1-2 sentences, what are you working on?"

### Finishing Workflow (Change 10)

- [ ] `skills/execution/SKILL.md` contains an "After All Steps Complete" section at the end.
- [ ] Presents exactly 3 options: merge to main locally, push and raise PR, keep branch as-is.
- [ ] Does not auto-merge or auto-push — waits for engineer's choice.
- [ ] Regardless of choice, includes session hygiene reminder: "Start a new chat. Use `/verify`."

### WORKFLOW.md Accuracy (Change 11)

- [ ] "Phase Review Checkpoints" section describes two-stage review (spec compliance, then code quality).
- [ ] "End-to-End Example" Phase 1 checkpoint (AUTH-456 scenario) is updated to show both review stages before engineer review.
- [ ] "Execution Modes" section references 2-5 minute step granularity instead of implying larger steps.
- [ ] "Cheat Sheet" entry for "My test is failing mid-execution" mentions the 3-attempt escalation threshold.
- [ ] "End-to-End Example" Step 6 includes the structured finishing choice (merge/PR/keep) instead of just "raise your PR".
- [ ] "Phase Review Checkpoints" section mentions the Verification Gate (claims require pasted evidence).

### Drift Control in copilot-instructions.md (Change 12)

- [ ] `copilot-instructions.md` contains a "Drift Control" section between Hard Rules and Conscious Skip Protocol.
- [ ] Drift Control contains exactly 6 rules:
  1. Reproduce the bug before proposing a fix
  2. Ask before guessing when information is missing
  3. State uncertainty explicitly — never present guesses as facts
  4. Do not fabricate APIs, file paths, or tool behaviors
  5. Verify the solution works after implementing it
  6. Read relevant existing code before suggesting or making modifications
- [ ] The section header includes a one-line rationale: "Reinforcement rules for behaviors that demonstrably drift in practice."

## Architecture / Design Decisions

### Why modify existing files, not create new ones

The Copilot skill system is file-based — each SKILL.md is loaded into context when
invoked. Adding new files means new concepts, new routing, new things to remember.
Adding sections to existing files means the enforcement is present exactly when the
skill is active, at the cost of a few extra tokens per invocation.

### Why not full rationalization tables

Superpowers uses extensive rationalization tables (excuse -> reality mappings) because
it serves thousands of users and needs to handle worst-case AI behavior. For personal
use, iron laws + hard gates achieve 80% of the enforcement at 20% of the token cost.
Rationalization counters can be added reactively if specific drift patterns emerge.

### Why 2-5 minute steps instead of 30 minute steps

The plan is consumed by subagents in phased execution. Each subagent gets only its
phase's steps. A 30-minute step requires judgment about what to do — a 2-5 minute
step is unambiguous. This is the single highest-leverage change because it improves
determinism at every downstream consumer: execution, TDD, verification.

### Why two-stage review instead of one

Spec compliance and code quality are different concerns with different failure modes.
Checking spec compliance first (does it match the plan?) is a fast binary filter —
if the implementation missed a step, there's no point reviewing code style. This
ordering prevents wasted review cycles.

### Why Drift Control in copilot-instructions.md

The 6 Drift Control rules are behavioral constraints (don't guess, don't fabricate,
verify your work) that apply to every phase, not just one skill. Placing them in
copilot-instructions.md means they're always in context alongside the Hard Rules.
They complement Hard Rules: Hard Rules are workflow gates (no code before plan),
Drift Control rules are behavioral gates (no guessing, verify your work).

## Files Changed

| File | Change Type | Description |
|---|---|---|
| `github/skills/tdd/SKILL.md` | Modify | Add iron law blockquote after frontmatter |
| `github/skills/debugging/SKILL.md` | Modify | Add iron law blockquote + escalation section |
| `github/skills/verification/SKILL.md` | Modify | Add iron law blockquote |
| `github/skills/execution/SKILL.md` | Modify | Add iron law, verification gate, two-stage review, skill chaining, finishing workflow |
| `github/skills/planning/SKILL.md` | Modify | Replace step granularity, add no-placeholder enforcement, add self-review loop |
| `github/skills/spec-writing/SKILL.md` | Modify | Add self-review loop |
| `github/skills/brainstorming/SKILL.md` | Modify | Replace entry logic with conditional Active Context check |
| `github/WORKFLOW.md` | Modify | Align guide text with changes 1-10 |
| `github/copilot-instructions.md` | Modify | Add Drift Control section (6 rules) |

**Files NOT changed:** setup/SKILL.md, conventions/SKILL.md, review/SKILL.md,
all agents (design, implementation, review), all prompts (10 files).

## Risks & Dependencies

- **Token budget risk:** ~1000 tokens added across 7 skills. Each skill is loaded
  independently, so the per-invocation cost increase is small (80-150 tokens per
  skill). Monitor Copilot context limits if skills grow further.
- **Over-enforcement risk:** Iron laws and hard gates could make the AI too rigid
  for edge cases. Mitigated by the Conscious Skip Protocol already in place — if
  a rule genuinely doesn't apply, the engineer states the skip explicitly.
- **Two-stage review overhead:** Adds one extra review pass per phase in phased
  execution. For a 3-phase plan, this is 3 extra spec-compliance checks. Acceptable
  tradeoff for catching plan-implementation mismatch before code quality review.
- **Granularity change in planning:** Existing plans written at 30-minute granularity
  won't match the new 2-5 minute standard. No migration needed — new plans follow the
  new rule, old plans still execute (just with coarser steps).

## Testing Strategy

Since this system has no automated tests (Markdown artifacts only), verification is
manual:

- **Per-skill review:** After each skill is modified, read it end-to-end and verify
  the new sections integrate naturally with existing content.
- **Dry run:** Pick a small feature and run through the full workflow (brainstorm ->
  spec -> plan -> execute -> verify -> review) using the updated skills. Check that:
  - Plan steps are 2-5 minutes each with code blocks
  - Execution invokes TDD/debugging skills via REQUIRED references
  - Phased review shows two stages before engineer checkpoint
  - Debugging escalates after 3 hypotheses
  - Verification gate catches unsupported completion claims
- **Regression check:** Verify the Quick Reference table in WORKFLOW.md still matches
  the actual phase/agent/prompt routing (unchanged, but confirm).
