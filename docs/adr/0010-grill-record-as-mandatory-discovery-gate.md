# GrillRecord as Mandatory Discovery Gate Before Planning

`/grill` must produce a human-approved `grill.json` (GrillRecord) before `check-plan` will evaluate any PlanRecord. `check-plan` enforces two subset invariants against the GrillRecord:

- `plan.intended_files ⊆ grill.impacted_files` — the plan may not touch files the grill never examined
- `plan.verification_commands ⊆ grill.mandatory_verification_steps` — the plan's commands must come from the grill-approved verification pool

The GrillRecord carries a full ApprovalRecord (`human_approval`) using the canonical `approval_model.py` structure with `kind: "grill"`. This is the Discovery Gate, distinct from the Commitment Gate on the PlanRecord.

**Considered Options**

- Keep `/grill` advisory only (produces discussion, no artifact) — rejected. Without a machine-readable output, `check-plan` cannot enforce scope containment or verification command provenance. AI context decay between the grill session and plan generation loses constraints.
- Have `/grill` write a draft that the AI later inlines into the plan — rejected. Inlining puts the AI in control of both the constraint definition and the plan that satisfies it.
- Require a human-approved GrillRecord as a prerequisite artifact for `check-plan` — chosen.

**Consequences**

- Every task now has a mandatory `/grill` phase before `/plan`. The full lifecycle is: `/setup` → `/grill` → `/plan` → `/execute` → `/verify`.
- `orchestration.json.phase_order` must expand from `["setup", "plan", "execute", "verify"]` to `["setup", "grill", "plan", "execute", "verify"]`.
- `check-state`'s task-closure logic must account for the new artifact set.
- The GrillRecord schema must be added: `schema_version`, `task_id`, `grilled_at`, `impacted_files`, `mandatory_verification_steps`, `human_approval`.
- `check-plan` gains a new pre-flight: load `grill.json`, validate its ApprovalRecord, then run the subset checks before any existing plan validation.
- Quick tasks (`is_quick_task: true`) may need an exemption policy for the grill gate, to be defined in `orchestration.json.plan_contract`.
