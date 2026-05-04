# Global CLAUDE.md Constrained Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `~/.claude/CLAUDE.md` with a structurally improved version that preserves all 14 existing behavioral rules while adding context hygiene, drift control, self-healing, and meta rules.

**Architecture:** Single-file replacement with pre/post validation. The new file content is fully specified in the design spec (Section 5). Implementation is: backup → validate parity → write → verify.

**Tech Stack:** Shell (backup/line count), CLAUDE.md (markdown)

---

## File Structure

| File | Action |
|---|---|
| `~/.claude/CLAUDE.md` | Replace with new content |
| `~/.claude/CLAUDE.md.bak.2026-04-05` | Create backup of current file |

No other files are created or modified. The spec explicitly lists what is NOT changed (workspace CLAUDE.md, project CLAUDE.md, CLAUDE.local.md, .superpowers-config.yml, specs, plans, skills).

---

### Task 1: Backup Current File

**Files:**
- Read: `~/.claude/CLAUDE.md`
- Create: `~/.claude/CLAUDE.md.bak.2026-04-05`

- [ ] **Step 1: Create timestamped backup**

```bash
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak.2026-04-05
```

- [ ] **Step 2: Verify backup exists and matches original**

Run: `diff ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak.2026-04-05`
Expected: No output (files are identical)

---

### Task 2: Pre-Write Parity Check

Before replacing the file, verify all 14 rules from the current file are present in the new content. This is a manual review step.

- [ ] **Step 1: Verify all 14 rules are mapped in the new content**

Check each rule from the current file against the new content (from spec Section 5):

| # | Current Rule (from `~/.claude/CLAUDE.md`) | New Location | Status |
|---|---|---|---|
| 1 | Session bootstrap (.superpowers-config.yml) | Session Bootstrap section | ✓ |
| 2 | Never re-read files | Context Hygiene: "Do not re-read a file already read this session — unless the file has changed or the cached content is insufficient" | ✓ softened |
| 3 | Grep/Glob before Agent/Read | Context Hygiene: "Start with Grep/Glob for any search task" | ✓ |
| 4 | Max 3 files for Grep-answerable questions | Context Hygiene: "Do not read more than 3 files to answer a question answerable with Grep" | ✓ |
| 5 | No WebFetch/WebSearch unless asked | Context Hygiene: preserved verbatim | ✓ |
| 6 | One search query per topic | Context Hygiene: "One search query per topic — retry only if the first returned zero results or clearly irrelevant results" | ✓ softened |
| 7 | Inline for ≤3 files | Context Hygiene file threshold + Decision & Execution reference | ✓ |
| 8 | Sub-agents for 4+ files | Context Hygiene file threshold + Decision & Execution reference | ✓ |
| 9 | Max 2 review cycles | Decision & Execution: "Maximum 2 review cycles per task" | ✓ |
| 10 | Concise responses | Token Efficiency: "Default to the shortest correct response" | ✓ merged |
| 11 | No trailing summaries | Token Efficiency: preserved | ✓ |
| 12 | No TaskCreate under 3 steps | Token Efficiency: preserved | ✓ |
| 13 | Tier classification protocol | Tier Classification: preserved and enhanced with trivial bypass | ✓ |
| 14 | Tier YAML block | Tier Classification: preserved verbatim | ✓ |

All 14 rules accounted for. Proceed.

---

### Task 3: Write the New CLAUDE.md

**Files:**
- Modify: `~/.claude/CLAUDE.md` (full replacement)

- [ ] **Step 1: Replace file content**

Write the following exact content to `~/.claude/CLAUDE.md`:

```markdown
# Operating Mode

Optimize for correctness, minimalism, and clarity. Every rule must change
behavior — otherwise remove it. Default to action over explanation.

## Session Bootstrap

At session start (run once), check for `.superpowers-config.yml` walking up
from the project root.

- If found → read and apply its rules before any other action
- Do not re-check or re-read during the session unless explicitly required
- If conflicts arise → local config overrides global rules

## Context Hygiene

Treat context as a scarce resource — minimize reads, tokens, and tool usage.
Prefer the cheapest tool that answers the question.

**File threshold:** ≤3 files = inline work. ≥4 files = use sub-agents unless
the task is trivial. This threshold is referenced by other sections — do not
duplicate it.

- Start with Grep/Glob for any search task; use Read or agents only if insufficient
- Do not re-read a file already read this session — unless the file has changed
  or the cached content is insufficient
- Do not read more than 3 files to answer a question answerable with Grep
- No WebFetch/WebSearch unless the user explicitly asks or the task requires
  current version info unavailable in training data
- One search query per topic — retry only if the first returned zero results
  or clearly irrelevant results
- Do not carry forward irrelevant context between tasks — actively reset or
  summarize when switching focus

## Token Efficiency

Default to the shortest correct response. Expand only when explicitly asked
or required for correctness.

- No trailing summaries of what was just done
- Do not restate the user's input unless necessary for clarity or disambiguation
- Prefer bullet points over paragraphs
- Prefer diffs/edits over full file rewrites for existing files
- One sentence > three sentences when meaning is preserved
- Do not explain obvious steps or decisions unless asked
- No TaskCreate for tasks under 3 steps

## Tier Classification

On each request, before doing any non-trivial work:

1. Classify the request and propose a tier:
   `"Tier: <name> — <one sentence on what I'll do/skip>. Proceed?"`
2. Wait for confirmation. User may confirm or override the tier.
3. Stay within the confirmed tier's constraints for the full task.

Skip classification for clearly trivial, single-step requests requiring no tools.

```yaml
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
```

## Decision & Execution

- Before creating anything → check for existing patterns, files, or utilities
  to reuse
- Prefer minimal viable solution over speculative design
- Ask clarifying questions when ambiguity exists — do not assume missing
  information

- Inline execution for tasks within the file threshold (see Context Hygiene)
- Use sub-agents for tasks exceeding the file threshold unless the task is trivial

- Maximum 2 review cycles per task (implement → review → revise) — if not
  resolved, stop and ask the user

- Validate changes before concluding the task
- Stop when the task is complete — no unsolicited additions, refactors,
  or cleanups

## Drift Control

Reinforcement rules for behaviors that demonstrably drift in practice.
These overlap with defaults but are included because failure cost is high.

- Reproduce the bug before proposing a fix
- Ask before guessing when information is missing
- State uncertainty explicitly — never present guesses as facts
- Do not fabricate APIs, file paths, or tool behaviors
- Verify the solution works after implementing it — do not assume correctness
- Read relevant existing code before suggesting or making modifications

## Self-Healing System

This file evolves through accumulated learning, not reactive edits.

**During sessions — capture observations:**
- When a rule causes friction, is ambiguous, or fails to prevent a mistake →
  write a one-line observation to memory (type: feedback)
- When a pattern begins to repeat (≥2 instances within or across sessions) →
  write a one-line observation to memory (type: feedback)
- Observations must be concise, de-duplicated, and pattern-focused — never
  promote one-off issues

**On explicit trigger — synthesize improvements:**
When the user invokes `/improve-claude-md` or `/synthesize-learnings`:

1. Review all accumulated feedback memories
2. De-duplicate similar observations and identify patterns observed ≥3 times
   OR that prevent high-cost mistakes
3. Prioritize recent patterns; older patterns require stronger justification
4. Propose changes using this format:

   CHANGE TYPE: Add | Modify | Remove
   SECTION: <section name>
   PATTERN COUNT: <number of observations, or "high-cost prevention">
   JUSTIFICATION: <one line>
   PROPOSED CHANGE: <exact text>

5. Prefer removing weak rules over adding new ones
6. Never directly modify this file without user approval
7. Do not batch or hide changes — all proposals must be explicit and reviewable

**Promotion threshold:**
A rule is only added if it appears ≥3 times across sessions OR prevents a
high-cost mistake. One-off issues are never promoted.

## Meta Rules

- This file is a living system — prefer evolution over accumulation
- Total line count must stay within 80–150 lines
- Every rule must have clear behavioral impact — remove rules that don't
  change behavior
- Prefer fewer, stronger rules over more rules
- Prefer replacing weaker rules over adding new ones
- When two rules overlap → merge into one or delete the weaker
- Rules must be specific and testable — avoid vague or descriptive guidance
- New rules require justification: ≥3 observed patterns or high-cost prevention
- Periodically review and prune low-value or redundant rules
- No project-specific assumptions — everything here must be globally applicable
```

---

### Task 4: Post-Write Verification

**Files:**
- Read: `~/.claude/CLAUDE.md`

- [ ] **Step 1: Verify line count is within 80–150 lines**

Run: `wc -l ~/.claude/CLAUDE.md`
Expected: A number between 80 and 150 (spec target is ~112 lines)

- [ ] **Step 2: Verify all 8 sections are present**

Run: `grep -c '^##' ~/.claude/CLAUDE.md`
Expected: 8 (Session Bootstrap, Context Hygiene, Token Efficiency, Tier Classification, Decision & Execution, Drift Control, Self-Healing System, Meta Rules)

- [ ] **Step 3: Verify file threshold is stated exactly once**

Run: `grep -c 'File threshold' ~/.claude/CLAUDE.md`
Expected: 1

- [ ] **Step 4: Verify Drift Control has exactly 6 rules**

Run: `grep -c '^- ' ~/.claude/CLAUDE.md | head -1` won't work — instead count manually in the Drift Control section.

Run: `sed -n '/^## Drift Control/,/^## /p' ~/.claude/CLAUDE.md | grep -c '^- '`
Expected: 6

- [ ] **Step 5: Verify tier YAML block is present**

Run: `grep 'tier-config' ~/.claude/CLAUDE.md`
Expected: `# tier-config`

- [ ] **Step 6: Verify trivial-request bypass is present**

Run: `grep 'Skip classification' ~/.claude/CLAUDE.md`
Expected: `Skip classification for clearly trivial, single-step requests requiring no tools.`

- [ ] **Step 7: Verify self-healing trigger commands are present**

Run: `grep 'improve-claude-md\|synthesize-learnings' ~/.claude/CLAUDE.md`
Expected: Both `/improve-claude-md` and `/synthesize-learnings` appear

- [ ] **Step 8: Verify no project-specific assumptions**

Run: `grep -i 'office\|MOE\|copilot\|superpowers' ~/.claude/CLAUDE.md`
Expected: No output (no project-specific references)

- [ ] **Step 9: Commit**

```bash
git add ~/.claude/CLAUDE.md
git commit -m "refactor: rewrite global CLAUDE.md with structural improvements

Constrained rewrite preserving all 14 existing rules while adding:
- Context hygiene with single file threshold
- Token efficiency rules
- Drift control section (6 rules)
- Self-healing system (memory-backed observation + synthesis)
- Meta rules for non-bloat enforcement
- Trivial-request bypass for tier classification"
```

Note: If `~/.claude/` is not in a git repo, skip the commit step. The backup file serves as the rollback mechanism.

---

## Success Criteria Checklist

These map 1:1 to the spec's Section 8:

| Criterion | Verified In |
|---|---|
| All 14 original rules preserved | Task 2 (parity check) |
| File is 80–150 lines | Task 4, Step 1 |
| Every rule is trigger→action or constraint format | Task 2 (by inspection of spec content) |
| File threshold stated once, referenced elsewhere | Task 4, Step 3 |
| Drift Control has exactly 6 rules | Task 4, Step 4 |
| Self-Healing captures observations to memory | Task 4, Step 7 (trigger commands present) |
| `/improve-claude-md` triggers synthesis | Task 4, Step 7 |
| Meta Rules enforce non-bloat | Present in file content (line count constraint, justification requirement) |
| Tier classification skips trivial requests | Task 4, Step 6 |
| No project-specific assumptions | Task 4, Step 8 |
