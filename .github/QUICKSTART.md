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

## Workflow

```
/setup → /grill → /plan → /execute → /verify
```

| Command   | What it does |
|-----------|--------------|
| `/setup`  | Validate bundle, record graph state, update AGENTS.md |
| `/grill`  | Discovery Gate — map blast radius, surface risks, lock verification steps |
| `/plan`   | Declare intended files, risk, and verification commands. Requires approved grill |
| `/execute`| Apply only the approved plan edits |
| `/verify` | Run locked verification commands and produce a witnessed receipt |

Human approval is required before `/execute` and before final verification acceptance.

## If Graphify is unavailable

Skip steps 2–4. Run `/setup` anyway — it records degraded mode. You can still work;
each phase will prompt for explicit human approval to proceed without fresh graph context.

## If something looks wrong

Run from your repo root:
```
bash .github/workflow/doctor
```

It reports which validators pass and what is missing.
