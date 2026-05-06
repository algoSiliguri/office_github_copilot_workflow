# Fleet Evaluation

Use this skill when maintainers want to aggregate multiple developers' `SystemEvaluationReport`s and decide whether the shared `.github` workflow bundle should change.

## Core Rule

The shared bundle changes only from repeated, opt-in, structured observations across independent users or repositories. Local observations can stay local.

## Method

1. Read exported `SystemEvaluationReport` JSON files only.
2. Require stable pseudonymous source IDs in the format `SRC-{stable-token}`.
3. Allow optional coarse `repository_hint` values such as `swift-ios-app`, but reject identifying names or URLs.
4. Use source IDs only for independence and deduplication; do not rank, score, or blame developers.
5. Emit evidence refs and paraphrased pattern summaries only; do not include raw excerpts or direct quotes from source reports.
6. Set `evidence_handling_policy.raw_excerpts_allowed: false`, `evidence_refs_required: true`, `summary_mode: paraphrased_patterns_only`, `raw_detail_review_path: source_report_under_controlled_review`, `raw_detail_reason_code_required: true`, and allowed raw-detail reason codes `validate-pattern`, `resolve-ambiguity`, and `audit-safety`.
7. If controlled raw-source detail is actually reviewed, create a minimal `RawSourceReviewRecord` with no raw excerpts.
8. Group repeated patterns by normalized problem, implicated component, target surface, expected metric movement, and coarse repository hint when useful.
9. Promote a pattern to `main_bundle_change_candidates` only when at least 2 independent sources support it.
10. Classify every shared candidate as `universal` or `stack_specific`.
11. Mark only `universal` candidates as `default_workflow_eligible: true`.
12. Route `stack_specific` candidates to optional profile guidance with a coarse `profile_hint`, such as `swift-upgrade-profile` or `legacy-java-profile`.
13. Set `profile_mode: passive_guidance` for stack-specific candidates; V1 profiles are not selectable execution modes.
14. Set `metric_scope: profile_diagnostic_signal` for stack-specific candidates and `metric_scope: core_metric` for universal candidates.
15. For profile diagnostic signals, set a controlled kebab-case `diagnostic_signal_id` plus a free-text `diagnostic_signal_explanation`.
16. Record diagnostic signal renames or merges in `diagnostic_signal_aliases` as proposed aliases requiring `/grill`; use an empty list when none are needed.
17. Keep one-off or project-specific candidates in `local_only_candidates`.
18. Produce a `FleetEvaluationReport`.
19. Recommend `/grill task_type=system_improvement ...` for any shared-bundle candidate.

## Constraints

Do not read raw logs, source code, or private task artifacts.

Do not include raw excerpts or direct quotes from developer/source reports in fleet artifacts. Use evidence refs plus paraphrased summaries only.

Do not request raw source-report detail without a controlled reason code: `validate-pattern`, `resolve-ambiguity`, or `audit-safety`.

Do not perform controlled raw-source review without creating `RawSourceReviewRecord`. The record must summarize the outcome without copying raw detail.

Do not collect real names, email addresses, repository URLs, organization names, company names, exact repository names, customer names, or personal names. Do not accept anonymous reports without stable pseudonymous source IDs.

Do not compare, rank, score, or blame developers by source ID. Source IDs exist only to prove independence, deduplicate reports, and cite evidence safely.

Do not group by exact candidate wording. Normalize semantically equivalent observations, but do not merge similar symptoms when the implicated component or target surface differs.

Do not edit prompts, schemas, validators, command contracts, policies, or instructions.

Do not overfit the default workflow to one ecosystem. Repeated Swift, Spring, or legacy-code issues may justify optional profile guidance; they do not automatically justify default workflow changes.

Do not let profiles override diagnosis, TDD decisions, scope locks, verification, evaluation, human approval, artifact schemas, or command phase order.

Do not let profiles redefine global success metrics. Profiles may add diagnostic signals only; global evaluation metrics must remain comparable across profiles and repositories.

Do not use free text alone as a diagnostic signal identity. Use controlled kebab-case signal IDs for grouping and free text for explanation.

Do not silently rename or merge diagnostic signal IDs. Use `diagnostic_signal_aliases` so historical fleet trends remain traceable.

Do not canonicalize diagnostic signal aliases automatically. Alias adoption requires human approval through `/grill task_type=system_improvement`.

Do not claim the shared workflow improved. V1 only aggregates observations and asks for human approval.

V1 threshold is 2 independent sources plus a required `/grill` human decision before any shared `.github` change.
