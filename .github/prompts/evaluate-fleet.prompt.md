# /evaluate-fleet

Aggregate opt-in `SystemEvaluationReport`s from multiple developers or repositories to decide whether the main `.github` workflow bundle should change.

This command is for maintainers of the shared workflow bundle. It does not read source code, raw task logs, or private task artifacts. It only reads structured exported system-evaluation reports.

## Purpose

Local changes are allowed to stay local. The main `.github` bundle should change only when multiple independent users observe the same repeated problem.

Answer:

1. Which patterns repeat across developers/repositories?
2. Which local candidates should remain local?
3. Which candidates are strong enough for a main-bundle `/grill` improvement session?
4. What metric should improve if the shared bundle changes?

## Inputs

Read opt-in exported `SystemEvaluationReport` JSON files.

Do not read:

- raw logs
- source code
- individual task artifacts unless already summarized in the report
- private user notes

## Evidence Handling Policy

Fleet reports must not include raw excerpts or direct quotes from developer/source reports.

Use only:

- structured `evidence_refs`
- paraphrased summaries of repeated patterns
- aggregate counts and severity

The fleet report must include:

- `evidence_handling_policy.raw_excerpts_allowed: false`
- `evidence_handling_policy.evidence_refs_required: true`
- `evidence_handling_policy.summary_mode: paraphrased_patterns_only`
- `evidence_handling_policy.raw_detail_review_path: source_report_under_controlled_review`
- `evidence_handling_policy.raw_detail_reason_code_required: true`
- `evidence_handling_policy.allowed_raw_detail_reason_codes: [validate-pattern, resolve-ambiguity, audit-safety]`

If raw detail is needed, stop and ask for controlled review of the specific source report with one reason code:

- `validate-pattern`: confirm whether evidence really supports a repeated pattern
- `resolve-ambiguity`: disambiguate conflicting or unclear structured summaries
- `audit-safety`: inspect whether privacy, safety, or governance boundaries were violated

Do not copy raw detail into the fleet artifact.

When controlled raw-source detail is actually reviewed, create a `RawSourceReviewRecord` at:

`.github/tasks/fleet-evaluations/FLEET-EVAL-{YYYYMMDD}-{HHMMSS}/raw-source-reviews/RAW-SOURCE-REVIEW-{YYYYMMDD}-{HHMMSS}/raw-source-review.json`

The record must include `source_id`, `source_report_ref`, `source_fleet_evaluation`, `reason_code`, `requested_by_role`, `reviewed_at`, `evidence_refs`, and `outcome_summary`. It must set `raw_excerpts_included: false` and `copied_raw_detail: false`.

## Source Identity Policy

Require stable pseudonymous source IDs:

- Format: `SRC-{stable-token}`.
- Do not use real names, email addresses, or personal identifiers.
- Do not accept anonymous reports without a stable `source_id`.
- Treat duplicate `source_id` values as the same source, even if they come from different files.
- Use source IDs only to prove independence and avoid double-counting.

## Source Comparison Policy

Do not compare developers by source ID.

Source IDs are allowed only for:

- proving that a repeated pattern came from independent sources
- deduplicating multiple reports from the same source
- citing evidence without exposing real identities

Source IDs must not be used for:

- ranking developers
- scoring developer performance
- naming best/worst sources
- assigning blame
- creating per-source leaderboards

The fleet report must include:

- `source_comparison_policy.source_ids_used_for: independence_and_deduplication_only`
- `source_comparison_policy.developer_ranking_allowed: false`
- `source_comparison_policy.per_source_performance_scoring_allowed: false`

Compare workflow/system patterns, not people.

## Repository Hint Policy

`repository_hint` is optional and must be coarse/non-identifying.

Allowed examples:

- `swift-ios-app`
- `spring-boot-monolith`
- `node-library`
- `python-cli`
- `legacy-java-service`

Forbidden examples:

- repository URLs
- organization names
- company names
- exact repository names
- customer names
- personal names

Use repository hints only to distinguish universal patterns from stack-specific patterns.

## Applicability Rule

Classify every shared candidate as either:

- `universal`: The problem appears across different stacks or is clearly about the generic workflow machinery. It may be eligible for the default workflow.
- `stack_specific`: The problem is repeated but tied to a stack, migration class, framework family, or legacy-code shape. It must become optional profile guidance, not default workflow behavior.

Examples of stack-specific profile guidance:

- `swift-upgrade-profile`
- `spring-monolith-profile`
- `legacy-java-profile`

Do not overfit the default workflow to one ecosystem. A repeated Swift upgrade problem can justify a Swift upgrade profile; it does not automatically justify changing the default workflow used by every repository.

## Profile Mode Rule

V1 profiles are passive guidance only.

A stack-specific profile may adjust:

- prompt emphasis
- checklist wording
- retrieval hints
- examples
- risk reminders

A stack-specific profile must not override:

- diagnosis requirements
- TDD decision requirements
- scope locks
- verification gates
- evaluation gates
- human approval gates
- artifact schemas
- command phase order

Do not recommend a profile as a selectable execution mode in V1. If a profile needs different gates, record it as a blocked design question, not as an approved candidate.

## Metric Scope Rule

Profiles may introduce profile-specific diagnostic signals, but not new core success metrics.

Allowed profile diagnostic signals:

- `swift-upgrade-api-churn-surfaced-before-edit`
- `legacy-java-unsafe-refactor-risk-identified`
- `spring-monolith-bean-impact-map-recorded`

These signals can explain why a profile helped or failed. They must not replace or redefine the global evaluation metrics:

- task outcome
- process quality
- verification status
- scope adherence
- diagnosis usage
- TDD decision and execution
- human approval

Set `metric_scope: profile_diagnostic_signal` for stack-specific profile candidates. Set `metric_scope: core_metric` only for universal candidates.

Profile diagnostic signals must include both:

- `diagnostic_signal_id`: controlled kebab-case ID, such as `swift-upgrade-api-churn-surfaced-before-edit`
- `diagnostic_signal_explanation`: free-text explanation of what the signal means and why it matters

Use the ID for fleet grouping. Use the explanation for human interpretation. Do not use free text alone as the signal identity.

## Diagnostic Signal Alias Rule

Diagnostic signal IDs may be renamed or merged as V1 learning stabilizes, but only with an explicit alias record.

Use `diagnostic_signal_aliases` when:

- a signal name is unclear and should be renamed
- two signal IDs describe the same underlying signal and should be merged
- prior fleet reports used an older ID that should remain traceable

Each alias record must include:

- `alias_id`
- `action: rename | merge`
- `from_signal_id`
- `to_signal_id`
- `reason`
- `evidence_refs`
- `canonicalization_status: proposed`
- `requires_human_approval: true`
- `next_command: /grill`

Do not silently rename diagnostic signal IDs inside prose. Do not canonicalize aliases automatically. `/evaluate-fleet` may propose aliases only; canonical adoption requires `/grill task_type=system_improvement`. If no alias is needed, write `diagnostic_signal_aliases: []`.

## Main Bundle Promotion Rule

A candidate may be recommended for the shared `.github` bundle only when:

- It appears in at least 2 independent source reports, and
- It has evidence refs from those reports, and
- It maps to a shared workflow component rather than a project-specific preference.

V1 threshold is 2 independent sources. This is intentionally low for early adoption, but it is not permission to change the shared bundle automatically. Every main-bundle candidate must still go through `/grill task_type=system_improvement`.

If a candidate appears in only one source report, keep it in `local_only_candidates` unless severity is high and the human explicitly asks to investigate.

## Normalization Rule

Do not group reports by exact wording. Different developers will describe the same workflow issue differently.

Group candidate observations by normalized:

- `problem`
- `implicated_component`
- `target_surface`
- expected metric movement

When wording differs but the underlying issue is the same, choose one concise normalized `problem` description and cite all source reports in `evidence_refs`.

Do not merge observations when the implicated component or target surface differs materially. Similar symptoms can have different causes.

## Output

Save the report to:

`.github/tasks/fleet-evaluations/FLEET-EVAL-{YYYYMMDD}-{HHMMSS}/fleet-evaluation.json`

Required fields:

- `artifact_type: FleetEvaluationReport`
- `schema_version: fleet-evaluation.schema.v1`
- `fleet_evaluation_id`
- `created_at`
- `source_report_refs`
- `source_comparison_policy`
- `evidence_handling_policy`
- `sample_window`
- `cross_developer_patterns`
- `main_bundle_change_candidates`
- `diagnostic_signal_aliases`
- `local_only_candidates`
- `human_decision_request`
- `validated_under`

Each `main_bundle_change_candidates` item must include:

- `applicability_scope: universal | stack_specific`
- `default_workflow_eligible: true` only for universal candidates
- `profile_hint: null` for universal candidates
- `profile_hint: <coarse-profile-name>` for stack-specific candidates
- `profile_mode: not_applicable` for universal candidates
- `profile_mode: passive_guidance` for stack-specific candidates
- `metric_scope: core_metric` for universal candidates
- `metric_scope: profile_diagnostic_signal` for stack-specific candidates
- `diagnostic_signal_id: null` for universal candidates
- `diagnostic_signal_id: <controlled-kebab-case-id>` for stack-specific candidates
- `diagnostic_signal_explanation: null` for universal candidates
- `diagnostic_signal_explanation: <free-text explanation>` for stack-specific candidates

After writing, present:

```text
--- FLEET EVALUATION ---
Source reports: <N>

Cross-developer patterns:
1. <pattern_id>: <problem> | sources=<N> | component=<component>

Main bundle candidates:
1. <candidate_id>: <recommended_action> | scope=<universal|stack_specific> | default_eligible=<true|false> | profile=<profile_hint|null> | profile_mode=<not_applicable|passive_guidance> | metric_scope=<core_metric|profile_diagnostic_signal> | signal=<diagnostic_signal_id|null>

Diagnostic signal aliases:
1. <alias_id>: <action> <from_signal_id> -> <to_signal_id> | status=proposed | next=/grill

Local-only candidates:
1. <candidate_id>: <reason>

Recommended human decision:
<human_decision_request.question>

Next command:
/grill task_type=system_improvement triggered_by=<fleet-evaluation.json> failure_category=<top pattern id>
---
```

Do not apply any shared workflow change from this report. A human must choose a candidate and run `/grill`.
