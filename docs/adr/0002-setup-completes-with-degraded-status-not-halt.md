# Setup Completes with Degraded Status When graphify-out Is Missing

When `/setup` detects that `graphify-out/` is absent or incomplete, it writes `graph_status: missing` into `graph-record.json` and completes setup rather than halting. The degraded-mode approval gate belongs at `/plan`, not at `/setup`, because setup also installs bundle layout, hooks, and the AGENTS block — none of which depend on graph freshness. Halting setup on a missing graph would block all other setup work for a condition that only matters at planning time.

**Considered Options**

- Halt `/setup` entirely when graphify-out is missing; require the user to run `graphify` and retry.
- Complete `/setup` with `graph_status: missing`, warn the user, and defer the approval gate to `/plan`.

**Consequences**

`/plan` is the enforcement point for graph freshness. Normal planning requires `graph_freshness_mode: fresh`. If `graph_status` is `missing`, `/plan` must record `graph_freshness_mode: degraded-approved` and carry a `graph-degraded` approval before producing an execution-ready plan. `check-plan` enforces this. `/setup` is responsible only for detecting and recording state honestly.
