# GitHub Copilot CLI Workflow Bundle

Fresh v1 repo-local orchestration bundle for GitHub Copilot CLI.

The v1 foundation is not plugin-first. It is a portable `.github` layer that can be copied into normal repositories and used on managed office laptops without plugin installation, MCP, LSP, admin privileges, YAML parsers, or third-party validator dependencies.

## Core Path

```text
/setup -> /plan -> /execute -> /verify
```

`/evaluate` is maintainer-only for workflow improvement. `/quick-task` is not a user-facing command; it is a classification inside `/plan`.

## What Is Authoritative

- `AGENTS.md` and `.github/copilot-instructions.md`: always-on behavior
- `.github/agents/workflow-orchestrator.agent.md`: routing, phase boundaries, context compaction
- `.github/skills/<skill>/SKILL.md`: compact task-specific behavior
- `.github/workflow/*.json`: required JSON config and graph metadata
- `.github/workflow/schemas/*.json`: artifact contracts
- `.github/workflow/validators/*`: standard-library-only validation
- `.github/tasks/`: live task artifacts
- `.github/examples/tasks/`: committed examples and fixtures

Docs explain the system but do not govern it.

## V1 Skills

1. `graph-context`
2. `task-planning`
3. `bounded-execution`
4. `verification-review`
5. `workflow-evaluation`

## Safe Default Validation

Run from the repository root:

```bash
python3 .github/workflow/validators/check-setup
python3 .github/workflow/validators/check-plan .github/examples/tasks/TASK-001/plan.json
python3 .github/workflow/validators/check-execution .github/examples/tasks/TASK-001/execution.json
python3 .github/workflow/validators/check-verification .github/examples/tasks/TASK-001/verification.json .github/examples/tasks/TASK-001/review.json
```

Or run:

```bash
bash release-check.sh
```

## Operating Modes

- **Safe Default Mode:** repo-local files, Copilot CLI instructions, five skills, one orchestrator agent, JSON artifacts, graph metadata, stdlib validators, and human gates.
- **Enhanced Local Mode:** Safe Default plus optional hooks and local scripts.
- **Enterprise-Approved Mode:** post-v1 organization-approved plugin, MCP, LSP, or policy-managed installs.
- **Future Plugin Mode:** post-v1 packaging of the same repo-local bundle after install/update/audit behavior is proven.
