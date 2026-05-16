# Evidence Policy Heuristics Stay in Python Code, Not Config

The term lists used to detect graph-as-proof violations (`GRAPH_TERMS`, `PROOF_TERMS`, `COMMAND_TERMS` in `evidence_policy.py`) are kept as Python constants rather than moved to `orchestration.json`, contrary to the pattern in ADR-0004.

**Considered Options**

- Declare term lists in `orchestration.json` under `verify_contract.graph_proof_detection`, consistent with ADR-0004.
- Keep term lists as internal constants inside `evidence_policy.py`.

**Consequences**

The term lists are implementation details of a detection heuristic, not governance policy. The governance policy — "Graphify must not be used as correctness evidence" — is already stated in CONTEXT.md (Graph Verification Boundary) and enforced at the seam: `uses_graph_as_proof(summary) -> bool`. Exposing the vocabulary lists as config would publish implementation details as policy, invite callers to reason about the lists rather than the predicate, and make the heuristic harder to evolve as a unit. The seam is the predicate; what's behind it is internal.
