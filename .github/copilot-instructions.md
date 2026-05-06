# GitHub Copilot Enterprise — Workflow Instructions

This repo ships a portable AI workflow for IntelliJ Copilot Chat and Copilot CLI.
Project-specific config: `.github/workflow/config.yaml` — written by `/setup-workflow`, never edit manually.

## Available commands

| Command | Phase | Primary surface |
|---|---|---|
| `/setup-workflow` | Bootstrap | Plugin |
| `/diagnose` | Bug/regression diagnosis | Plugin + CLI |
| `/grill` | Problem exploration + decisions | Plugin |
| `/legacy-explore` | Legacy/ambiguity gate (advanced) | Plugin |
| `/write-plan` | Scope lock | Plugin |
| `/context-packet` | Retrieval prep (conditionally mandatory) | Plugin |
| `/execute-plan` | Implementation | Plugin + CLI |
| `/verify` | Evidence-backed verification | CLI |
| `/review` | Scope-check before merge | Plugin |
| `/evaluate` | Human-confirmed task evaluation | Plugin |
| `/evaluate-system` | Retrospective over completed task artifacts | Plugin |
| `/evaluate-fleet` | Cross-developer retrospective over exported system evaluations | Plugin |
| `/quick-task` | Lightweight path | Plugin |

## Workflow phase order

```
setup-workflow → [diagnose for bugs/regressions] → grill → [legacy-explore if required] → write-plan → [context-packet] → execute-plan → verify → review → evaluate → [evaluate-system periodically]
                                              ↑
                                         quick-task (parallel escape hatch)

Shared workflow maintainers may additionally run:

```
evaluate-system exports from multiple developers → evaluate-fleet → grill system_improvement
```
```

## Permission ladder

| Tier | Actions | Approval required |
|---|---|---|
| 1 | Read, search, explain | None |
| 2 | Edit declared in-scope files | Plan scope |
| 3 | CLI handoff, run commands | Human-approved handoff block |
| 4 | Schema, contract, manifest changes | Explicit human instruction |

## Output contract

All phase state via status blocks — never prose paragraphs.

```
STATUS: [phase] | SURFACE: [plugin|cli] | SCOPE: [N files] | NEXT: [command]
```

## CLI handoff rules

Triggers:
1. Plan step declares `preferred_surface: copilot_cli`
2. Verification requires running commands
3. Scope spans >5 files with non-trivial changes

Always show CLI handoff block and wait for human approval before switching surfaces.

## Enforcement model

v1 is a governed convention system. Validators are deterministic gates but only run when invoked. No phase is complete unless required validators were run and output was shown in the completion block. Invalid artifacts are detectable, not impossible. Hard enforcement via CLI wrapper, Git hooks, or CI is a v2 feature.

Every command completion block must include:
- `VALIDATORS_REQUIRED:` list of required validators for this phase
- `VALIDATORS_RUN:` list actually run, with pasted output
- `ARTIFACTS_WRITTEN:` list of artifact paths written
- `NEXT_ALLOWED:` next allowed command

## Precedence chain

When rules conflict, the higher layer wins:
1. `.github/copilot-instructions.md` — always-on
2. `manifest` / `contracts` / `schemas` / `policies` / `validators` — governance authority
3. `protocols/` — reusable cross-cutting decision procedures (not governance authority)
4. `prompts/` — command invocation layer
5. `skills/` — phase procedure layer
6. `docs/` — explanation only
7. `agents/` — non-canonical / advisory

## Runtime scope

v1 primary runtime: GitHub Copilot Chat in JetBrains. `copilot-instructions.md` is the canonical always-on entrypoint. Governance files are runtime-neutral. Other LLM runtimes (Claude Code, etc.) require their own entrypoint setup — see `CLAUDE.md` at repo root.

## V1 Readiness

V1 is stable for local/plugin use when `.github/ai-workflow/validators/validate-release-readiness` passes. V1 is not self-modifying; system and fleet evaluations produce candidate improvements only, and shared workflow changes require human-approved `/grill task_type=system_improvement`.

## Hard rules

- No task done without `VerificationRecord` containing command output
- No bugfix planning without diagnosis when reproduction/root cause is unclear
- Bugfix GrillRecords must reference `source_diagnosis` when a DiagnosisRecord exists
- Low-confidence diagnosis blocks production-fix planning; only reproduction tests, instrumentation, or test-surface improvement may proceed
- `/evaluate` must report task outcome and process quality separately; never hide process violations inside a successful task result, and never downgrade criteria-derived task outcome solely because process quality failed
- `/evaluate-system` converts completed task artifacts into aggregate metrics, repeated problem patterns, and human-approved improvement candidates; use structured JSON first, raw logs only as cited evidence for a specific pattern, run it periodically, and never let it self-modify the workflow
- `/evaluate-system` may set `implicated_component`, but it is a hypothesis, not blame; use `unknown` when evidence is insufficient
- `/evaluate-fleet` may recommend main `.github` bundle changes only from opt-in structured SystemEvaluationReports across at least 2 independent sources; this is a V1 recommendation threshold only, and every shared change still requires `/grill`
- `/evaluate-fleet` requires stable pseudonymous `SRC-*` source IDs; do not collect real names, email addresses, or anonymous untraceable reports
- `/evaluate-fleet` uses source IDs only for independence, deduplication, and safe evidence refs; never rank, score, or blame developers by source ID
- `/evaluate-fleet` must not include raw excerpts or direct quotes from developer/source reports; use evidence refs plus paraphrased pattern summaries only
- `/evaluate-fleet` raw source-report drilldown requires controlled review with reason code `validate-pattern`, `resolve-ambiguity`, or `audit-safety`
- Controlled raw source-report drilldown must create `RawSourceReviewRecord`; the record may contain outcome summary and evidence refs only, never raw excerpts or copied raw detail
- `/evaluate-fleet` may use optional coarse `repository_hint` values like `swift-ios-app`; do not collect repo URLs, organization names, company names, exact repo names, customer names, or personal names
- `/evaluate-fleet` groups repeated observations by normalized problem, implicated component, target surface, and expected metric movement, not exact wording
- `/evaluate-fleet` must classify shared candidates as `universal` or `stack_specific`; only universal candidates may be default-workflow eligible, while stack-specific candidates become optional profile guidance
- Stack-specific profiles are passive guidance only in V1; they must not override diagnosis, TDD decisions, scope locks, verification, evaluation, human approval, artifact schemas, or command phase order
- Stack-specific profiles may add diagnostic signals, but they must not redefine global success metrics; fleet comparison depends on stable core metrics
- Profile diagnostic signals require controlled kebab-case IDs plus free-text explanations; do not aggregate signals by free text alone
- Diagnostic signal IDs may be renamed or merged only through explicit `diagnostic_signal_aliases` records in `/evaluate-fleet`; never silently rename signals in prose
- `/evaluate-fleet` may propose diagnostic signal aliases only; canonical alias adoption requires `/grill task_type=system_improvement`
- No edits outside declared plan scope
- No CLI handoff without human approval
- No plan creation until GrillRecord has `decision: proceed`
- No plan creation when GrillRecord says exploration is required and no LegacyExplorationRecord exists
- No plan creation without explicit `retrieval_decision` and `tdd_decision`
- TDD is mandatory for behavior-changing work unless the plan records a concrete non-applicability reason
- `/quick-task` may bypass retrieval, TDD, and full evaluation only when `bypass_justification` records concrete reasons for all three
- All full-workflow runtime artifacts saved as JSON under `.github/tasks/TASK-{NNN}/`; system evaluations live under `.github/tasks/system-evaluations/SYS-EVAL-{YYYYMMDD}-{HHMMSS}/`; fleet evaluations live under `.github/tasks/fleet-evaluations/FLEET-EVAL-{YYYYMMDD}-{HHMMSS}/`

## Instruction hierarchy

`.github/copilot-instructions.md` is always-on. `.github/instructions/*.instructions.md` may add scoped instructions. `.github/prompts/*.prompt.md` are reusable user-invoked prompts. Only `.agent.md` files under `.github/agents/` should be treated as supported custom agent profiles.

Manifest at `.github/ai-workflow/manifest.yaml` is a machine-readable registry for CLI validators only — do not load it as an instruction source.
