# Policy Values Live in orchestration.json, Not Python Constants

Governance-relevant values that define what the workflow permits — governance and memory path prefixes, the graph refs cap, and the approval kind registry — are declared in `orchestration.json` rather than as hardcoded constants in validator modules. Validators load these values from the injected config dict at startup.

**Considered Options**

- Keep values as Python constants in the modules that use them (e.g., `APPROVAL_KINDS` in `approval_model.py`, `GOVERNANCE_PREFIXES` in `path_policy.py`).
- Declare values in `orchestration.json` alongside the contracts that motivate them, and load them into Python modules via injected config.

**Consequences**

Adding or changing a policy value (new approval kind, new governance path, revised ref cap) is a config edit reviewable as a structured JSON artifact rather than a code change. `orchestration.json` is already the authority for phase contracts, human gates, and graph freshness policy — these values extend that authority consistently. Python modules become pure classification and validation logic with no embedded policy. This pattern does not apply to heuristic vocabulary used for quality checks (see ADR-0005).
