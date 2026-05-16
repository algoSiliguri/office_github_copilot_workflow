#!/usr/bin/env python3
"""Emit a redacted session end event at agentStop."""
import json
import sys

from hooklib import event_record, normalize_payload, read_active_task, read_payload, write_event


payload = read_payload(sys.stdin)
normalized = normalize_payload(payload, "agentStop")
task_id = read_active_task(normalized["cwd"])

event = event_record(
    normalized,
    task_id=task_id,
    event_type="session.ended",
    decision="observe",
    reason="agent stopped; raw session content omitted",
    risk="low",
)
event["metadata"] = {"requires_next_human_decision": True}

written_path = None
ok = True
error = None
try:
    written_path = write_event(normalized["cwd"], event)
except Exception as exc:
    ok = False
    error = str(exc)[:240]

print(json.dumps({
    "ok": ok,
    "event_id": event["event_id"],
    "written_path": written_path,
    "orphan": task_id is None,
    "requires_next_human_decision": True,
    "error": error,
}, sort_keys=True))
