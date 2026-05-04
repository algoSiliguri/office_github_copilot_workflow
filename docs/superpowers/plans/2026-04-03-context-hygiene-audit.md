# Context Hygiene Audit & Lean Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a layered CLAUDE.md hierarchy and control plane config to eliminate cold-start token waste across the ~/Documents/Claude workspace.

**Architecture:** Five configuration files form an "onion" — global instincts at `~/.claude/CLAUDE.md`, workspace context at `~/Documents/Claude/CLAUDE.md`, a YAML control plane at `~/Documents/Claude/.superpowers-config.yml`, project context at `~/Documents/Claude/Office/CLAUDE.md`, and a gitignored personal override template at `~/Documents/Claude/Office/CLAUDE.local.md`. Claude reads them in order at session start; each layer narrows behavior without repeating earlier content.

**Tech Stack:** Plain Markdown, YAML — no build system, no dependencies.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `~/.claude/CLAUDE.md` | Global thrifty persona — instills token-saving instincts for every project on this machine |
| Create | `~/Documents/Claude/CLAUDE.md` | Workspace context — names active projects and shared conventions |
| Create | `~/Documents/Claude/.superpowers-config.yml` | Control plane — default plugin/agent rules for all Claude/* projects |
| Create | `~/Documents/Claude/Office/CLAUDE.md` | Project context — Office structure, current state, no-build-system note |
| Create | `~/Documents/Claude/Office/CLAUDE.local.md` | Personal template — gitignored session overrides |
| Modify | `~/Documents/Claude/Office/.gitignore` | Add `CLAUDE.local.md` entry (create file if missing) |

---

### Task 1: Global Thrifty Persona

**Files:**
- Create: `~/.claude/CLAUDE.md`

- [ ] **Step 1: Verify `~/.claude/` directory exists**

Run: `ls ~/.claude/`
Expected: directory listing (settings.json, plugins/, etc.)

If the directory is missing, stop — something is wrong with the Claude Code installation.

- [ ] **Step 2: Write `~/.claude/CLAUDE.md`**

Create the file with this exact content:

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

- [ ] **Step 3: Verify the file was written**

Run: `cat ~/.claude/CLAUDE.md`
Expected: full content above, no truncation, correct section headers visible.

---

### Task 2: Workspace Context File

**Files:**
- Create: `~/Documents/Claude/CLAUDE.md`

- [ ] **Step 1: Verify the workspace directory exists**

Run: `ls ~/Documents/Claude/`
Expected: `Office/` and `MOE/` directories visible (plus any other projects).

- [ ] **Step 2: Write `~/Documents/Claude/CLAUDE.md`**

Create the file with this exact content:

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

- [ ] **Step 3: Verify the file was written**

Run: `cat ~/Documents/Claude/CLAUDE.md`
Expected: full content above with all three sections present.

---

### Task 3: Workspace Control Plane

**Files:**
- Create: `~/Documents/Claude/.superpowers-config.yml`

- [ ] **Step 1: Write `~/Documents/Claude/.superpowers-config.yml`**

Create the file with this exact content:

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

- [ ] **Step 2: Verify the file was written**

Run: `cat ~/Documents/Claude/.superpowers-config.yml`
Expected: full content above, all four top-level keys (`skills`, `agent`, `mcp`) present with comments intact.

- [ ] **Step 3: Verify the file is hidden (dotfile)**

Run: `ls -la ~/Documents/Claude/ | grep superpowers`
Expected: `.superpowers-config.yml` listed (note the leading dot).

---

### Task 4: Office Project Context

**Files:**
- Create: `~/Documents/Claude/Office/CLAUDE.md`

- [ ] **Step 1: Write `~/Documents/Claude/Office/CLAUDE.md`**

Create the file with this exact content:

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

- [ ] **Step 2: Verify the file was written**

Run: `cat ~/Documents/Claude/Office/CLAUDE.md`
Expected: full content above with all three sections (Structure, Current State, No Build System) present.

---

### Task 5: Personal Override Template

**Files:**
- Create: `~/Documents/Claude/Office/CLAUDE.local.md`

- [ ] **Step 1: Write `~/Documents/Claude/Office/CLAUDE.local.md`**

Create the file with this exact content:

```markdown
# Local Overrides — not committed to git

## Active Focus (update each session)
<!-- What you're working on right now — prevents cold-start re-discovery questions -->

## Personal Skill Overrides
<!-- Override workspace .superpowers-config.yml rules for this session/project -->

## Scratch Notes
<!-- Anything you want Claude to know that doesn't belong in the permanent project file -->
```

- [ ] **Step 2: Verify the file was written**

Run: `cat ~/Documents/Claude/Office/CLAUDE.local.md`
Expected: full content above with all three sections as HTML comments (they should appear verbatim, not rendered).

---

### Task 6: Update .gitignore

**Files:**
- Modify (or create): `~/Documents/Claude/Office/.gitignore`

- [ ] **Step 1: Check if `.gitignore` already exists**

Run: `cat ~/Documents/Claude/Office/.gitignore 2>/dev/null || echo "FILE_MISSING"`

Two outcomes:
- File exists: note its current content — you will append to it.
- `FILE_MISSING`: you will create it from scratch.

- [ ] **Step 2: Check if `CLAUDE.local.md` is already listed**

Run: `grep -c 'CLAUDE.local.md' ~/Documents/Claude/Office/.gitignore 2>/dev/null || echo "0"`

- If output is `0` or the file was missing: proceed to Step 3.
- If output is `1` or more: the entry already exists — skip Step 3, mark this task done.

- [ ] **Step 3: Add `CLAUDE.local.md` to `.gitignore`**

If the file was **missing**, create it with:

```
CLAUDE.local.md
```

If the file **exists**, append one line:

```
CLAUDE.local.md
```

(Use the Write tool for a new file; use the Edit tool's append behavior or the Bash `echo >> ` for an existing file.)

- [ ] **Step 4: Verify the entry is present**

Run: `cat ~/Documents/Claude/Office/.gitignore`
Expected: `CLAUDE.local.md` appears on its own line. No other content should have been removed.

---

## Self-Review Against Spec

### Spec Coverage Check

| Spec requirement | Covered by |
|---|---|
| `~/.claude/CLAUDE.md` with thrifty persona content | Task 1 |
| `~/Documents/Claude/CLAUDE.md` with workspace context | Task 2 |
| `~/Documents/Claude/.superpowers-config.yml` with control plane | Task 3 |
| `~/Documents/Claude/Office/CLAUDE.md` with project context | Task 4 |
| `~/Documents/Claude/Office/CLAUDE.local.md` template | Task 5 |
| `.gitignore` updated with `CLAUDE.local.md` | Task 6 |
| No changes to superpowers plugin, `.github/` files, specs, plans, `settings.json` | Not applicable — plan creates only the 6 listed files |

All spec requirements covered. No gaps.

### Placeholder Scan

No TBD, TODO, or "implement later" placeholders. Every step contains exact file content or exact commands with expected output.

### Content Consistency

The content in each task is copied verbatim from the spec. Section headers, YAML keys, and Markdown structure match across all tasks.
