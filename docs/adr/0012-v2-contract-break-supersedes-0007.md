# V2 Contract Break — Phase 1 Artifact Schemas Unfrozen for Security Hardening

Status: supersedes 0007 (Phase 2 Extension Points Are Read-Only Seams on Phase 1 Artifacts)

ADR-0007 froze phase 1 artifact contracts at their schema versions to protect read-only seam guarantees. The v2 security hardening decisions documented in ADRs 0008–0011 require incompatible changes to six phase 1 contracts. This ADR authorises the break.

## What changes in v2

- `plan-record.schema.v1` → `plan-record.schema.v2`: `verification_command` (string) replaced by `verification_commands` (array of command arrays); `quick_task_classification` field removed entirely.
- `verification-record.schema.v1` retired: replaced by `verification-draft.schema.v2` (AI-written semantic fields only) and `verification-receipt.schema.v2` (script-written facts merged with human review disposition).
- `review-record.schema.v1` retired: review fields folded into `verification-receipt.schema.v2`.
- `phase_order` in `orchestration.json` expands from `["setup", "plan", "execute", "verify"]` to `["setup", "grill", "plan", "execute", "verify"]`.
- `quick_task_classification` and all `graph_light_quick_task` logic removed from validators, schemas, and config.
- `approval_kinds` in `orchestration.json` gains `"grill"` and `"requirements"`.

## Why this break is acceptable

The entire phase 1 artifact chain existed within a single non-production bundle. There are no external consumers depending on schema version stability. The security vulnerabilities the v2 architecture closes (agent-writable verification commands, unfalsifiable receipt generation, no pre-plan blast-radius gate) are more important than schema stability at this stage.

## V1 artifacts

Existing v1 artifacts (verification-record.schema.v1, review-record.schema.v1) are retired. Task example fixtures under `.github/examples/tasks/TASK-001/` are migrated to v2 schemas. No backward-compatibility shims.
