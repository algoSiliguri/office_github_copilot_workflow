# Graph Freshness Is Derived from Git Commit Comparison in check-graph, Not Written by Hook

`graph-record.json:graph_status` can say `fresh` after source files have been modified during a session. `post-tool-use.py` detects file changes and emits an advisory `mark_graph_stale` flag in its output, but does not update `graph-record.json`. A subsequent `/plan` sees an honest-looking fresh record that no longer reflects reality.

**Considered Options**

- Hook write: `post-tool-use.py` writes `graph_status: stale` to `graph-record.json` when source files change during a session.
- Git-derived check: `check-graph` compares `graph-record.json:git_commit` to `git rev-parse HEAD`. A mismatch fails with a staleness error. `/setup` remains the sole writer of `graph-record.json`.

**Consequences**

`/setup` remains the sole writer of `graph-record.json`, consistent with `graph-context/SKILL.md`. No dual-writer problem. The git-derived check works in Safe Default Mode because it runs in a stdlib Python validator with no hook dependency. Freshness enforcement is deterministic and auditable: `check-graph` either passes or fails with a clear message. When git is unavailable — shallow clones, containers without git — `check-graph` soft-skips the commit comparison, warns to stderr, and passes; the check degrades gracefully rather than blocking gitless environments. `check-plan` continues to trust `graph_freshness_mode` as declared in the plan artifact; `check-graph` is the authority on whether that declaration is honest. The `mark_graph_stale` advisory flag remains in `post-tool-use` output and `events.jsonl` metadata as a signal for future evaluation tooling but carries no enforcement weight.
