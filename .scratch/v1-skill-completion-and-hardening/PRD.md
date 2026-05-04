# PRD: v1 Skill Completion and Hardening

**Date:** 2026-05-04
**Status:** needs-triage
**Source:** Grill session — adversarial v1 readiness review

---

## Problem Statement

The GitHub Copilot plugin-first workflow bundle has a sound orchestration core but cannot ship as a credible v1 for office and enterprise use. Five concrete defects block it:

1. All four custom agents declare `tools: [codebase]` — an unrecognized tool name that is silently ignored, leaving every agent with unrestricted tool access. The scope-lock model that the workflow depends on does not exist at runtime.

2. Five support skills required for daily developer work are absent: `/diagnose`, `/tdd`, `/safe-refactor`, `/zoom-out`, and `/grill-with-docs`. Without them, the most common daily workflows (fix a bug, write tests, understand unfamiliar code) have no structured entry point and fall through to freeform chat.

3. `/legacy-explore` — the only monolith safety gate — has 12 lines of agent instruction and a generic `findings[]` string array in its schema. It cannot guide Copilot to detect generated code, stored procedure surfaces, blast radius, test surface quality, or slow-build signals. A team on a 500k-line monolith gets no protection.

4. Four protocol files exist at `.github/ai-workflow/protocols/` but no agent or instruction references them. They are invisible to Copilot plugin sessions. The verification gate, stage review rules, phase checkpoint behavior, and retrieval decision logic exist only as documentation, not as enforced runtime behavior.

5. No versioning infrastructure exists. No `VERSION` file, no `CHANGELOG`, no upgrade command, no artifact migration state. A team upgrading the bundle after three months of task accumulation has no safe path.

---

## Solution

Harden the v1 bundle to make every documented workflow guarantee actually enforceable at runtime:

- Replace invalid tool declarations with correct least-privilege tool sets in all agent files.
- Add five support skills using the confirmed hybrid 1-layer model (`.agent.md` + thin `.prompt.md` wrapper) so daily workflows have structured entry points without framework overhead.
- Enrich the `/legacy-explore` agent with explicit monolith-specific protocol checks and extend `LegacyExplorationRecord` with five structured fields that make risk machine-readable for downstream planning.
- Wire each protocol file to its responsible agent via a hybrid reference pattern (inline rule summary + `#file:` reference). Delete any protocol not referenced by at least one agent or instruction file.
- Add a `VERSION` file, `CHANGELOG.md`, and an `/upgrade-workflow` prompt that scans task artifacts for schema mismatches and flags `migration_required` or forces phase regeneration.

The result is a bundle where every stated guarantee is enforced in the plugin session path, not only described in documentation.

---

## User Stories

1. As an office developer using Copilot Chat in IntelliJ, I want the `/grill` agent to be restricted to read and search tools only, so that it cannot accidentally modify source files during a problem exploration session.

2. As an office developer, I want the `/write-plan` agent to be restricted to read and search tools only, so that no file edits happen before a plan is approved.

3. As an office developer, I want the `/execute-plan` agent to have read, edit, search, and execute tools, so that it can implement the plan without needing to escalate for tool permissions mid-task.

4. As an office developer, I want the `/legacy-explore` agent to be restricted to read and search tools only, so that exploration never modifies the codebase.

5. As an office developer, I want to invoke `/diagnose` in Copilot Chat and receive a structured diagnosis loop — reproduce, hypothesise, instrument, fix, regression test — so that I do not fall through to freeform debugging chat.

6. As an office developer, I want `/diagnose` to hand off to `/grill` or `/write-plan` when the root cause implies a non-trivial fix, so that the fix stays inside the governed workflow.

7. As an office developer, I want to invoke `/tdd` and receive a red-green-refactor loop grounded in the repo's test runner, so that I can build features test-first without setting up the workflow manually.

8. As an office developer, I want `/tdd` to use read, edit, search, and execute tools so it can run tests and verify green before declaring a cycle complete.

9. As an office developer, I want to invoke `/safe-refactor` and receive a bounded refactor plan that identifies the blast radius, dependent callers, and test surface before any edits, so that refactors do not silently break unrelated modules.

10. As an office developer, I want `/safe-refactor` to hand off to `/write-plan` when the refactor scope exceeds a single file, so that large refactors stay governed.

11. As an office developer, I want to invoke `/zoom-out` on any file, module, package, or service and receive a compact orientation — responsibility, main files, call flow, risks, follow-up questions — so that I can understand unfamiliar code before starting a formal task.

12. As an office developer, I want `/zoom-out` to require no prior artifact and produce no durable artifact, so that it is fast and frictionless for daily orientation use.

13. As an office developer, I want to invoke `/grill-with-docs` and have Copilot search local documentation (README, docs/, ADRs, architecture notes, runbooks, domain glossary, existing specs) before grilling me, so that questions are grounded in what the team already knows.

14. As an office developer, I want `/grill-with-docs` to degrade cleanly to normal `/grill` when no local documentation exists, so that a fresh repo import does not break the skill.

15. As an office developer, I want `/grill-with-docs` to emit a documentation gap note when docs are absent, so that the team knows to create a `CONTEXT.md` or ADR.

16. As an office developer working on a large legacy monolith, I want `/legacy-explore` to explicitly check for generated code and warn me not to recommend modifying it, so that implementation plans never include edits to generated files.

17. As an office developer, I want `/legacy-explore` to detect stored procedure and database-touching surfaces and note the schema-change risk in the exploration record, so that `/write-plan` can account for migration requirements.

18. As an office developer, I want `/legacy-explore` to compute a blast-radius estimate (affected files, affected modules, caller count, confidence) so that `/write-plan` has a structured risk signal rather than a prose paragraph.

19. As an office developer, I want `/legacy-explore` to assess test surface quality (low / medium / high) so that characterization test recommendations appear in the planning record when coverage is weak.

20. As an office developer, I want `/legacy-explore` to detect slow-build or expensive-verification signals and record them as planning constraints, so that `/execute-plan` can account for build time in its phase strategy.

21. As an office developer, I want `/write-plan` to refuse to proceed if a required `LegacyExplorationRecord` is missing the new monolith fields, so that weak exploration cannot silently gate a risky plan.

22. As an office developer running `/verify`, I want the verification gate rules to be explicitly loaded in the agent session (not only documented in a separate file), so that Copilot enforces them rather than inferring them.

23. As an office developer running `/review`, I want the stage review rules to be explicitly loaded in the agent session, so that scope-check behavior is consistent across all review invocations.

24. As an office developer running `/execute-plan`, I want the phase checkpoint behavior to be explicitly loaded in the agent session, so that multi-step execution is resumable and checkpointed correctly.

25. As an office developer, I want the retrieval decision logic audited: if it is already covered by the context policy, it should be deleted from protocols; if it adds unique guidance, it should be wired to the relevant agent.

26. As an office developer importing this bundle into a new repo, I want a `VERSION` file at the `.github/` root so I know which version of the bundle I am running.

27. As an office developer, I want a `CHANGELOG.md` that lists each version's schema changes, new required fields, and breaking changes, so that I know what to re-run after an upgrade.

28. As an office developer upgrading the bundle, I want to invoke `/upgrade-workflow` and have Copilot scan all task artifacts for schema mismatches and either accept them, flag them as `migration_required`, or instruct me to regenerate from the previous phase.

29. As an office developer, I want task artifacts to declare `migration_required` state when a schema upgrade adds required fields they do not have, so that validators never silently reject old artifacts without a clear recovery path.

30. As an office developer, I want the `INSTALL.md` to include an Upgrading section that tells me: check the CHANGELOG, run CLI validators, handle any `migration_required` artifacts, so that upgrades have a documented safe path.

---

## Implementation Decisions

### Module 1 — Agent Tool Mapping

Four existing agents need corrected `tools:` declarations. The valid tool names per official Copilot docs are `read`, `edit`, `search`, `execute`, `agent`, `web`, `todo`, and MCP-namespaced tools. `codebase` is not valid and is silently ignored.

Mappings locked in grilling session:
- `grill`, `write-plan`, `legacy-explore`: `[read, search]`
- `execute-plan`: `[read, edit, search, execute]`

No schema or contract changes required. File edits only.

### Module 2 — Support Skills (1-Layer)

Five new skills using the hybrid architecture: `.agent.md` agent file + thin `.prompt.md` wrapper that references the agent via `#file:`. No schema, no contract, no validator. Each skill hands off to existing 3-layer phases rather than producing governed artifacts.

Tool grants:
- `diagnose`: `[read, search]` (analysis only; fix handoff goes to `/write-plan`)
- `tdd`: `[read, edit, search, execute]` (must run test commands)
- `safe-refactor`: `[read, search, edit]` (reads callers, edits only after plan confirmed)
- `zoom-out`: `[read, search]` (orientation only, no writes)
- `grill-with-docs`: `[read, search]` (doc discovery + grilling, no writes)

`grill-with-docs` special behavior: discover local docs first; if none, degrade to normal `/grill` and emit documentation gap note. Must not fabricate project context.

### Module 3 — Legacy Monolith Safety Enrichment

`/legacy-explore` agent instructions extended with five explicit protocol checks:

1. Test surface quality — search for test files, count coverage signals, rate low/medium/high
2. Generated code detection — look for generation markers, build tool outputs, do-not-edit headers
3. Stored procedure / DB-touching surface — detect SQL, ORM calls, migration files; note schema-change risk
4. Blast-radius via import graph — count direct callers, one-hop dependents, flag affected modules
5. Slow-build / expensive-verification signals — detect build tool configs, CI time signals, note in planning constraints

`LegacyExplorationRecord` schema extended with five new required fields:
- `blast_radius`: object with `affected_files`, `affected_modules`, `caller_count`, `confidence`
- `test_surface_quality`: enum `low | medium | high`
- `has_generated_code`: boolean
- `has_stored_procedures`: boolean
- `planning_constraints`: string array

Rule: values may be `"unknown"` with `confidence: low`. Silent omission is not acceptable. Unknown must be stated.

### Module 4 — Protocol Surface Wiring

Protocol files must be explicitly visible in Copilot plugin sessions. Hybrid reference pattern: each agent includes an inline rule summary (one sentence) plus an explicit `#file:` reference to the full protocol.

Wiring decisions:
- `verification-gate.md` → referenced in `/verify` agent
- `stage-review.md` → referenced in `/review` agent
- `phase-checkpoint.md` → referenced in `/execute-plan` agent
- `retrieval-decision.md` → audit: if content duplicates context policy → delete; if unique → wire to context-packet agent

Hard rule: any protocol file not referenced by at least one agent or instruction file after this work is deleted. No dead abstractions in v1.

### Module 5 — Versioning Infrastructure

New files:
- `VERSION` at `.github/` root — single line, semver (e.g., `1.0.0`)
- `CHANGELOG.md` at `.github/` root — append-only, one section per version with schema changes and migration notes
- `/upgrade-workflow` prompt + agent — scans `.github/tasks/` for artifacts whose `schema_version` does not match current schemas; emits per-artifact status: `compatible`, `migration_required`, or `regenerate`

Artifact version-binding rule: every task artifact already declares `schema_version` in `validated_under`. Validators must check this field against current schema and emit `migration_required` state rather than silent rejection when mismatch is detected.

`INSTALL.md` extended with Upgrading section: check CHANGELOG → run CLI validators → handle migration_required artifacts → re-run affected phases if needed.

---

## Testing Decisions

Good tests verify observable behavior through stable public interfaces, not internal implementation details.

**What makes a good test here:** run a validator against a known-good or known-bad artifact and assert pass/fail. Do not test internal YAML parsing — test that a correctly structured artifact passes and a structurally invalid one fails with a clear error.

**Modules to validate:**
- Agent tool declarations — verify each agent file's `tools:` field contains only recognized tool names (can be a static lint check)
- `LegacyExplorationRecord` schema — validate existing example artifacts pass; validate artifacts missing new required fields emit `migration_required`, not silent failure
- Protocol references — verify each protocol file is referenced by at least one agent or instruction (grep-based CI check is sufficient)
- VERSION file — verify it exists and parses as semver
- `/upgrade-workflow` output — run against a fixture directory containing one current-schema artifact and one stale artifact; assert correct status per artifact

Prior art: existing `validate-artifact` and `validate-manifest` Python validators in `.github/ai-workflow/validators/` follow the pattern of loading a YAML file, checking required fields, and emitting structured pass/fail output. New checks should follow the same pattern.

---

## Out of Scope

- `/triage`, `/to-issues`, `/to-prd` support skills — require GitHub MCP server, blocked by org policy in v1
- `/grill-with-docs` deepening with CONTEXT.md bootstrapping workflow — deferred to v1.1
- Full machine-readable schema compatibility matrix — deferred to v1.1
- `.agent.md` extension rename from `.md` — both valid per official docs, not a functional defect, deferred
- MCP server integration of any kind
- GitHub Issues integration
- AGENTS.md / CLAUDE.md as Copilot Chat instruction sources — cloud agent surface only, wrong for plugin-first

---

## Further Notes

The scope-lock model is the core value proposition of this workflow. Every agent that has unrestricted tools undermines that proposition entirely. The tool-mapping fix (Module 1) is the highest-priority item — it is two lines per agent file and should be the first commit.

Support skills (Module 2) should follow Matt Pocock's one-skill-one-function principle strictly. Each skill should be completable in a single Copilot Chat session without loading the entire workflow framework. Resist the temptation to add schema validation to support skills in v1.

The `/legacy-explore` enrichment (Module 3) is the highest-risk module. The schema change adds required fields, which means all existing `LegacyExplorationRecord` artifacts become stale. This should be implemented after the versioning infrastructure (Module 5) so that the migration path exists before the breaking schema change ships.

Suggested implementation order: Module 1 → Module 5 → Module 3 → Module 4 → Module 2.
