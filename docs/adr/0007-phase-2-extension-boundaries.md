# Phase 2 Extension Points Are Read-Only Seams on Phase 1 Artifacts

Phase 1 produces stable, validated artifacts: GraphRecord, PlanRecord, ExecutionRecord, VerificationRecord, ReviewRecord, SessionEventLog, MemoryCandidate, and EvalSummary. Phase 2 capabilities — context packet builder, memory retrieval, eval aggregation, dashboard, and cross-repo knowledge — must read these artifacts without mutating them. A phase 2 component that writes to a phase 1 artifact path would corrupt the artifact chain and invalidate the validator guarantees that phase 1 depends on.

**Considered Options**

- Allow phase 2 components to extend phase 1 artifacts in place by adding optional fields.
- Require phase 2 components to read phase 1 artifacts as immutable inputs and write only to separate phase 2 output paths.

**Consequences**

Phase 1 artifact contracts are frozen at their schema versions. Phase 2 reads them but does not own or mutate them. Specific seams:

- **Context packet builder** reads PlanRecord, GraphRecord, and accepted MemoryCandidates. Writes to a separate context packet path, not back to plan.json.
- **Memory retrieval** reads accepted MemoryCandidates from `.github/local-memory/accepted/`. It cannot write to inbox, accepted, or rejected directories; only the human approval gate may promote candidates.
- **Eval aggregator** reads completed task artifact sets and EvalSummary runs from `.github/evals/runs/`. It cannot write back to task artifacts.
- **Dashboard** reads eval outputs. It cannot write to any workflow artifact path.
- **Cross-repo import** is advisory only. Imported knowledge may be proposed as a MemoryCandidate (subject to the human approval gate) but never written directly into phase 1 artifacts.

`evaluate-tasks` is the only phase 1 component permitted to write eval outputs, and only to `.github/evals/runs/`. Hook scripts are the only phase 1 components permitted to write to event logs. `/setup` is the only component permitted to write to GraphRecord.
