# Copilot Workflow Bundle — Quick Start

## Prerequisites

- GitHub Copilot CLI installed and authenticated
- Python 3.9+

## Setup (one-time per repo)

1. **Copy `.github/` into the root of your target repo.**

2. **Install Graphify** (one-time per machine):
   ```
   pip install graphify
   ```

3. **Build the knowledge graph** (from your repo root):
   ```
   graphify .
   ```

4. **Register the Copilot skill** (one-time per machine):
   ```
   graphify copilot install
   ```

5. **Open Copilot CLI** from your repo root:
   ```
   copilot
   ```

6. **Run `/setup`** — validates the bundle, checks graph state, reports anything missing.

7. **Describe your task** — type `/grill I want to <what you want to do>`. Copilot allocates
   a task ID, creates the task folder, maps the blast radius, and asks you to approve before
   planning begins. You do not need to create folders manually.

## Workflow

```
/setup → /grill <describe task> → /plan → /execute → /verify
```

| Command   | What it does |
|-----------|--------------|
| `/setup`  | Validate bundle, record graph state, update AGENTS.md |
| `/grill`  | Allocate task ID, map blast radius, surface risks, lock verification steps |
| `/plan`   | Declare intended files, risk, and verification commands. Requires approved grill |
| `/execute`| Apply only the approved plan edits |
| `/verify` | Run locked verification commands and produce a witnessed receipt |

Human approval is required at `/grill`, before `/execute`, and before final verification.

## If Graphify is unavailable

Skip steps 2–4. Run `/setup` anyway — it records degraded mode. You can still work;
each phase will prompt for explicit human approval to proceed without fresh graph context.

## If something looks wrong

Run from your repo root:
```
bash .github/workflow/doctor
```

It reports which validators pass and what is missing.

## Known unknowns (check these on first office laptop test)

These three things depend on the exact Copilot CLI version installed and have not been
verified in a live office environment. Note what you observe so the bundle can be fixed.

**1. Does Copilot CLI auto-load `.github/copilot-instructions.md`?**
Expected: yes, GitHub docs say Copilot CLI reads this file automatically from repo root.
Check: after opening Copilot in a repo with this bundle, type `/setup` and see if it
follows the workflow rules (creates graph-record.json, writes AGENTS.md block). If Copilot
ignores the instructions file, the version may be too old — update Copilot CLI first.

**2. Does `graphify copilot install` make Copilot load graph context?**
Expected: yes, the install command registers a Copilot skill that surfaces graphify output.
Check: after running `/grill`, does Copilot reference files from graphify-out/GRAPH_REPORT.md
when identifying blast radius? If not, `graphify copilot install` may not have worked —
run it again and check `~/.copilot/skills/` for a graphify entry.

**3. Do `.github/hooks/workflow-hooks.json` hooks actually fire?**
Expected: yes, Copilot CLI loads hooks from `.github/hooks/` per the hooks spec.
Check: after `/execute`, look for a log file at `.github/tasks/TASK-001/logs/events.jsonl`.
If the file is absent, hooks are not firing — the Copilot CLI version may predate hook
support, or the hook config format may need adjustment for the installed version.
