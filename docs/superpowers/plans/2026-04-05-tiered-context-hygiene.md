# Tiered Context Hygiene & Token Efficiency Protocol — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a three-tier classification system to `~/.claude/CLAUDE.md` and a `session-tier` skill for mid-session overrides so that Claude matches effort to request complexity rather than running the full workflow pipeline on every task.

**Architecture:** Two artifacts — a `## Tier Classification` prose+YAML block appended to the global `CLAUDE.md` fires on every request at zero overhead; a standalone `~/.claude/skills/session-tier/SKILL.md` handles mid-session overrides and diagnostics only when explicitly invoked.

**Tech Stack:** Markdown only. No code, no build system, no dependencies.

---

## File Map

| Action | Path |
|--------|------|
| Modify | `~/.claude/CLAUDE.md` — append `## Tier Classification` section |
| Create | `~/.claude/skills/session-tier/SKILL.md` — new user-local skill |

---

### Task 1: Append Tier Classification to `~/.claude/CLAUDE.md`

**Files:**
- Modify: `~/.claude/CLAUDE.md`

- [ ] **Step 1: Verify the section does not already exist**

Run:
```bash
grep -n "Tier Classification" ~/.claude/CLAUDE.md
```
Expected: no output (zero matches). If a match is found, stop and inspect — someone already added the section; do not duplicate it.

- [ ] **Step 2: Read the current end of the file to confirm insertion point**

Run:
```bash
tail -5 ~/.claude/CLAUDE.md
```
Expected output (approximately):
```
## Communication
- Responses are concise. No trailing summaries of what was just done.
- No TaskCreate for tasks under 3 steps.
```

The new section appends after the last line of the file.

- [ ] **Step 3: Append the Tier Classification section**

Open `~/.claude/CLAUDE.md` with the Edit or Write tool and append the following block to the end of the file (after a blank line):

```markdown

## Tier Classification

On every request, before doing any work:
1. Classify the request and propose a tier: `"Tier: <name> — <one sentence on what I'll do/skip>. Proceed?"`
2. Wait for confirmation. User may confirm or name a different tier to override.
3. Stay within the confirmed tier's constraints for the full task.

The tier constraints in the `tier-config` block define the upper bounds on turns,
tool calls, and token cost per task. Claude must stay within those limits once a
tier is confirmed.

```yaml
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
```
```

> **Note:** The yaml fence above must appear as a literal triple-backtick code block inside the markdown file (not escaped). The final file should contain the raw text ` ```yaml ` on its own line.

- [ ] **Step 4: Verify the append**

Run:
```bash
grep -A 20 "## Tier Classification" ~/.claude/CLAUDE.md
```
Expected: the full section including the yaml block exactly as written in Step 3.

Also confirm no existing sections were disturbed:
```bash
grep "^## " ~/.claude/CLAUDE.md
```
Expected output:
```
## Session Bootstrap
## File References
## Web Research
## Agent Dispatch
## Communication
## Tier Classification
```

- [ ] **Step 5: Commit**

```bash
git -C ~/.claude add CLAUDE.md
git -C ~/.claude commit -m "feat: add tier classification protocol to CLAUDE.md"
```

If `~/.claude` is not a git repo, skip the commit step and note it in your handoff.

---

### Task 2: Create the `session-tier` skill

**Files:**
- Create: `~/.claude/skills/session-tier/SKILL.md`

- [ ] **Step 1: Verify the directory does not already exist**

Run:
```bash
ls ~/.claude/skills/session-tier/ 2>&1
```
Expected: `No such file or directory`. If the directory exists, inspect its contents before proceeding — do not overwrite silently.

- [ ] **Step 2: Create the skill directory and file**

Create `~/.claude/skills/session-tier/SKILL.md` with the following content:

```markdown
---
name: session-tier
description: Use to override the active tier mid-session or show current tier constraints. Commands: set <quick|focused|full>, show, reset.
---

# Session Tier

## Purpose

Mid-session override and diagnostics for the tier classification protocol. Does not classify requests on its own — use only for explicit overrides and status checks.

## Commands

### `/session-tier set <quick|focused|full>`

Override the active tier immediately. Suppresses automatic tier proposals for all subsequent requests in the session.

Respond with exactly one line:
`"Active tier: <Name>. Constraints: max <N> turns, <N> tools, <N> cost."`

Constraints by tier:
- **quick:** max 1 turn, 0 tools, 100 cost
- **focused:** max 3 turns, 3 tools, 500 cost
- **full:** max 10 turns, 10 tools, 2000 cost

**Invalid input:** If the requested tier is not one of `quick`, `focused`, `full`, respond with one line and do not change state:
`"Unknown tier '<value>'. Valid tiers: quick, focused, full."`

### `/session-tier show`

Print the current active tier and the full `tier-config` block:

\```yaml
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
\```

If no override is active, prepend: `"No active override. Auto-classification is active."`

### `/session-tier reset`

Clear any active override. Auto-classification resumes from the next request onward.

Respond with exactly one line: `"Override cleared. Auto-classification resumes."`

## Precedence

An override set via `/session-tier set` takes effect immediately and suppresses automatic tier proposals for all subsequent requests until `/session-tier reset` is called.
```

> **Note:** The `\``` ` escapes above are only to prevent nesting inside this plan document. When writing the actual SKILL.md, use unescaped triple backticks for the yaml fence.

- [ ] **Step 3: Verify the file was created correctly**

Run:
```bash
cat ~/.claude/skills/session-tier/SKILL.md
```
Check:
- Frontmatter block is present with `name: session-tier` and `description:`
- All three commands (`set`, `show`, `reset`) are present
- Invalid input behavior is documented
- The yaml `tier-config` block is present and matches the values in CLAUDE.md

Run:
```bash
grep -c "session-tier" ~/.claude/skills/session-tier/SKILL.md
```
Expected: at least 3 matches (name field, show section header, set section header).

- [ ] **Step 4: Commit**

```bash
git -C ~/.claude add skills/session-tier/SKILL.md
git -C ~/.claude commit -m "feat: add session-tier skill for mid-session tier overrides"
```

If `~/.claude` is not a git repo, skip the commit step.

---

### Task 3: Smoke-test in a live session

> These steps require opening a fresh Claude Code session — they cannot be automated.

- [ ] **Step 1: Start a new Claude Code session**

Close the current session and open a new one (so CLAUDE.md is re-loaded).

- [ ] **Step 2: Verify tier proposal on a simple request**

Type: `what is 2 + 2`

Expected: Claude proposes `Tier: Quick —` before answering. Confirm with "yes" or "go". Claude answers without using any tools.

- [ ] **Step 3: Verify tier proposal on a complex request**

Type: `add a new authentication module to this project`

Expected: Claude proposes `Tier: Full —` before answering. You do not need to confirm — cancel the request after verifying the proposal appears.

- [ ] **Step 4: Test `/session-tier show`**

Invoke the skill: `/session-tier show`

Expected output (no active override):
```
No active override. Auto-classification is active.
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
```

- [ ] **Step 5: Test `/session-tier set focused`**

Invoke: `/session-tier set focused`

Expected: `"Active tier: Focused. Constraints: max 3 turns, 3 tools, 500 cost."`

Then ask a simple question. Expected: **no tier proposal** — override suppresses auto-classification.

- [ ] **Step 6: Test `/session-tier set bogus`**

Invoke: `/session-tier set bogus`

Expected: `"Unknown tier 'bogus'. Valid tiers: quick, focused, full."` and no state change.

- [ ] **Step 7: Test `/session-tier reset`**

Invoke: `/session-tier reset`

Expected: `"Override cleared. Auto-classification resumes."`

Then ask a simple question. Expected: tier proposal reappears.

---

## Spec Coverage Check

| Spec requirement | Task |
|-----------------|------|
| Every request receives a tier proposal before any work begins | Task 1 (CLAUDE.md policy) + smoke test Step 2–3 |
| User confirms with one word or overrides by naming a tier | Task 1 (CLAUDE.md prose) |
| Claude stays within tier constraints for the full task | Task 1 (CLAUDE.md policy + yaml block) |
| `/session-tier set focused` suppresses further proposals | Task 2 + smoke test Step 5 |
| `/session-tier show` returns current tier + config block | Task 2 + smoke test Step 4 |
| `/session-tier reset` re-enables auto-classification | Task 2 + smoke test Step 7 |
| Invalid tier input returns error, no state change | Task 2 + smoke test Step 6 |
| Existing CLAUDE.md behavior is unaffected | Task 1 Step 4 (section headers check) |
