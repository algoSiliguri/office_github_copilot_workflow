---
ticket: WORKFLOW-EVOLUTION-01
phase: spec
created: 2026-04-17
status: draft
source: conversational — brainstorm session 2026-04-17
---

# Spec: WORKFLOW-EVOLUTION-01 — Copilot Workflow Evolution

## Problem Statement

The GitHub Copilot workflow system was designed under low-context, timeout-sensitive constraints.
The binary execution threshold (≤3 files inline, >3 files sub-agent), full conventions
re-embedding per phase, and optional retrieval enforcement are structural mismatches for a
high-context, premium-model environment. These mismatches force unnecessary sub-agent overhead,
waste tokens on redundant embedding, leave coverage confidence as a documented-but-ignored field,
and provide no structure for inline execution at higher file counts.

## Solution Approach

Evolve five core mechanisms — execution routing, phase execution discipline, sub-agent prompt
efficiency, coverage confidence enforcement, and retrieval integration — so they behave correctly
under current operating conditions and remain principled as the system grows. Accompany this with
targeted removal of vestigial elements and a documentation restructure that separates usage
guidance from system design.

---

## Requirements

### R1 — Adaptive Execution Mode Selection

- [ ] The planner selects execution mode using file count as the **initial signal**, not the
  final decision. Mode may be overridden based on step complexity, file coupling, and iteration
  likelihood.
- [ ] Default routing baseline:
  - ≤5 files AND low risk → `inline`
  - 6–12 files OR high risk/uncertainty → `phased-inline`
  - >12 files → `phased-subagent`
- [ ] Override rules (applied after baseline):
  - ≤5 files with high risk/uncertain steps → escalate to `phased-inline`
  - 6–12 tightly coupled, well-understood files → downgrade to `inline` if complexity is low
  - >12 clearly trivial changes (e.g. rename across files) → may use `phased-inline`
- [ ] The plan must include a one-sentence mode justification on the `> **Execution mode:**` line:
  `> **Execution mode:** phased-inline — 8 files, auth module changes have high iteration risk`
- [ ] Risk/complexity signals the planner must explicitly assess before setting mode:
  - Does any step touch a module flagged `active` or `high-risk` in the codebase index?
  - Does any step require resolving a decision conflict flagged during planning?
  - Are more than 3 steps in a phase marked with "or equivalent" / "depending on current state"?
  - If yes to any: escalate mode by one tier.

### R2 — Phased-Inline as First-Class Execution Mode

- [ ] `phased-inline` executes phases sequentially in the current session. No sub-agents.
- [ ] `phased-inline` is UX-identical to `phased-subagent`: same phase start format, same
  checkpoint format, same gate discipline. The engineer cannot distinguish the modes from
  the output.
- [ ] Phase start announcement (both `phased-inline` and `phased-subagent`):
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase [N] of [M] — [Phase name] — [N files] / [N steps]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- [ ] Phase checkpoint after completion:
  ```
  Phase [N] complete — [Phase name]

  Files changed:
    + [file] (created)
    ~ [file] (modified)

  [Stage 1] Spec compliance: PASS  ← show this line when passing
  [Stage 1] Spec compliance: FAIL — [missing file or unlisted change]  ← show this line when failing

  [Stage 2] Code quality: PASS  ← show this line when passing
  [Stage 2] Code quality: FAIL — [finding: what + where]  ← show this line when failing

  Test output:
  [pasted output]

  Review:
  [exact questions from plan's Engineer review prompt]

  Type `continue` for Phase [N+1], or describe a concern.
  ```
  Show exactly one Stage 1 line and one Stage 2 line — the applicable variant only.
- [ ] Stage detail rule: PASS is one line. FAIL is one line including the finding (what + where).
  No explanation, no suggestion — the engineer decides what to do with it.
- [ ] On failure: "Phase [N] failed — [test name or compliance finding]. Use `/debug`. Type
  `retry phase [N]` when fixed." No auto-retry.
- [ ] Gate is hard: the agent does not proceed to the next phase without explicit `continue`.
- [ ] Amendment and discovery tracking applies in `phased-inline` identically to inline and
  sub-agent modes.

### R3 — Lean Sub-Agent Conventions Injection

- [ ] The `phased-subagent` prompt replaces full `conventions/SKILL.md` embedding with a
  **minimal conventions summary** extracted at dispatch time:
  ```
  --- CONVENTIONS ---
  Test: [command]
  Commit: [format]
  Lint: [command or "none"]
  Ticket: [format]
  --- END CONVENTIONS ---
  ```
- [ ] The execution skill dynamically injects additional convention details when a phase step
  requires them. Detection rule: scan each step's text for the following keyword patterns.
  When matched, inject the named conventions section (if it exists in `conventions/SKILL.md`):
  - Words: "error", "exception", "throws", "catch", "validate", "validation" → `## Error Handling`
  - Words: "endpoint", "request", "response", "API", "contract", "status code" → `## API Conventions`
  - Words: "migration", "schema", "table", "query", "database", "model" → `## Data Conventions`
  - Any framework name that appears as a section header in conventions (exact match) → that section
  - Default: no injection beyond the minimal summary
- [ ] Injected content is appended after `--- END CONVENTIONS ---` with a label:
  `--- INJECTED: [section name] ---`
- [ ] If `conventions/SKILL.md` does not contain a matching section for an injected keyword:
  no injection. Do not fail or warn.
- [ ] The 10-rule `RULES:` block in the sub-agent prompt is collapsed to 8 rules. Rules 6
  (TDD) and 7 (debugging) are merged into one: "Follow TDD for new logic (RED→GREEN→REFACTOR);
  use systematic debugging for failures (reproduce→isolate→hypothesise→verify→fix)."

### R4 — Coverage Confidence as Hard Constraint

- [ ] The execution skill reads `Coverage confidence:` from the context packet before any step.
  Behavior is mandatory, not advisory:
  - `high` → The agent is **prohibited** from loading files outside the context packet.
    Any step that would require a file read beyond the packet must stop and report:
    "Step [N] requires reading [file], which is outside the context packet. Coverage is HIGH.
    Should I expand context or rephrase the step to work within the packet?"
  - `medium` → Controlled one-hop expansion is allowed. The agent may read files
    referenced by packet modules, but must not scan broadly.
  - `low` → Expansion is **required**. The agent must acknowledge the gap at phase start:
    "Coverage confidence is LOW for this phase. I will use full codebase search as needed."
    The Codebase Search Protocol is available without restriction.
- [ ] Coverage confidence level is surfaced at the phase/session start in all modes:
  `Context: [high|medium|low] coverage — [behavior description]`
- [ ] If no context packet exists for a phase: treat as `low` confidence. Apply the LOW behavior.
- [ ] Coverage confidence enforcement applies in `inline`, `phased-inline`, and
  `phased-subagent` modes identically.

### R5 — Inline Mode Soft Checkpoints

- [ ] When executing in `inline` mode with ≥6 steps total, steps are grouped into logical
  units by file (all steps on one file form one group) or by natural step dependency.
- [ ] After each group completes, the agent shows a soft checkpoint:
  ```
  — [group name, e.g. "RateLimiter.java"] — [N steps complete]
  Tests: [PASS / FAIL — summary line]
  ```
- [ ] Soft checkpoints are informational — no `continue` gate. The agent proceeds automatically.
- [ ] After all steps complete, a **hard checkpoint** is shown with the same format as
  the `phased-inline` checkpoint (files changed, Stage 1, Stage 2, test output, finishing
  options). This is the only gate in inline mode.
- [ ] For inline plans with <6 steps: no soft checkpoints. Hard checkpoint at the end only.

### R6 — Retrieval as Mandatory at Defined Entry Points

- [ ] **Planning phase** (`planning/SKILL.md`): The intelligence retrieval step is already
  present. Change its status from conditional to mandatory:
  - "If index absent or maturity = low: skip" remains valid as the skip condition.
  - Add: if index exists at any maturity level above `low`, retrieval **must run**. A skip
    without justification blocks the plan from being written.
  - The planner must note at the top of the plan: `Retrieval: ran | skipped — [reason]`
- [ ] **Execution phase** (`execution/SKILL.md`): The context packet check is already present.
  Change its framing from optional to mandatory:
  - "If not found: proceed without" is replaced with: "If not found: explicitly note in the
    session — 'No context packet for phase [N]. Proceeding with full codebase search.' This
    is not silent — the absence is acknowledged."
  - The agent must not silently skip the context packet check.
- [ ] **Brainstorming phase** (`brainstorming/SKILL.md`): The intelligence scan already runs
  silently. Change: when candidates are found, surface them proactively before the first
  clarifying question (current behavior). When no candidates are found, explicitly say:
  "Index has no match for this ticket area — starting without codebase context."
  This makes retrieval absence visible, not invisible.
- [ ] Retrieval enforcement does not apply to spec-writing, TDD, debugging, or verification
  phases — these operate on artifacts already produced.

### R7 — Vestigial Element Removal

- [ ] Remove `allowed-tools:` line from frontmatter in:
  `execution/SKILL.md`, `verification/SKILL.md`, `review/SKILL.md`, `planning/SKILL.md`,
  `brainstorming/SKILL.md`
- [ ] Remove `Recommended: Standard` / `Recommended: Premium` from handoff sections in:
  `execution/SKILL.md`, `planning/SKILL.md`, `spec-writing/SKILL.md`, `setup/SKILL.md`,
  `debugging/SKILL.md`, `brainstorming/SKILL.md`, `verification/SKILL.md`
- [ ] Remove `Apply context hygiene summary, then proceed.` from all skills. Replace with:
  `Apply context hygiene before closing this chat.` — a self-contained instruction.
- [ ] Remove the "Model Routing" section from `WORKFLOW.md` (current lines 77–112).
- [ ] Before removing any element: verify that no skill's decision logic references it as
  a load-bearing signal. Specifically: check that `Recommended:` is not parsed by any agent
  file or prompt file as an instruction. If it is, update the agent/prompt file first.

### R8 — Simplified Handoff Text

- [ ] Default handoff format across all skills:
  ```
  Next: `/[skill] [artifact-path]` in a new chat.
  ```
- [ ] Optional hint: if the next skill requires a non-obvious input format, add one line:
  ```
  Note: [brief clarification — one sentence only]
  ```
- [ ] The hint is added only when the next skill's input is ambiguous to a developer who
  hasn't used the workflow recently. It is never added as a default.
- [ ] Handoff text for skills with no artifact output (e.g. brainstorming → spec-writing):
  ```
  Next: `/write-spec [brainstorm-path]` in a new chat.
  ```

### R9 — Documentation Restructure

- [ ] `WORKFLOW.md` is rewritten as a practical usage guide. Contents:
  - Quick reference table (phases, commands, outputs — no model column)
  - Setup (one-time per repo)
  - Phase sequence with explicit skip guidance ("when skipping is legitimate")
  - Session hygiene: one concise paragraph — start new chat per phase, why it matters
  - Common situations cheat sheet
  - One condensed end-to-end example (≤40 lines)
  - No execution internals, no sub-agent mechanics, no threshold logic
- [ ] `ARCHITECTURE.md` is created. Contents:
  - Execution mode decision logic (three-tier model, override rules, justification requirement)
  - Phased-inline mechanism (how it differs from sub-agent at the implementation level)
  - Sub-agent dispatch protocol (minimal conventions summary, dynamic injection rules)
  - Coverage confidence constraint table (HIGH/MEDIUM/LOW behaviors)
  - Retrieval integration points (which phases enforce retrieval and how)
  - Review checkpoint anatomy (two-stage review, stage detail rules, gate protocol)
  - Session hygiene protocol (canonical definition — skills reference this, not duplicate it)
  - Sync policy: "Updated in the same commit as any skill that changes its decision logic.
    WORKFLOW.md is not updated for internal mechanism changes."
  - Evolution principles: "Mechanisms replace rules. Simpler systems that scale. Every
    constraint must be enforceable as an artifact or a file-based check — not a convention."
- [ ] WORKFLOW.md and ARCHITECTURE.md both carry an `updated:` header. When a skill PR
  changes decision logic, the PR description must state which ARCHITECTURE.md section was updated.

---

## Architecture / Design Decisions

**Execution routing lives in the planner, not the executor.**
The execution skill reads the annotated mode and runs it. The planner sets the mode with
justification. This separation means the execution skill stays simple; routing intelligence
lives where the plan is made.

**Phased-inline is the default mode for most plans.**
For typical feature plans (6–12 files), phased-inline eliminates sub-agent overhead while
preserving checkpoint discipline. Sub-agent mode becomes a deliberate choice for large or
genuinely context-heavy plans, not the default for anything over 3 files.

**Lean-by-default conventions injection is pull-based, not push-based.**
The sub-agent does not receive all conventions and decide what's relevant. The parent session
scans phase steps and pushes only the relevant sections. This keeps sub-agent prompts lean
without requiring sub-agents to make judgment calls about what they need.

**Coverage confidence is a constraint, not metadata.**
Changing it from an advisory field to a behavioral constraint closes the gap between
what the context packet knows and what the agent does. HIGH confidence becomes a boundary
that the agent cannot cross silently.

**Retrieval absence must be visible.**
Silent skips (no index → proceed silently) hide information gaps. Making absence explicit
at phase start gives the engineer a signal that context quality is lower than usual.

_Decision check: index not available — 2026-04-17_

---

## Design Rationale

- **Chosen:** Adaptive routing with file count as baseline signal + override rules, because
  file count is a reliable proxy but not sufficient for risk-adjusted decisions.
- **Rejected: Pure file-count thresholds** — a static number cannot distinguish a 4-file
  high-risk auth change from a 4-file low-risk config update.
- **Rejected: Fully dynamic routing (no baselines)** — without a default, every plan
  requires deliberate mode reasoning; baselines make the common case automatic and overrides
  handle exceptions.
- **Chosen:** Phased-inline as a first-class mode, not a workaround, because it makes
  checkpoint discipline available without sub-agent cost for the majority of plans.
- **Rejected: Raising the inline threshold without adding structure** — a higher threshold
  with no checkpoints trades one problem (sub-agent overhead) for another (opaque execution).
- **Chosen:** Lean conventions summary with keyword-triggered injection, because it preserves
  efficiency for most phases while ensuring completeness for phases that need specific patterns.
- **Rejected: Fixed minimal template for all sub-agents** — some phases genuinely need
  framework-specific conventions; a fixed template would miss these.
- **Chosen:** Coverage confidence as a hard constraint, because a documented advisory field
  that agents ignore is worse than no field — it creates false confidence in the system design.

---

## Risks & Dependencies

- Removing `Recommended:` hints may create confusion if any agent file (design.agent.md,
  implementation.agent.md, review.agent.md) currently uses this line as a routing signal.
  Must audit agent files before removal.
- The dynamic conventions injection requires scanning phase step text for keywords. If steps
  are too terse (e.g. "implement error handling"), keyword matching may fail to inject. The
  risk is under-injection rather than over-injection — acceptable, since the base summary
  always exists.
- Phased-inline accumulates tool call history across all phases. For plans near the 12-file
  upper boundary, late phases may have degraded context focus. This is not a concern at 200k
  context for current plan sizes; revisit if plans regularly exceed 40+ total steps.
- ARCHITECTURE.md requires disciplined maintenance. If it drifts from skill implementations,
  it becomes worse than no architecture doc. The sync policy (same-commit requirement) must
  be enforced by convention, not automation.

---

## Testing Strategy

- **Unit:** Each mechanism change is verifiable by inspecting the skill file for:
  - Presence of mode justification line in planning output format
  - Presence of phase start separator format in execution skill
  - Correct coverage confidence behavior table
  - Absence of `allowed-tools:`, `Recommended:`, and `Apply context hygiene summary`
- **Integration:** Run `/execute-plan` on a 4-file test plan and confirm phased-inline
  checkpoints appear with correct format; confirm no sub-agent dispatch occurs.
- **Integration:** Run `/execute-plan` on a 15-file test plan and confirm sub-agent is
  dispatched with lean conventions summary (not full text).
- **Integration:** Run `/write-plan` and confirm mode annotation includes justification text.
- **Manual:** Verify WORKFLOW.md no longer contains model routing table or sub-agent
  implementation details. Verify ARCHITECTURE.md exists and covers all listed sections.
- **Regression:** Confirm review/SKILL.md, verification/SKILL.md, and tdd/SKILL.md are
  unchanged (these skills are not in scope).
