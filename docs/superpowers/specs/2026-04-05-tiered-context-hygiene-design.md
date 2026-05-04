# Design Spec: Tiered Context Hygiene & Token Efficiency Protocol

**Date:** 2026-04-05
**Scope:** Generic — applies to every project, every session, every plugin
**Type:** New protocol — policy layer + operational skill

---

## 1. Problem Statement

Full agentic workflows (brainstorm → plan → execute → verify → review) are the right way
to work, but they consume premium quota fast. Simple requests trigger the same heavyweight
pipeline as complex features. There is no mechanism to match effort to complexity — every
session starts at full cost and burns through quota before meaningful work is done.

**Core tension:** full workflow quality vs sustainable token usage across a daily quota.

---

## 2. Solution: Three-Tier Classification + Skill Override

Two artifacts:

1. **Policy layer** — tier definitions baked into `~/.claude/CLAUDE.md` as prose rules +
   a machine-parsable YAML block. Fires automatically on every request, zero overhead.

2. **Operational skill** — `session-tier` skill for mid-session overrides and diagnostics.
   Loaded only when needed.

---

## 3. Tier Definitions

| Tier | Behavior | When to use |
|---|---|---|
| **Quick** | Direct answer, no tools | Factual questions, simple lookups, one-liners |
| **Focused** | Targeted tool loop (≤3 tools, ≤3 turns) | Debugging, small edits, search + answer tasks |
| **Full** | Complete pipeline: brainstorm → plan → execute → verify → review | New features, multi-file changes, design decisions |

### Constraints (authoritative)

```yaml
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
```

`max_cost` is a relative token budget per task (not a hard API limit). The tier constraints
define upper bounds on turns, tool calls, and token cost per task. Claude must stay within
those limits once a tier is confirmed.

---

## 4. Tier Proposal Protocol

On every request, before any work:

1. Classify the request complexity
2. Propose a tier with one-line summary:
   `"Tier: Focused — I'll search 2–3 files and answer directly, no skill pipeline. Proceed?"`
3. Wait for user confirmation
   - User says "yes", "go", or similar → proceed in proposed tier
   - User names a different tier ("Quick", "Full") → switch to that tier, proceed
4. Stay within the confirmed tier's constraints for the full duration of the task

---

## 5. `session-tier` Skill

**Location:** `~/.claude/skills/session-tier/SKILL.md`

**Purpose:** Mid-session override and diagnostics only. Does not classify requests or
carry any global behavior. Loaded only when explicitly invoked.

### Commands

**`/session-tier set <quick|focused|full>`**
Overrides the active tier immediately. Suppresses automatic tier proposals for all
subsequent requests in the session. Claude acknowledges with one line:
`"Active tier: Focused. Constraints: max 3 turns, 3 tools, 500 cost."`

**`/session-tier show`**
Prints the current active tier and the full `tier-config` block.

**`/session-tier reset`**
Clears any active override. Auto-classification resumes from the next request onward.

**Invalid input:**
If the requested tier is not one of `quick`, `focused`, or `full`, return a one-line
error and do not change state:
`"Unknown tier '<value>'. Valid tiers: quick, focused, full."`

### Precedence

An override set via `/session-tier set` takes effect immediately and suppresses
automatic tier proposals for all subsequent requests until `/session-tier reset` is called.

---

## 6. `~/.claude/CLAUDE.md` Changes

A new **Tier Classification** section is appended to the existing file. Existing prose
rules are not modified.

Content to add:

```markdown
## Tier Classification

On every request, before doing any work:
1. Classify the request and propose a tier: `"Tier: <name> — <one sentence on what I'll do/skip>. Proceed?"`
2. Wait for confirmation. User may confirm or name a different tier to override.
3. Stay within the confirmed tier's constraints for the full task.

The tier constraints in the `tier-config` block define the upper bounds on turns,
tool calls, and token cost per task. Claude must stay within those limits once a
tier is confirmed.

​```yaml
# tier-config
tiers:
  quick:    { max_turns: 1, max_tools: 0, max_cost: 100 }
  focused:  { max_turns: 3, max_tools: 3, max_cost: 500 }
  full:     { max_turns: 10, max_tools: 10, max_cost: 2000 }
​```
```

---

## 7. Files to Create / Modify

| File | Action |
|---|---|
| `~/.claude/CLAUDE.md` | Append new `## Tier Classification` section |
| `~/.claude/skills/session-tier/SKILL.md` | Create new skill file |

---

## 8. What Is Not Changed

- Existing CLAUDE.md prose rules (file re-read guard, Grep-first, agent dispatch, no trailing summaries)
- Any existing specs, plans, or skill files
- The superpowers plugin itself
- `.superpowers-config.yml` workspace config

---

## 9. Success Criteria

- [ ] Every request receives a tier proposal before any work begins
- [ ] User can confirm with one word or override by naming a tier
- [ ] Claude stays within tier constraints (turns, tools, cost) for the full task
- [ ] `/session-tier set focused` suppresses further tier proposals for the session
- [ ] `/session-tier show` returns current tier + config block
- [ ] `/session-tier reset` re-enables auto-classification
- [ ] Invalid tier input returns error, no state change
- [ ] Existing CLAUDE.md behavior is unaffected
