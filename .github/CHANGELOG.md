# Changelog

All schema changes, new required fields, and breaking changes are documented here.
Format: `## [version] — YYYY-MM-DD`. New versions prepended at top. Old entries never edited.

---

## 2026-05-06 — v1 hardening (governance lock)

Locked in a grill session and implemented across docs, schemas, and prompts/skills.

### Enforcement & architecture
1. **Enforcement model clarified.** v1 is a *governed convention system with deterministic validators and human-enforced gates* — not runtime enforcement. Hard enforcement (CLI wrapper, Git hooks, CI) is deferred to v2.
2. **Two-layer behavior spec.** `prompts/` is the invocation layer (intent + entry contract); `skills/` is the procedure layer (executable steps). `agents/` is non-canonical/advisory. Precedence chain: `copilot-instructions.md` > governance > protocols > prompts > skills > docs > agents.
3. **Single artifact root.** `tasks/TASK-NNN/` is the only runtime artifact location. `ai-workflow/artifacts/examples/` exists exclusively for test fixtures and validator regression cases.
4. **Copilot/JetBrains-primary framing.** v1 ships as a Copilot/JetBrains-native workflow bundle. Other LLM runtimes may consume the same governance files but require their own entrypoint setup. `CLAUDE.md` at repo root provides the Claude Code entrypoint.
5. **`validate-manifest` upgraded.** Now checks both internal validity AND filesystem consistency: every file declared in the manifest must exist on disk, and every governed file on disk must be registered in the manifest.
6. **Protocols promoted to layer 3.** `protocols/` sits between governance and prompts/skills. Every protocol must be referenced by at least one prompt or skill.
7. **`/diagnose` deferred to v2.** Removed from v1 command lists. Referenced as a future v2 diagnostic command only.

### Schemas & artifacts
8. **Structured success criteria (`grill.schema.v2`).** `success_criteria` are now structured objects: `id` (SC-001 form), `description`, `verification_type`, `verification_command`, `expected_signal`, `observable: true`. Free-text criteria are rejected by the schema.
9. **`/quick-task` governance.** 8 eligibility rules (max 2 files, no protected file types, etc.). Every invocation produces a `QuickTaskRecord` with an `eligibility_check` block. Escalation is a hard stop — the agent cannot continue under `/quick-task` once any rule fails.
10. **`/context-packet` is conditionally mandatory.** No longer "optional." The `context_packet_required` flag in the `PlanArtifact` controls it. `/execute-plan` preflight halts if the flag is true and `context-packet.json` is absent.
11. **TaskManifest single terminal write.** `/evaluate` writes the `TaskManifest` exactly once, after human confirmation or override, setting `phase: evaluated`, `status: completed`, `evaluated_at`, and `artifact_refs.evaluation`. No intermediate writes during draft.

### Evaluation & improvement loop
12. **Outcome bands.** Four-band classification: `success` (rate == 1.0), `partial_success_high` (rate >= 0.8), `partial_success_low` (rate >= 0.5), `failure` (rate < 0.5 or review failed). `EvaluationRecord` adds `criteria_count`, `criteria_met_count`, `criteria_unmet_count`, `outcome_band`.
13. **Improvement signal surfaced, not auto-actioned.** `/evaluate` completion block shows `improvement_signal`, unmet criteria IDs, and a `suggested_next_action` containing a pre-filled `/grill` invocation. No automatic task creation — humans drive the loop.

---

## [1.0.0] — 2026-05-04

### Baseline release

**Agent tool declarations**
- Fixed invalid `tools: [codebase]` in all four agent files. `codebase` is not a recognized tool name and was silently ignored, leaving all agents with unrestricted tool access.
- Correct mappings: `grill`, `write-plan`, `legacy-explore` → `[read, search]`; `execute-plan` → `[read, edit, search, execute]`

**New support skills (1-layer)**
- `/diagnose` — disciplined bug investigation loop
- `/tdd` — red-green-refactor loop grounded in repo test runner
- `/safe-refactor` — bounded refactor planning with blast-radius analysis
- `/zoom-out` — lightweight codebase orientation, no artifact, no gate
- `/grill-with-docs` — doc-grounded grill variant, degrades to `/grill` when no docs exist

**`LegacyExplorationRecord` schema — breaking change**
- Added 5 new required fields: `blast_radius`, `test_surface_quality`, `has_generated_code`, `has_stored_procedures`, `planning_constraints`
- **Migration:** existing `LegacyExplorationRecord` artifacts from before this version will be flagged `migration_required` by `validate-artifact`. Re-run `/legacy-explore` for any affected task to regenerate.

**Protocol surface wiring**
- `verification-gate.md` → wired to `/verify` and `/quick-task` agents
- `stage-review.md` → wired to `/review` agent
- `phase-checkpoint.md` → wired to `/execute-plan` agent
- `retrieval-decision.md` → wired to `/write-plan` agent

**Versioning infrastructure**
- Added `VERSION` file at `.github/VERSION`
- Added this `CHANGELOG.md`
- Added `## Upgrading` section to `INSTALL.md`
- Added `/upgrade-workflow` command
- `validate-artifact` now emits `migration_required` state on schema version mismatch instead of hard failure
