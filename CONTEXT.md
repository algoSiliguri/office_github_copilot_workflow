# Context

## Glossary

### Repo-Local Copilot CLI Orchestration Bundle

A portable set of repository files, primarily under `.github/`, that configures GitHub Copilot CLI behavior through repository-native instructions, skills, hooks, validators, and task artifacts. It does not require IDE plugin installation or external plugin loading for v1.

### Future Plugin Mode

An optional later distribution path where the repo-local orchestration bundle may be packaged as a GitHub Copilot CLI plugin after enterprise installation and policy constraints are proven safe.

### User-Facing Workflow Command

A small, human-invoked Copilot CLI command that represents a major workflow intent. In v1, the user-facing workflow commands are `/setup`, `/plan`, `/execute`, and `/verify`.

### Maintainer Evaluation Command

A maintainer-only command, `/evaluate`, used to inspect completed workflow artifacts and logs for system improvement candidates. It is not part of the ordinary task execution path.

### Quick Task Classification

A low-risk task classification made during `/plan`. It may produce a thinner PlanRecord, but it still requires intended files, risk, verification command, and human approval before edits. It is not a user-facing bypass command.

### Project Skill

A compact Copilot CLI project skill stored under `.github/skills/<skill>/SKILL.md`. V1 uses exactly five project skills: `graph-context`, `task-planning`, `bounded-execution`, `verification-review`, and `workflow-evaluation`.

### Diagnosis Required

A planning state for unclear bugs or regressions. `task-planning` must not produce an execution-ready plan until root cause, evidence, affected files, and verification strategy are explicit.

### GraphRecord

A repository-local orchestration metadata artifact at `.github/workflow/graph-record.json` that records the Graphify provider contract, required graph output locations, observed output presence, freshness state, and degraded approval state for the current target repository or branch.

### Graphify Copilot Install Intent

A setup-time instruction to run `graphify copilot install`. It records that the repository expects Copilot-facing Graphify setup, but it is not proof that Copilot will load or use a Graphify skill in a future session.

### Graphify Copilot Health Check

A non-mutating setup doctor check that verifies the local `graphify` command is discoverable, required `graphify-out/` files exist, and the Copilot Graphify skill is present at a discoverable user-home path. It reports fix commands instead of installing or modifying user files.

### Graph References

Task-scoped references to relevant graph nodes, communities, paths, or reports selected during `/plan` and stored in `PlanRecord.graph_refs[]`. Execution may follow approved graph references, but verification must rely on real checks, tests, diff scope, and human review.

### Degraded Graph Mode

A human-approved planning mode used when graphify output is missing, stale, or freshness cannot be proven. The plan must record the graph freshness problem and the user's approval to continue.

### Graph Usage

A required PlanRecord declaration that states whether Graphify was `used`, `skipped-with-approval`, or `unavailable`, whether the graph report was read, which graph queries ran, which graph references were selected, and why. It keeps Graphify from becoming an implicit assumption during planning.

### Graph Scope

A required PlanRecord explanation of how graph context affected planning scope. It records relevant modules, directly intended files, nearby files intentionally excluded, graph-discovered risk notes, and a concrete graph-to-plan decision.

### Graph Verification Boundary

The rule that Graphify is planning and review context, not verification proof. Verification proof must come from real commands, checks, tests, diff scope, command exit codes, and human review.

### Graph Scope Review

A ReviewRecord classification that compares actual changed files to the approved graph scope. It separates graph-near drift from graph-unrelated drift so review can catch when an agent wandered outside the planned area.

### Structural Scope Error

A scope gap discovered during `/execute` where Graphify context reveals that the plan's `intended_files` was fundamentally incomplete — files the plan should have included were never listed. A structural scope error requires halting execution, amending the plan via `/plan`, and re-obtaining human approval. It is distinct from opportunistic scope drift, where a small adjacent file is added inline with scope-drift approval.

### Graph-Light Planning

A quick-task-only planning mode where Graphify is unavailable or intentionally skipped. It must be explicitly allowed in the quick-task classification and still requires human approval before execution.

### Diagnostic Event Log

A local-only JSONL diagnostic trail at `.github/tasks/TASK-{NNN}/logs/events.jsonl`. It records compact redacted event summaries, references, human decisions, assumptions, deviations, and verification outcomes. It is not a chat transcript or full Copilot session copy.

### ApprovalRecord

A first-class human-in-the-loop decision artifact embedded in task and graph records. It records the approval kind, requester, human decision maker, timestamp, decision, reason, and expiry. ApprovalRecord replaces bare approval booleans for plan approval, degraded graph use, scope drift, memory writes, and governance edits.

### Local Memory Notebook

A gitignored repository-local notebook at `.github/local-memory/` for human-approved knowledge worth carrying forward. It stores proposed, accepted, and rejected MemoryCandidate records. It is not a diagnostic log, chat transcript, global AI memory, context retrieval system, dashboard, or dreaming loop.

### MemoryCandidate

A proposed durable memory item with a claim, source task, type, evidence references, reason it matters, expiry, status, and optional memory-write ApprovalRecord. A MemoryCandidate must stay proposed until human approval moves it to accepted, and rejected candidates remain audit evidence rather than reusable context.

### Evaluation Run

A maintainer-only analysis run that reads completed task artifacts, redacted event logs, and local memory notebook records, then writes dashboard-ready metrics and findings. It is not a dashboard UI, not dreaming, and not raw prompt export.

### Native Copilot Session History

The full local Copilot CLI session history stored by Copilot outside the repository. V1 may reference it by session ID, but does not copy full prompts, model responses, tool transcripts, or raw chat history into repository artifacts by default.

### Redacted Event Summary

A compact structured log event that omits sensitive prompt, response, file, and shell-output content by default, replacing it with summaries and references.

### V1 Hook Layer

Repository-level Copilot CLI hooks for `sessionStart`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `agentStop`, and `sessionEnd`. `agentStop` fires when the agent finishes a response turn. `sessionEnd` fires when the CLI session terminates. Hooks guard and log workflow behavior; they do not secretly plan, execute, verify, evaluate, or regenerate graph data.

### Approve Plan Gate

The mandatory human approval before `/execute`. The human approves the PlanRecord's intended files, risk class, graph freshness mode, verification command, and quick-task classification when present.

### Approve Risky Tool Use Gate

The mandatory human approval for risky setup or execution actions, including destructive commands, network commands, dependency installation, graph regeneration, hook or script execution that changes files, workflow governance edits, or writes outside approved plan scope.

### Approve Verification Review Gate

The mandatory human approval during `/verify` for the task result, scope drift disposition, degraded verification acknowledgment, and any remaining assumptions or deviations.

### Approve Workflow Improvement Gate

The maintainer-only human approval required before changing instructions, skills, hooks, schemas, validators, policies, or command definitions based on workflow evaluation.

### V1 Task Artifact Set

The required v1 artifacts are GraphRecord, PlanRecord, ExecutionRecord, VerificationRecord, ReviewRecord, and SessionEventLog. V1 does not require TaskManifest.

### PlanRecord

The task planning artifact at `.github/tasks/TASK-{NNN}/plan.json`. It includes planning decisions, diagnosis when required, exploration findings, context references, graph references, quick-task classification when present, intended files, risk, verification command, and plan approval.

### TaskManifest

An optional future generated index for task lookup. It is not authoritative or required in v1.

### Workflow Orchestrator Agent

The single required v1 repository custom agent at `.github/agents/workflow-orchestrator.agent.md`. It routes intent to `/setup`, `/plan`, `/execute`, `/verify`, or maintainer `/evaluate`, selects the right skill, enforces phase boundaries, and keeps context compact. It does not execute plan edits, bypass hooks, approve actions, load the whole graph, load all artifacts by default, or self-modify workflow files.

### Safe Default Mode

The v1 acceptance mode. It uses repo-local `.github` files, Copilot CLI, repository instructions, five project skills, one workflow orchestrator agent, graph metadata, typed artifacts, redacted logs, validators, and human gates. It does not require plugin installation, MCP, LSP, admin privileges, or hooks.

### Enhanced Local Mode

Safe Default Mode plus hooks, local validators or scripts, explicit graphify approval, and optional project LSP configuration. It still does not depend on plugin installation.

### Enterprise-Approved Mode

A post-v1 operating mode that may add organization-approved plugin, MCP, LSP, or policy-managed installation after admin and security approval.

### V1 Acceptance Criterion

Safe Default Mode must complete `/setup -> /plan -> /execute -> /verify` without plugin, MCP, LSP, hooks, or admin privileges.

### Safe Default Validator

A required v1 validator that runs with zero third-party runtime dependencies. Safe Default validators may use Python standard library modules such as `json`, but must not require packages such as PyYAML.

### Required V1 Configuration

The required v1 configuration and task artifacts use JSON or JSONL. YAML may exist only as optional enhanced-local configuration, not as part of the Safe Default acceptance path.

### Bundle AGENTS.md

The root `AGENTS.md` in the orchestration bundle repository. It guides maintenance of the orchestration system itself and must not be copied verbatim into target repositories.

### Target Repository AGENTS.md Managed Block

A bounded block that `/setup` creates or updates in a target repository's root `AGENTS.md` without overwriting existing team instructions. It points to the repo-local Copilot instructions, skills, workflow orchestrator agent, config, and graph record, and lists only the v1 commands and human gates.

### Workflow State File

A lightweight mutable state file at `.github/workflow/state.json` that records the currently active task. `/plan` writes `active_task` to it when a task begins. `/verify` clears `active_task` to `null` on task closeout. Hook scripts read from it to determine which task log to append events to. It is distinct from policy files (`orchestration.json`, `config.json`), which are static. The active task lifecycle contract is declared in `orchestration.json` under `plan_contract.writes_active_task_to_state` and `verify_contract.clears_active_task_on_closeout`.

### Open Task

A task whose lifecycle has started but has not reached terminal verification and review disposition. V1 permits at most one open task at a time so hook logs, state, and task artifacts have a single coordination target.

### Fresh V1 Layout

The clean v1 repository structure that replaces the old command, agent, schema, manifest, policy, and validator sprawl. Because no users depend on the old structure, v1 optimizes for a fresh minimal layout rather than backward compatibility.

### Authority Rule

`AGENTS.md` and `.github/copilot-instructions.md` define always-on behavior. Skills define specialized behavior. Hooks guard and log. Artifacts carry phase state. Validators prove structure. Docs explain but do not govern.

**Authoritative in phase 1:** validators, approved artifacts, human approval records, verification command output and exit code, graph-record status for the planning gate.

**Not authoritative in phase 1:** raw hook event logs, Graphify report as verification proof, local memory notebook contents, evaluation findings, skills text without validator support.
