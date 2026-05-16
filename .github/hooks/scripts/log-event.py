#!/usr/bin/env python3
"""Write redacted high-value hook events to the active task or orphan log."""
import json
import os
import sys

from hooklib import event_record, normalize_payload, read_active_task, read_payload, redact_dict, write_event

HOOK_EVENT_TYPES = {
    "sessionStart": "session.started",
    "userPromptSubmitted": "prompt.submitted",
    "sessionEnd": "session.ended",
}


payload = read_payload(sys.stdin)
normalized = normalize_payload(payload, os.environ.get("COPILOT_HOOK_EVENT"))
task_id = read_active_task(normalized["cwd"])
event_type = HOOK_EVENT_TYPES.get(normalized["hook_event"], "prompt.submitted")

event = event_record(
    normalized,
    task_id=task_id,
    event_type=event_type,
    decision="observe",
    reason="hook event captured; raw payload omitted",
    risk="low",
)
event["metadata"] = {
    "hook_event": normalized["hook_event"],
    "payload": redact_dict({
        "prompt": normalized.get("prompt"),
        "toolName": normalized.get("tool_name"),
    }),
}

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
    "error": error,
}, sort_keys=True))
