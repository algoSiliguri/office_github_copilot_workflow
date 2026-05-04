# PRD: GitHub Copilot Enterprise Plugin-First Workflow v1

**Date:** 2026-05-03
**Status:** Ready for implementation

---

## Problem Statement

Office developers using GitHub Copilot Enterprise through the IntelliJ / JetBrains plugin have no structured, deterministic workflow to follow. The current `.github/` system was built for terminal agents (Claude Code, Codex) and is unusable from IntelliJ Copilot Chat — the primary surface most office developers actually use.

Specifically:
- `copilot-instructions.md` tells Copilot to "load manifest.yaml" — meaningless to the plugin
- No agents exist for multi-turn phases like grill or plan
- No path-specific instructions exist
- No tech-stack detection or auto-configuration
- Brainstorm and write-spec phases are loose, unstructured, and don't enforce decisions before planning
- Artifact schemas use inconsistent naming and lack surface metadata
- Validators reference legacy artifact type names

The result: developers either bypass the workflow entirely or fight the tooling to make it work from IntelliJ.

---

## Solution

Rebuild the portable `.github/` drop-in as a GitHub Copilot Enterprise-first, IntelliJ plugin-centered workflow system. Copy the folder into any office repo, run `/setup-workflow` once to auto-detect the tech stack, and the full grill → plan → execute → verify → review workflow becomes available as slash commands from IntelliJ Copilot Chat — with CLI retained as a secondary surface for command-heavy execution.

Key improvements:
- `copilot-instructions.md` rewritten as a compact, plugin-first behavioral contract
- Custom agents (`grill`, `write-plan`, `execute-plan`) provide bounded, approval-gated multi-turn phases
- Prompt files thin-wrap agents for agent-backed phases; remain full for single-shot phases
- `/setup-workflow` auto-detects tech stack and writes `workflow/config.yaml` — no manual placeholders
- `GrillRecord` replaces brainstorm and absorbs spec-level thinking via an `approach[]` block
- Canonical artifact schema names aligned with the brief
- Path-specific instructions enforce workflow editing rules across any repo
- CLI handoff is explicit, human-approved, and plan-declared

---

## User Stories

1. As an office developer, I want to copy `.github/` into any repo and have Copilot Enterprise understand the workflow immediately, so that I do not need to configure anything manually.
2. As an office developer, I want to run `/setup-workflow` in IntelliJ Copilot Chat and have it auto-detect my tech stack and build/test/verify commands, so that I do not maintain manual configuration files.
3. As an office developer, I want `copilot-instructions.md` to explain the workflow, available commands, permission tiers, and output contract in under 80 lines, so that Copilot stays on-task in every interaction.
4. As an office developer, I want to type `/grill` in IntelliJ Copilot Chat and enter a structured Q&A session that forces decisions before planning, so that bad ideas are caught before any code is written.
5. As an office developer, I want the grill session to capture architecture decisions and rejected alternatives, so that I do not re-litigate design choices during planning.
6. As an office developer, I want the grill record to declare whether the task should proceed, so that there is an explicit human approval gate before a plan is created.
7. As an office developer, I want to type `/write-plan` and have Copilot produce a bounded `PlanArtifact` grounded in the grill record, so that implementation scope is locked before any code is touched.
8. As an office developer, I want the plan to declare which files are in scope and which are out of scope, so that I can hold Copilot accountable to the plan during execution.
9. As an office developer, I want the plan to declare whether a context-packet is required before execution, so that large-repo execution has bounded retrieval rather than open-ended guessing.
10. As an office developer, I want the plan to declare the preferred surface per step (IntelliJ plugin vs. Copilot CLI), so that I know when to stay in the IDE and when to open a terminal.
11. As an office developer, I want to type `/execute-plan` and have Copilot stay bounded to the declared plan scope, so that unplanned files are not silently modified.
12. As an office developer, I want Copilot to request a CLI handoff explicitly and show me a human-readable handoff block before I switch to the terminal, so that I always approve the handoff rather than having it happen silently.
13. As an office developer, I want CLI handoff to include allowed commands, allowed files, blocked actions, and the expected return artifact, so that the terminal session is as bounded as the plugin session.
14. As an office developer, I want to type `/verify` and have Copilot produce a `VerificationRecord` with command output rather than a claim of success, so that verification is always evidence-backed.
15. As an office developer, I want to type `/review` and have Copilot compare the changed files against the plan scope, so that scope creep is caught before merge.
16. As an office developer, I want to type `/quick-task` for small low-risk changes without invoking the full workflow, so that simple tasks do not require a grill and plan.
17. As an office developer, I want `/quick-task` to automatically escalate to `/grill` when scope, risk, file count, or uncertainty grows, so that small tasks do not accidentally become unbounded.
18. As an office developer, I want all task artifacts saved to `.github/tasks/TASK-001/`, so that I can inspect, version-control, and reference them across sessions.
19. As an office developer, I want every artifact to carry `primary_surface` and `secondary_surfaces_allowed` metadata, so that the surface layer is explicit in every workflow record.
20. As an office developer, I want path-specific instructions to automatically apply when I edit workflow files in `.github/ai-workflow/`, so that I do not accidentally break schemas, contracts, or validators.
21. As an office developer, I want `copilot-instructions.md` to reference `workflow/config.yaml` for project-specific values rather than embedding them inline, so that the behavioral contract stays portable and config stays repo-local.
22. As an office developer, I want the grill agent to restrict its context to the task scope rather than the whole repo, so that I get focused, relevant responses rather than broad noise.
23. As an office developer, I want the write-plan agent to only see the grill record and the declared in-scope files, so that the plan is grounded in evidence rather than assumptions.
24. As an office developer, I want the execute-plan agent to be bounded to declared plan scope and refuse to touch out-of-scope files, so that plan adherence is enforced.
25. As an office developer, I want Copilot to never claim the task is done without a `VerificationRecord`, so that success is always grounded in fresh evidence.
26. As an office developer, I want the permission ladder (Tier 1–4) to be embedded in `copilot-instructions.md`, so that Copilot knows what requires approval before acting.
27. As an office developer, I want Copilot output to use status blocks rather than prose paragraphs, so that phase state, surface, scope, and next step are always visible at a glance.
28. As an office developer, I want the workflow to work on any tech stack without modification, so that I can drop it into Java, Python, Node, Rust, or any other repo.
29. As an office developer, I want the manifest to serve as machine-readable registry for validators and CLI tooling only, not as an LLM instruction layer, so that the plugin behavioral contract is self-contained in `copilot-instructions.md`.
30. As an office developer, I want Python validators to enforce schema correctness, scope locks, and review gates at the CLI layer, so that deterministic checks are not left to LLM judgment alone.

---

## Implementation Decisions

### Phase Map

```
setup-workflow → grill → [context-packet: optional, plan-declared] → write-plan → execute-plan → verify → review
                                                                              ↑
                                                                         quick-task (parallel escape hatch)
```

### Agents

Three custom agents at `.github/agents/`:
- `grill.md` — multi-turn structured Q&A, context-restricted to task scope, produces `GrillRecord`
- `write-plan.md` — sees grill record + declared in-scope files only, produces `PlanArtifact`
- `execute-plan.md` — bounded to plan-declared file scope, enforces CLI handoff protocol

Agent names match prompt names exactly. Agents are the authority; prompt files thin-wrap them.

### Prompt Files

Thin wrappers for agent-backed phases (grill, write-plan, execute-plan): ~5 lines, `#file:` reference to agent. Full rewrites for single-shot phases: verify, review, quick-task, context-packet, setup-workflow.

### copilot-instructions.md

Rewritten from scratch. Under 80 lines. Sections:
- What this repo is
- Available commands (slash commands list)
- Workflow phase order
- Permission ladder (Tier 1–4 summary)
- Output contract (status blocks, not prose)
- CLI handoff rules
- Reference to `workflow/config.yaml` for project-specific config
- Instruction hierarchy (instructions > agents > prompts)

### workflow/config.yaml

Written by `/setup-workflow`. Fields:
- `project.name`, `project.description`, `project.primary_language`, `project.framework`
- `commands.build`, `commands.test`, `commands.verify`, `commands.lint`
- `workflow.cli_handoff_allowed`, `workflow.task_path`, `workflow.instruction_version`

Auto-detected from `build.gradle`, `pom.xml`, `package.json`, `pyproject.toml`, `Makefile`, `Cargo.toml`. Validator confirms required fields populated before any workflow phase proceeds.

### GrillRecord Schema

New schema. Absorbs spec-level thinking. Fields: `artifact_type`, `schema_version`, `task_id`, `primary_surface`, `secondary_surface`, `goal`, `problem_statement`, `assumptions[]`, `questions[]`, `risks[]`, `constraints[]`, `approach[]` (NEW: `decision`, `rationale`, `alternatives_rejected`), `success_criteria[]`, `decision`, `open_blockers[]`, `validated_under`.

### Other Artifact Schemas

All updated to canonical names: `PlanArtifact`, `ExecutionRecord`, `VerificationRecord`, `ReviewRecord`, `QuickTaskRecord`. All gain `primary_surface` and `secondary_surfaces_allowed` fields. `brainstorm.schema.json` and `spec.schema.json` deleted.

### PlanArtifact additions

New fields: `context_packet_required: true/false`, `context_packet_path`. Validator blocks execute-plan if `context_packet_required: true` and no context packet artifact exists.

### CLI Handoff Protocol

Three triggers:
1. Plan step declares `preferred_surface: copilot_cli`
2. Verification requires running commands
3. Scope spans >5 files with non-trivial changes

Handoff always produces a human-readable block. Human must approve before switching to terminal. Block contains: reason, task path, allowed commands, allowed files, blocked actions, expected return artifact.

### Path-Specific Instructions

Single file: `.github/instructions/workflow.instructions.md`. Apply glob: `.github/**`. Rules: schema versioning on edit, contract scope enforcement, validator test requirements, governance file tier classification.

### Task Artifact Path

`.github/tasks/TASK-{NNN}/` with sequential numeric IDs. Each folder holds all phase artifacts for that task.

### Manifest Role

Demoted to CLI/validator infrastructure registry. Not loaded by LLM. `copilot-instructions.md` references it only as: "Machine-readable registry — do not modify directly."

### Validators

Python validators kept. Updated only for new artifact type names. Existing enforcement logic preserved.

---

## Testing Decisions

Good tests verify external behavior: given a complete artifact input, does the validator accept or reject it correctly? Tests do not inspect internal validator logic or Python implementation details.

Modules to validate via test artifacts:
- `GrillRecord` — valid + missing required field + missing `approach` block
- `PlanArtifact` — valid + scope violation + missing `context_packet_path` when required
- `VerificationRecord` — valid + missing command output
- `ReviewRecord` — valid + scope mismatch
- `QuickTaskRecord` — valid + escalation trigger

Prior art: existing `artifacts/examples/` YAML files. New examples follow same structure, updated for canonical schema names.

---

## Out of Scope

```
Copilot cloud agent
MCP integration
Custom IntelliJ plugin development
Hosted governance dashboard
Multi-agent chaining
Vector memory system
Production deployment automation
Autonomous remote side effects
Language/framework-specific path instructions
write-spec phase
brainstorm phase
Complex RBAC
Team/admin policy automation
```

---

## Further Notes

- Agents are currently "preview" in JetBrains per GitHub docs. If agent support degrades, prompt files serve as full fallbacks (revert thin-wrapper to full prompt content).
- `workflow/config.yaml` is the only repo-specific file that needs updating after drop-in. Everything else in `.github/` is portable.
- Grill replaces brainstorm entirely. No migration path needed — this is v1 greenfield.
- HumanLayer 12-Factor Agents philosophy is the governing design reference: human contact as first-class tool, developer owns context window, small focused agents per phase, stateful artifact-based resumption.
