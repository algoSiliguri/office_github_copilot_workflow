#!/usr/bin/env python3
"""Finalize a task state summary at agentStop without hidden workflow logic."""
import json
import sys

REQUIRED_STATUS_KEYS = [
    "task_id",
    "phase",
    "artifact_status",
    "verification_status",
    "unresolved_assumptions",
    "unresolved_deviations",
    "next_human_decision",
]


def read_payload():
    if sys.stdin.isatty():
        return {}
    return json.load(sys.stdin)


payload = read_payload()
missing = [key for key in REQUIRED_STATUS_KEYS if key not in payload]
ok = not missing
print(json.dumps({
    "ok": ok,
    "redacted": True,
    "missing": missing,
    "requires_next_human_decision": True,
    "next_human_decision": payload.get("next_human_decision")
}, sort_keys=True))
