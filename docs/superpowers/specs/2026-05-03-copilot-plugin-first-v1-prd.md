# PRD: GitHub Copilot Plugin-First Workflow v1

**Date:** 2026-05-03
**Status:** Drafted from grilling session

## Problem Statement

Office developers need a reusable AI workflow that works naturally from GitHub Copilot Chat in IntelliJ / JetBrains, remains deterministic under change, and stays safe on large or fragile repositories.

The current workflow implementation is not yet credible as a first public v1:
- it mixes multiple incompatible workflow graphs
- it overclaims plugin behavior that is not aligned with official GitHub Copilot documentation
- it relies on internal layers that are not cleanly exposed through documented Copilot surfaces
- its config, manifest, validators, and public instructions do not agree on the same contract
- it claims legacy-monolith readiness without a dedicated bounded exploration gate

The result is a workflow that is structured, but not yet consistently portable, plugin-first, or deterministic enough for serious office repositories.

## Solution

Ship a narrower and truer v1: a portable GitHub Copilot workflow that is plugin-first for planning and orchestration, CLI-backed for evidence capture, and safe on complex repositories when explicit exploration gates are followed.

The v1 product contract is:
- align with official GitHub Copilot docs first
- use only documented JetBrains plugin primitives for the main user surface
- keep the plugin command surface small and easy to learn
- replace legacy workflow branches with one authoritative flow
- separate user-facing plugin behavior from machine-readable harness internals
- require bounded exploration before planning on unclear or risky codebases
- require human approval for degraded states, not just CLI switching
- require exact compatibility checks for artifact reuse across workflow versions

This v1 is not full autonomous end-to-end execution from IntelliJ alone. It is a deterministic workflow harness with a clear plugin/CLI boundary.

## User Stories

1. As an office developer, I want to drop a reusable workflow folder into a repository and have the main Copilot behavior work immediately from IntelliJ Copilot Chat, so that adoption is low-friction.
2. As an office developer, I want the primary workflow to rely only on officially documented GitHub Copilot customization surfaces, so that the behavior is aligned with the product I actually use.
3. As an office developer, I want repository-wide instructions to stay short, durable, and plugin-appropriate, so that Copilot gets stable guidance without excess context.
4. As an office developer, I want path-specific instructions to carry file-area rules automatically, so that workflow edits are governed without repeating those rules in every prompt.
5. As an office developer, I want prompt files to act as the visible task entrypoints in the plugin, so that the workflow is understandable from the IDE itself.
6. As an office developer, I want the workflow to expose a small set of core plugin commands, so that the system is learnable in real day-to-day use.
7. As an office developer, I want `/setup-workflow` to detect project metadata and common commands, so that repo-local setup is fast and mostly automatic.
8. As an office developer, I want the runtime config file to stay small and human-checkable, so that setup output is understandable and maintainable.
9. As an office developer, I want `/grill` to be the single pre-planning decision phase, so that there is one authoritative route into planning.
10. As an office developer, I want `/brainstorm` and `/write-spec` removed from v1, so that the workflow graph is deterministic instead of forked.
11. As an office developer, I want `/grill` to ask one question at a time and capture recommended answers, so that design decisions become explicit before implementation starts.
12. As an office developer, I want `/grill` to end with an explicit proceed-or-stop decision, so that planning only happens when readiness is clear.
13. As an office developer, I want `/write-plan` to turn resolved decisions into a bounded implementation plan, so that execution scope is locked before edits begin.
14. As an office developer, I want each plan step to declare its files, verification intent, preferred surface, and risk class, so that execution expectations are structurally visible.
15. As an office developer, I want high-risk or degraded plan steps to require explicit human acknowledgment, so that risky work is not normalized silently.
16. As an office developer, I want `/quick-task` to stay strictly narrow, so that it does not become a loophole around the main workflow.
17. As an office developer, I want `/quick-task` to escalate aggressively when scope, ambiguity, or risk grows, so that small tasks do not turn into unbounded work.
18. As an office developer, I want `/execute-plan` to stay inside declared plan scope, so that adjacent files are not modified opportunistically.
19. As an office developer, I want the workflow to request a CLI handoff explicitly when command execution is needed, so that switching surfaces is visible and intentional.
20. As an office developer, I want CLI handoff blocks to list the reason, allowed commands, allowed files, blocked actions, and return artifact, so that the shell phase remains bounded.
21. As an office developer, I want verification to be evidence-backed and command-driven, so that success claims depend on real output rather than narrative confidence.
22. As an office developer, I want the plugin to orchestrate verification while the CLI captures evidence, so that the plugin-first story remains true without overstating plugin capability.
23. As an office developer, I want review to compare actual changes against declared scope, so that scope creep is caught before merge.
24. As an office developer, I want every task to persist durable artifacts, so that progress survives chat resets and can be resumed safely.
25. As an office developer, I want artifact compatibility to be checked using exact workflow, command, and schema versions, so that stale artifacts are rejected reliably after workflow changes.
26. As an office developer, I want machine-readable workflow metadata to stay separate from user-facing plugin instructions, so that the plugin surface is easier to understand and cheaper in context.
27. As an office developer, I want internal implementation guides to avoid pretending to be official Copilot skills unless they are stored in supported skill locations, so that the repo structure matches official docs.
28. As an office developer, I want serious repos to provide at least minimal human-authored context, so that the workflow does not infer domain meaning entirely from code layout.
29. As an office developer, I want large or unclear codebases to require explicit bounded exploration before planning, so that monolith work starts from evidence instead of guesswork.
30. As an office developer, I want exploration to trigger automatically when target files are unknown, ownership is unclear, tests are weak, or multiple modules may be involved, so that the workflow stays cautious when uncertainty is high.
31. As an office developer, I want the workflow to remain usable on legacy monoliths without exploding context, so that the system is not limited to greenfield repos.
32. As an office developer, I want degraded states such as partial verification or unresolved ambiguity to require explicit human acknowledgment, so that risk acceptance is deliberate.
33. As an office developer, I want the workflow promise to be narrower and true, so that the system is trustworthy in practice.

## Implementation Decisions

- The primary plugin contract is defined only through officially supported GitHub Copilot repository instructions, path-specific instructions, and prompt files.
- Machine-readable workflow metadata remains internal harness infrastructure and is not a behavioral authority for plugin interactions.
- The workflow graph for v1 is single-path and authoritative: setup, grill, write plan, execute, verify, review, with quick-task as a narrow side path and bounded exploration as an explicit prerequisite when triggered.
- Legacy phases from the older graph are removed from the v1 surface rather than carried as first-class aliases.
- The runtime config is intentionally small and repo-local. It stores project identity, common commands, and minimal workflow toggles only.
- Bounded exploration is a first-class capability for legacy or ambiguous repositories. Planning does not implicitly expand into broad codebase archaeology.
- Serious repositories are expected to provide a minimal human-authored context artifact in addition to detected config.
- Verification is treated as a separate contract from planning: plans declare verification intent, while verification artifacts capture CLI evidence.
- Human approval is required for degraded execution and degraded verification states, not just for shell handoff.
- Plan steps carry explicit risk classification so approvals and review gates can be tied to structure rather than prose.
- Artifact compatibility is enforced using exact or narrowly compatible workflow, command, and schema version tuples.
- Internal implementation guides that are not official Copilot skills should be renamed or relocated so repo structure matches product terminology.
- The user-facing plugin command surface is intentionally small. Retrieval and verification machinery may exist as internal or advanced phases without becoming the default mental model.

Major modules to build or reshape:
- Plugin instruction contract
- Prompt entrypoint set
- Repo-local setup and config detection
- Bounded exploration capability
- Grill decision artifact
- Plan artifact and risk model
- Execution and CLI handoff contract
- Verification evidence contract
- Review and scope-gate contract
- Compatibility and artifact validation layer

## Testing Decisions

- Good tests validate external behavior and contract enforcement, not implementation details of validators or prompt wording internals.
- The highest-value tests are artifact acceptance and rejection tests, compatibility tests, and scope/risk gate tests.
- The workflow should be tested as a harness: given a valid or invalid artifact, does the system accept, reject, block, or degrade correctly.
- Bounded exploration triggers should be tested as policy behavior, especially unknown target files, multi-module involvement, weak-test contexts, and ownership ambiguity.
- Quick-task tests should emphasize aggressive escalation behavior and confirm that public behavior changes are rejected from the fast path.
- Verification tests should prove that success cannot be claimed without real evidence and that degraded evidence paths are surfaced honestly.
- Review tests should prove that changed-file scope mismatches fail deterministically.
- Compatibility tests should verify that stale artifacts from earlier command or schema versions are rejected even when the top-level workflow version appears unchanged.

Areas that require explicit test coverage:
- Setup output contract
- Single authoritative workflow graph
- Removal of retired command references
- Exploration gating
- Risk-class approval gating
- CLI handoff contract
- Verification evidence requirements
- Review scope enforcement
- Exact compatibility enforcement

## Out of Scope

- Full autonomous end-to-end implementation from IntelliJ alone
- Custom IntelliJ plugin development
- Cloud-agent-first workflow design
- Multi-agent orchestration as a core v1 concept
- Broad memory or vector-retrieval systems
- Hosted governance dashboards
- Organization-wide policy management
- Language-specific specialization beyond basic setup detection
- Implicit repo-wide exploration during normal planning
- A permissive quick-task path for risky or behavior-changing work

## Further Notes

- The main success criterion for v1 is credibility, not breadth.
- A narrower contract that is true is preferred over a broader contract that relies on undocumented behavior.
- Legacy-monolith readiness depends on the exploration gate and approval model, not on claiming that all phases can safely infer context from code alone.
- Official GitHub Copilot documentation is the alignment source for naming, repo structure, and supported surfaces.
