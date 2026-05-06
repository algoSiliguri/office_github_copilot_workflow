# Effective Usage

## Mental model

This workflow is designed to make agent work auditable and bounded:

- discovery first
- explicit decisions before planning
- locked scope before editing
- verification with real command evidence
- review before merge

The goal is not to slow down simple work. The goal is to prevent unbounded agent drift on medium and large changes.

## When to use each path

Use `/quick-task` when:

- the change is small
- files are already known
- no broad exploration is needed
- you do not need a multi-step plan artifact

Use the full workflow when:

- requirements are ambiguous
- more than a few files may change
- architectural tradeoffs matter
- verification needs to be explicit
- you want a durable artifact trail in `.github/tasks/`

## Recommended command sequence

### 1. `/setup-workflow`

Run this once after installation or when project commands change.

Use it to establish the generated config that later phases depend on.

### 2. `/grill`

Use this before planning. Good usage means being concrete about:

- the actual user-visible goal
- what must not change
- risks and failure modes
- alternatives you are rejecting

Weak inputs here create weak plans later.

### 3. `/legacy-explore`

Run this only when ambiguity is real:

- target files are unknown
- module ownership is unclear
- tests are weak
- several subsystems may be involved

Do not use it as default repo-wide exploration.

### 4. `/write-plan`

This is the scope lock. A good plan:

- lists every file expected to change
- explicitly names nearby files that are out of scope
- defines exact verification commands
- states whether CLI handoff is allowed or required

If the file list is vague, the plan is weak.

### 5. `/context-packet`

**Conditionally mandatory.** The `context_packet_required` flag in the `PlanArtifact` determines whether this step is required. When `context_packet_required: true`, `/execute-plan` will stop at preflight if `context-packet.json` is absent.

Use when execution needs bounded retrieval across more than a tiny surface area. You may skip it for straightforward changes in familiar code only when the plan explicitly sets `context_packet_required: false`.

### 6. `/execute-plan`

This phase should be boring. If execution discovers new files are needed, stop and update the plan rather than editing opportunistically.

That is a feature, not friction.

### 7. `/verify`

This is mandatory for done-state claims. The verification command must be run exactly as declared, and the output must be captured as evidence.

No evidence, no verified completion.

### 8. `/review`

Use this as the final check that:

- implementation stayed within scope
- verification was real
- the outcome matches the plan

On PASS or PASS_WITH_DEGRADATION, `/review` automatically triggers `/evaluate`. No manual invocation needed.

### 9. `/evaluate`

Triggered automatically after a passing review. Scores the task against declared success criteria and produces an EvaluationRecord for your confirmation.

You will see a confirmation block. Respond with:
- `confirm evaluation by <your name>` — marks the record authoritative
- `override evaluation: <category> — <details>` — records your disagreement with a structured reason

A confirmed or overridden EvaluationRecord is the terminal artifact of every completed task.

## Improvement loop

After `/evaluate` completes, the completion block surfaces:

- `improvement_signal` — a categorised signal (e.g. prompt gap, skill gap, protocol missing)
- unmet criteria IDs (e.g. SC-003, SC-007)
- `suggested_next_action` — a pre-filled `/grill` invocation you can run or discard

**No automatic task creation.** Humans drive the loop:

1. Review the unmet criteria IDs and the suggested `/grill` invocation.
2. Decide whether to run it, modify it, or discard it.
3. If you proceed: populate `triggered_by` in the new grill with references to the EvaluationRecord files and the `failure_category`.
4. Run the full workflow. The resulting change (updated prompt, skill, or schema) is versioned, verified, and reviewed like any other task.

No automated writes to system files. Every improvement is an evaluatable task. Every task is traceable to the evidence that justified it.

## Effective operating habits

- Start with `/quick-task` only when the change is truly narrow.
- Prefer the full flow for anything that could branch into architecture decisions.
- Keep `files_in_scope` tight. Large scope invites sloppy execution.
- Treat CLI handoff as a controlled escalation, not a convenience shortcut.
- Put all generated artifacts under `.github/tasks/TASK-{NNN}/`.
- Use strict JSON filenames for runtime artifacts such as `task-manifest.json`, `grill.json`, `plan.json`, `execution.json`, `verification.json`, `review.json`, and `evaluation.json`.
- Re-run validation after changing workflow files.

## CLI handoff guidance

CLI handoff is appropriate when:

- a plan step explicitly requires CLI
- tests or verification commands must run
- changes span more than five files with non-trivial edits

When using CLI handoff, keep the allowed command list exact and narrow.

## Governance rules

Treat these as high-control files:

- `ai-workflow/manifest.yaml`
- `ai-workflow/schemas/*`
- `ai-workflow/validators/*`

Changes there should be deliberate, reviewed, and re-validated.

## Minimum validation set

```bash
python3 .github/ai-workflow/validators/bootstrap
python3 .github/ai-workflow/validators/validate-manifest
python3 .github/ai-workflow/validators/validate-config .github/workflow/config.yaml
```
