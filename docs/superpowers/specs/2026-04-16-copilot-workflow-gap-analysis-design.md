# Gap Analysis: GitHub Copilot Workflow System
**Date:** 2026-04-16
**Type:** Diagnostic — not a redesign

This document is a diagnostic pass over the existing GitHub Copilot workflow system (agents, prompts, skills, copilot-instructions.md). It identifies gaps, structural weaknesses, and feasibility boundaries. It does not propose solutions.

---

## Document Structure

**WORKFLOW.md** is the user-facing manual. It stays accessible and non-technical.
This document covers design-level analysis. Any future improvement specs live here in `docs/superpowers/specs/`, not in WORKFLOW.md.

---

## Core System Constraints

Four constraints run through every gap in this system. Referenced by ID throughout — not re-explained in each dimension.

**C1 — Stateless execution across phases**
No information persists across phase boundaries unless explicitly written to a file and explicitly reloaded. Every phase is a cold start.

**C2 — Weak artifact contracts**
Phase outputs exist but are not deterministically consumable by the next phase. They are human-readable, not execution-ready. The next phase must reinterpret instead of execute, leading to inconsistency and loss of intent.

**C3 — No native retrieval or discovery**
Copilot cannot discover or query relevant knowledge autonomously. Only explicitly referenced files can be used. No semantic search, ranking, or dynamic surfacing of prior knowledge exists.

**C4 — Context loading inefficiency**
Each phase rebuilds understanding by re-reading files. No caching, no incremental reuse, no reliable scoping. Cost and latency scale with repo size and number of phases.

**C5 — Limited execution control**
Agents cannot enforce behavior — only guide it. Adherence to rules depends on prompt strength, not guarantees.

---

## Evaluation Method

Each dimension follows this structure:
1. **What exists** — current mechanism as implemented
2. **What's missing / breaking** — gaps, inefficiencies, failure points
3. **Feasibility classification** — Impossible / Possible, missing / Possible, poorly structured
4. **Why it matters** — impact on reliability, DX, scalability, reasoning quality
5. **Root cause linkage** — constraint reference only, no re-explanation

---

## Dimension 1 — Workflow Quality (Phase Strength)

### 1. What exists

- Brainstorm: convergence criteria, structured summary (Problem / Success criteria / Constraints / Key risks)
- Planning: real file paths, no placeholders, ≤5 files per phase, execution mode annotation, engineer review prompts
- Execution: verification gate (evidence over claims), phased/inline modes, two-stage checkpoints, sub-agent isolation
- Review: five areas (spec coverage, verification evidence, test quality, security, deviations), severity tagging, CVE check

### 2. What's missing / breaking

- Brainstorm output is not a canonical artifact. Spec phase reconstructs intent from a lossy, human-pasted summary, causing drift between captured intent and encoded specification.
- Plans describe actions but not decision rationale. Under ambiguity, execution lacks a consistent basis for judgment, leading to divergent outcomes.
- Accepted deviations are ephemeral and non-recoverable. Divergence between plan and execution is lost once chat context is gone.
- Review validates presence of evidence, not correctness of coverage. There is no authoritative mapping between requirements and verification.
- No persistent lifecycle record of phase completion, acceptance, and commit state. Progress and auditability are not reconstructable.

### 3. Feasibility classification

- Canonical brainstorm artifact: **Possible, missing**
- Design rationale in plan: **Possible, missing**
- Deviation tracking in artifacts: **Possible, missing**
- Coverage mapping in review: **Possible, poorly structured** (verification exists but is not treated as source-of-truth)
- Phase completion signal: **Possible, missing**

### 4. Why it matters

Weak upstream outputs force downstream reinterpretation. Execution becomes probabilistic instead of deterministic. Variance accumulates across phases, making defects harder to trace and correct.

### 5. Root cause linkage

- C2 — Weak artifact contracts (primary)
- C1 — Stateless execution (deviation loss, handoff gaps)

---

## Dimension 2 — System Rigidity vs Usability

### 1. What exists

- Mandatory phase sequence with defined skip protocol
- Quick-task path for small changes
- Model routing table as single source of truth
- Hard rules in `copilot-instructions.md` (plan before code, verification before PR, etc.)

### 2. What's missing / breaking

- No gatekeeping at phase entry. Skills assume correct sequencing instead of validating prerequisites.
- Skip protocol is not recorded as structured state. Skips are only implicitly inferred and invisible downstream.
- Context hygiene summaries are inconsistent. No templated structure ensures reliable phase-to-phase continuity.
- Critical handoff data (artifact paths, required inputs) is not surfaced prominently, making continuation error-prone.
- No guided entry point. Workflow usability depends on prior knowledge rather than progressive discovery.

### 3. Feasibility classification

- Prerequisite checking at skill entry: **Possible, missing**
- Structured skip-state recording: **Possible, missing**
- Standardized context summary template: **Possible, poorly structured**
- Prominent artifact handoff output: **Possible, poorly structured**
- Enforcement beyond prompt guidance: **Impossible (C5)**
- Progressive discoverability: **Possible, missing**

### 4. Why it matters

Discipline enforced only by convention is unreliable under pressure. Without structural guidance, users default to skipping steps, weakening the system's guarantees.

### 5. Root cause linkage

- C5 — Limited execution control (primary)
- C2 — Weak artifact contracts (inconsistent summaries, handoffs)

---

## Dimension 3 — Context & Token Efficiency

### 1. What exists

- Phase isolation (new chat per phase) prevents context buildup
- Model routing reduces cost in execution phases
- Context hygiene summaries reduce reload size
- Conventions file as curated reference
- Sub-agent isolation with minimal scoped context

### 2. What's missing / breaking

- No amortization of exploration cost. Identical codebase discovery repeats across tickets with no reuse.
- Conventions are applied uniformly regardless of relevance, causing linear token overhead growth.
- No working context artifact. Each phase independently re-derives relevant files and modules.
- Large spec/plan artifacts exceed practical context limits, leading to implicit truncation or selective reading.
- Semantic search lacks protocol (no query strategy, stopping condition, or fallback), resulting in inconsistent coverage.

### 3. Feasibility classification

- Working context artifact: **Possible, missing**
- Conventions scope discipline: **Possible, poorly structured**
- Phase-relevant conventions subset: **Possible, missing**
- Semantic search protocol: **Possible, poorly structured**
- Cross-ticket exploration reuse (manual): **Possible, missing**
- Cached understanding across sessions: **Impossible (C1, C4)**

### 4. Why it matters

Context cost scales with repo size and phase count. Without reuse or scoping, the system degrades with scale and becomes unreliable for larger codebases.

### 5. Root cause linkage

- C4 — Context loading inefficiency (primary)
- C1 — Stateless execution (no reuse)
- C2 — Weak artifact contracts (no defined context artifact)

---

### Cross-Dimension Pattern (D1–D3)

- Outputs are not authoritative artifacts (C2)
- Phases act as independent interpreters, not deterministic executors (C1 + C2)
- Context is rebuilt instead of reused (C4)

The system behaves as loosely coupled reasoning steps rather than a deterministic workflow.

---

## Dimension 4 — Knowledge Capture & Traceability

### 1. What exists

- Spec file: requirements, constraints, edge cases, testing strategy
- Plan file: phased steps, file manifest, rollback plan, engineer review prompts
- Verification file: requirement-to-test mapping with evidence
- Brainstorm convergence message: problem, success criteria, constraints, risks (chat-based, not consistently persisted)

### 2. What's missing / breaking

- Decision rationale is not captured. The system has no memory of why a design was chosen — each ticket recomputes decisions without access to prior justification.
- No record of rejected alternatives. Absence of this creates decision space collapse — future work treats chosen designs as the only viable option.
- Execution discoveries are uncaptured signal from reality. Constraints and behaviors discovered during implementation are repeatedly rediscovered across tickets.
- No longitudinal knowledge accumulation. Each ticket operates as an isolated reasoning unit with zero carryover of experiential knowledge.
- Brainstorm output is not a canonical artifact (see D1). Early constraints and risks are not guaranteed to survive into formal artifacts.

### 3. Feasibility classification

- Decision rationale / rejected alternatives in spec: **Possible, missing**
- Execution discovery log per ticket: **Possible, missing**
- Post-ticket conventions update (human-curated): **Possible, missing**
- Automatic cross-ticket knowledge accumulation: **Impossible (C1, C3)**
- Canonical brainstorm artifact: **Possible, missing**

### 4. Why it matters

Without reasoning history, decisions are repeatedly made in isolation. Constraints already discovered are rediscovered, and prior tradeoffs are ignored. The system accumulates outputs but not intelligence.

### 5. Root cause linkage

- C1 — Stateless execution (primary)
- C2 — Weak artifact contracts

---

## Dimension 5 — Knowledge Base & Retrieval System

### 1. What exists

- `conventions/SKILL.md` as a single repo-specific reference
- Accumulating spec, plan, and verification artifacts in predictable paths
- `semantic_search` available to agents
- Active Context block (single-slot current feature)

### 2. What's missing / breaking

- Conventions are unstructured and grow linearly. They are accessed monolithically with no selective loading or scoping.
- No artifact index. Past work is non-addressable unless exact paths are known.
- `semantic_search` lacks protocol. Retrieval is non-repeatable and non-auditable.
- Active Context models current state only. It overwrites history and provides no temporal traceability.
- Artifacts lack metadata. Without consistent tagging, filtering and grouping are not possible even at file level.

### 3. Feasibility classification

- Artifact index (human-curated): **Possible, missing**
- Structured conventions (domain/module segmentation): **Possible, poorly structured**
- Artifact metadata / frontmatter schema: **Possible, missing**
- Semantic search protocol: **Possible, poorly structured**
- Active context history (append-based): **Possible, poorly structured**
- Dynamic retrieval / semantic discovery: **Impossible (C3)**

### 4. Why it matters

Accumulated artifacts without structure or index do not form a knowledge system. Signal does not compound — more files increase noise without increasing usability. The system cannot leverage its own history.

### 5. Root cause linkage

- C3 — No native retrieval (primary)
- C2 — Weak artifact contracts

---

## Dimension 6 — Human-in-the-Loop Knowledge Evolution

### 1. What exists

- Review checkpoints at phase transitions
- Engineer review prompts embedded in plan phases
- Review phase as a gate before PR
- Conscious skip protocol
- Spec review gate before planning

### 2. What's missing / breaking

- Checkpoints validate progression, not engagement. There is no guarantee that review questions were actually addressed.
- No learning loop. The system enforces delivery completeness but not knowledge extraction.
- No learning moment signal. High-signal events (unexpected behavior, constraint discovery) are not surfaced for capture.
- Approval applies to artifacts, not insights. Learned knowledge has no structured, approved path into persistence.
- Skip state is not visible downstream (see D2). Later phases cannot distinguish intentional skips from omissions.

### 3. Feasibility classification

- Structured review acknowledgment (explicit responses): **Possible, missing**
- Post-ticket learning prompt: **Possible, missing**
- Learning moment signals in skills: **Possible, missing**
- Skip-state visibility across phases: **Possible, missing**
- Automated knowledge capture without human approval: **Impossible (C1, C3, C5)**

### 4. Why it matters

The system enforces quality gates but not learning gates. Execution quality improves per ticket, but intelligence does not accumulate across tickets. The workflow is well-governed but not self-improving.

### 5. Root cause linkage

- C1 — Stateless execution
- C5 — Limited execution control
- C2 — Weak artifact contracts

---

### Cross-Dimension Pattern (D4–D6)

- Reasoning is not persisted as first-class data (C2)
- Learning does not accumulate across time (C1)
- Discovery is not structurally supported (C3)

The system captures outputs but not the intelligence behind them. Artifacts accumulate, but experience does not compound.

---

## Dimension 7 — UI / Developer Experience

### 1. What exists

- WORKFLOW.md: phase → agent → prompt → output mapping
- Context hygiene summary (summary, artifacts, next command)
- Phase handoff messages per skill
- Named agents (Design, Implementation, Review)
- Execution mode announcements and structured checkpoints

### 2. What's missing / breaking

- No persistent phase state indicator. State must be reconstructed from chat or files, both unreliable in practice.
- Context hygiene summaries are not canonical artifacts. Structure varies across agents, breaking consistency.
- No clear separation between agent output and required engineer action. Action points are not reliably distinguishable.
- Handoff messages do not prioritize critical data. Artifact paths are buried and easy to miss.
- Sub-agent invocation requires manual embedding of conventions. This step is opaque, error-prone, and not verifiable.

### 3. Feasibility classification

- Phase state persisted to disk: **Possible, missing**
- Standardized context summary template: **Possible, poorly structured**
- Consistent action-required formatting: **Possible, poorly structured**
- Artifact paths surfaced as primary output: **Possible, poorly structured**
- Sub-agent conventions embedding reliability: **Possible, poorly structured**

### 4. Why it matters

If interaction overhead exceeds workflow value, the system is bypassed. Friction at phase boundaries compounds across multi-phase work, reducing usability where structure is most needed.

### 5. Root cause linkage

- C1 — Stateless execution (primary)
- C2 — Weak artifact contracts

---

## Dimension 8 — Phase Handoff & Continuity

### 1. What exists

- Handoff sections in each skill (next phase, command, model)
- Context hygiene summaries as carry-forward mechanism
- File paths as continuity tokens
- "All Files Changed" manifest in plan
- Self-contained sub-agent prompts

### 2. What's missing / breaking

- No canonical artifact registry per ticket. Artifact discovery depends on memory or re-derivation.
- Context summaries are not persisted. Carry-forward depends on manual copy, introducing loss.
- Accepted deviations are not written back. Downstream phases operate on outdated plans.
- File manifests reflect plan intent, not execution reality. No authoritative post-execution state.
- Handoff messages specify commands but not required inputs, forcing reconstruction at each phase.

### 3. Feasibility classification

- Per-ticket artifact registry: **Possible, missing**
- Persisted context summary artifact: **Possible, missing**
- Plan amendment protocol (deviation write-back): **Possible, missing**
- Canonical post-execution file manifest: **Possible, missing**
- Explicit input specification in handoff: **Possible, poorly structured**

### 4. Why it matters

Handoff errors propagate silently. Incorrect inputs at phase boundaries cause downstream divergence that is hard to trace and expensive to debug.

### 5. Root cause linkage

- C1 — Stateless execution (primary)
- C2 — Weak artifact contracts

---

## Dimension 9 — Scalability Constraints (Large Repositories)

### 1. What exists

- Sub-agent isolation per phase
- Planning constraint (≤5 files per phase)
- Phase isolation via new chats
- Conventions file as curated reference

### 2. What's missing / breaking

- No scoped exploration protocol. Codebase discovery is unbounded and can exhaust context before planning completes.
- Conventions scale linearly but are applied uniformly, increasing token cost independent of relevance.
- No feature decomposition threshold. Large features generate oversized artifacts with no splitting guidance.
- Context limit failures are silent. Output may be truncated or incomplete without detection.
- `semantic_search` is unreliable at scale and lacks fallback, making discovery inconsistent.

### 3. Feasibility classification

- Scoped exploration protocol: **Possible, missing**
- Feature decomposition threshold: **Possible, missing**
- Phase-relevant conventions subset: **Possible, missing**
- Semantic search fallback protocol: **Possible, poorly structured**
- Context limit detection: **Impossible (C4, C5)**

### 4. Why it matters

The system degrades silently with scale. Large repositories expose its limits immediately, making it unreliable for real-world use.

### 5. Root cause linkage

- C4 — Context loading inefficiency (primary)
- C2 — Weak artifact contracts
- C5 — Limited execution control

---

## Dimension 10 — Alignment with Underlying System Philosophy

### 1. What exists

- Partial decision traceability in plan artifacts
- Structured reasoning capture via brainstorm output (one-shot)
- Human-in-the-loop approval gates
- Strong evidence-based verification

### 2. What's missing / breaking

- No append-only event log. There is no persistent record of decisions, deviations, or phase progression across tickets.
- Knowledge does not accumulate. Conventions remain static unless manually updated.
- No pattern extraction. Recurring behaviors and constraints are not captured structurally.
- Reasoning behind convergence is not preserved. Only final outputs exist, not the decision process.
- No compounding intelligence. System capability does not improve across tickets or sessions.

### 3. Feasibility classification

- Append-only phase/ticket log: **Possible, missing**
- Post-ticket conventions update loop: **Possible, missing**
- Pattern capture format in conventions: **Possible, missing**
- Decision reasoning capture in artifacts: **Possible, missing**
- Automatic compounding intelligence: **Impossible (C1, C3, C5)**
- Full philosophy alignment: **Impossible (partial alignment only)**

### 4. Why it matters

The system enforces correctness within a session but cannot improve over time. It prevents mistakes locally but cannot learn from them globally, setting a fixed ceiling on long-term value.

### 5. Root cause linkage

- C1 — Stateless execution (primary)
- C3 — No native retrieval
- C2 — Weak artifact contracts
- C5 — Limited execution control

---

### Cross-Dimension Pattern (D7–D10)

- Phase boundaries act as friction points rather than clean handoffs (C1, C2)
- Intelligence does not compound; the system operates at a fixed capability ceiling (C1, C3)
- Scalability failures are silent and undetected (C4, C5)

The system is optimized for single-session correctness, not multi-session learning or scale. As scope and usage grow, reliability degrades continuously without explicit signals.

---

## Consolidated Gap Map

| Dimension | Primary Constraint | Feasibility Profile |
|---|---|---|
| D1 — Workflow Quality | C2 | Mostly possible, missing |
| D2 — Rigidity vs Usability | C5 | Mix of missing and impossible |
| D3 — Context Efficiency | C4 | Possible, requires new artifacts |
| D4 — Knowledge Capture | C1 | Possible, missing |
| D5 — Knowledge Retrieval | C3 | Mostly impossible at dynamic layer; structural layer possible |
| D6 — Human Learning Loop | C1, C5 | Possible, missing (human-curated path only) |
| D7 — Developer Experience | C1, C2 | Possible, poorly structured |
| D8 — Phase Handoff | C1, C2 | Possible, missing |
| D9 — Scalability | C4 | Mix of possible and impossible |
| D10 — Philosophy Alignment | C1, C3 | Partial alignment is the realistic ceiling |

---

## What Can Be Improved vs. What Cannot

### Fundamentally impossible within current constraints
- Automatic cross-ticket knowledge accumulation
- Dynamic retrieval and semantic discovery
- Context limit detection and signaling
- Full philosophy alignment (compounding intelligence)
- Automated knowledge capture without human approval

### Possible with new structured artifacts
- Canonical brainstorm artifact
- Per-ticket artifact registry
- Decision rationale and rejected alternatives in spec
- Persisted context hygiene summary
- Execution discovery log
- Post-ticket learning prompt
- Append-only phase/ticket log
- Artifact metadata / frontmatter schema
- Artifact index

### Possible with better-specified existing mechanisms
- Conventions structure (domain/module segmentation)
- Context hygiene summary template (consistent schema)
- Semantic search protocol
- Handoff message format (input specification)
- Active context history (append vs. overwrite)
- Sub-agent conventions embedding

---

## Documentation Boundary

**WORKFLOW.md** — user-facing manual. Describes how to use the system. Should remain accessible, non-technical, and complete for any engineer picking it up for the first time. Changes here are UX changes.

**docs/superpowers/specs/** — design-level documentation. Covers system architecture, gap analysis, improvement specs. Not referenced during normal workflow use.

These two layers must not merge. Any future improvement work that touches both should update WORKFLOW.md for user-visible behavior changes and create a new spec here for the design rationale.
