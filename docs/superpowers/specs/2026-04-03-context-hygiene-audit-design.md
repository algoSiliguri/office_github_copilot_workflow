# Design Spec: Context Hygiene Audit & Lean Workflow

**Date:** 2026-04-03
**Context:** Audit of Claude Code session patterns across the ~/Documents/Claude workspace to eliminate token waste without losing workflow quality. Covers Office and MOE projects. Applies to Claude Code with superpowers, code-simplifier, and context7 plugins.

---

## 1. Problem Statement

Three recent sessions (56271b6c, 6decdc21, c5f5ea39) showed recurring token leaks:

| Leak | Evidence |
|---|---|
| Cold-start re-discovery | 21–31 Read calls per session just to re-establish known context |
| WebFetch/WebSearch duplication | Session 1: 13 fetches + 7 searches for the same GitHub Copilot docs topic |
| Agent over-dispatch | Sessions 2 & 3: 12–20 Agent calls; subagents re-read files the parent already read |
| File re-reads | Same spec file read 2x in one session; 30 individual files read one-by-one |
| TaskCreate/Update churn | 20+19 task ops in one session — overhead without proportional value |
| context7 MCP silent overhead | Plugin enabled but no observed usage across all three sessions |

No `CLAUDE.md` existed anywhere. Every session started cold.

---

## 2. Solution: Layered Onion + YAML Control Plane

Four files. Clear separation of concerns.

### File Hierarchy

```
~/.claude/CLAUDE.md                              ← Global: behavioral instincts (all projects on machine)
~/Documents/Claude/CLAUDE.md                     ← Workspace: applies to Office, MOE, all future Claude/* projects
~/Documents/Claude/.superpowers-config.yml       ← Control plane: default plugin/agent rules for all Claude/* projects
~/Documents/Claude/Office/CLAUDE.md              ← Project: Office-specific context only
~/Documents/Claude/Office/CLAUDE.local.md        ← Personal: session overrides, not committed to git
~/Documents/Claude/Office/.superpowers-config.yml  ← Optional: per-project control plane overrides
```

### Read Order at Session Start

1. Global `~/.claude/CLAUDE.md` → installs thrifty persona
2. `~/Documents/Claude/CLAUDE.md` → loads workspace context
3. `~/Documents/Claude/Office/CLAUDE.md` → loads project-specific context
4. `CLAUDE.local.md` if present → applies personal overrides
5. Bootstrap rule fires → walks up from project root to find nearest `.superpowers-config.yml` → applies all plugin/agent constraints

---

## 3. File Contents

### `~/.claude/CLAUDE.md` — The Thrifty Persona

```markdown
# Global Instincts

## Session Bootstrap
At the start of every session, check for a `.superpowers-config.yml` walking up from the
project root. If found, read it and apply all rules before any other action.

## File References
- Never read a file you have already read in this session — use the cached content.
- Use Grep or Glob before reaching for Agent or Read for any search task.
- Never read more than 3 files to answer a question you could answer with Grep.

## Web Research
- Do not WebFetch or WebSearch unless the user explicitly asks or the task requires
  current version info unavailable in training data.
- One search query per topic — do not retry with rephrased queries unless the first
  returned zero results.

## Agent Dispatch
- Prefer inline execution for tasks touching ≤3 files.
- Use sub-agents only for new features or tasks spanning 4+ files.
- Maximum 2 review cycles per task — if not resolved, stop and ask the user.

## Communication
- Responses are concise. No trailing summaries of what was just done.
- No TaskCreate for tasks under 3 steps.
```

---

### `~/Documents/Claude/CLAUDE.md` — The Workspace Architect

```markdown
# Claude Workspace Context

## What This Is
Workflow tooling workspace. Projects here build and maintain AI-assisted development
workflows for Claude Code and GitHub Copilot.

## Active Projects
- `Office/` — Claude Code workflow tooling, superpowers skill configs, Copilot IntelliJ integration
- `MOE/` — see MOE/CLAUDE.md for specifics

## Shared Conventions
- Specs → `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- No shared build system or test runner across projects
- Superpowers plugin: ~/.claude/plugins/cache/claude-plugins-official/superpowers/
```

---

### `~/Documents/Claude/Office/CLAUDE.md` — Office-Specific Context

```markdown
# Office Project Context

## Structure
- `docs/superpowers/specs/` — design specs
- `docs/workflow/` — workflow guides, plans, templates
- `github/` — GitHub Copilot skills, agents, prompts for IntelliJ

## Current State (as of 2026-04-03)
Phased execution workflow complete. Skills: brainstorming, planning, execution,
conventions. Copilot IntelliJ integration confirmed working in IDEA 2025.3.4.

## No Build System
No package.json, no Makefile. Nothing to install or compile.
```

---

### `~/Documents/Claude/.superpowers-config.yml` — The Control Plane

```yaml
# Superpowers Control Plane — ~/Documents/Claude workspace default
# Read at session start per ~/.claude/CLAUDE.md bootstrap rule.
# Override per-project by placing .superpowers-config.yml in the project root.

skills:
  tdd: inactive             # no test suites in these projects
  brainstorming:
    skip_for: [bugfix, typo, config-change]  # skip full brainstorm for minor tasks

agent:
  dispatch: inline-first    # inline unless task touches 4+ files
  max_review_cycles: 2      # stop and ask user after 2 failed review cycles

mcp:
  context7: on-demand       # fetch docs only when user explicitly asks
  code-simplifier: post-edit-only  # run only after edits, not at session start
```

---

### `~/Documents/Claude/Office/CLAUDE.local.md` — Template

```markdown
# Local Overrides — not committed to git

## Active Focus (update each session)
<!-- What you're working on right now — prevents cold-start re-discovery questions -->

## Personal Skill Overrides
<!-- Override workspace .superpowers-config.yml rules for this session/project -->

## Scratch Notes
<!-- Anything you want Claude to know that doesn't belong in the permanent project file -->
```

Add to project `.gitignore`:
```
CLAUDE.local.md
```

---

## 4. Estimated Token Reduction

| Leak eliminated | Estimated saving per session |
|---|---|
| Cold-start re-discovery (21–31 Reads → 0) | ~2,000–4,000 tokens |
| WebFetch/WebSearch deduplication | ~1,500–3,000 tokens |
| Agent over-dispatch (20 → 4–6 targeted) | ~3,000–6,000 tokens |
| context7 silent overhead removed | ~500–1,000 tokens |
| TaskCreate churn (20 → <5) | ~500 tokens |
| **Total estimated reduction** | **~40–50% per session** |

---

## 5. What Is Not Changed

- The superpowers plugin itself — no plugin code modifications
- The existing `.github/` Copilot workflow files
- Any existing spec or plan documents
- `settings.json` — no changes to enabled plugins (context7 stays enabled, just constrained to on-demand)

---

## 6. Implementation Scope

Files to create:
1. `~/.claude/CLAUDE.md`
2. `~/Documents/Claude/CLAUDE.md`
3. `~/Documents/Claude/.superpowers-config.yml`
4. `~/Documents/Claude/Office/CLAUDE.md`
5. `~/Documents/Claude/Office/CLAUDE.local.md` (template)

Files to update:
- `~/Documents/Claude/Office/.gitignore` (add `CLAUDE.local.md` entry, create if missing)
