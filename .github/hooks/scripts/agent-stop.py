#!/usr/bin/env python3
"""Emit a redacted session-end event at agentStop.

Reads official Copilot hook stdin: {timestamp, cwd}.
Scans for the active task and appends a session.ended log event.
"""
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def read_payload():
    if sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def read_active_task(cwd):
    """Read active_task from explicit workflow state file."""
    state_path = Path(cwd or ".") / ".github" / "workflow" / "state.json"
    try:
        with state_path.open(encoding="utf-8") as fh:
            return json.load(fh).get("active_task")
    except Exception:
        return None


def ts_to_iso(ts):
    if not ts:
        return datetime.now(timezone.utc).isoformat()
    try:
        return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


payload = read_payload()
cwd = payload.get("cwd", ".")
task_id = read_active_task(cwd)

event = {
    "schema_version": "event.schema.v1",
    "event_id": str(uuid.uuid4()),
    "timestamp": ts_to_iso(payload.get("timestamp")),
    "task_id": task_id,
    "session_id": None,
    "category": "session.ended",
    "phase": None,
    "source": "hook",
    "summary": "agent stopped; next human decision required",
    "refs": {"artifact_paths": [], "file_paths": [], "graph_refs": [], "command_refs": []},
    "sensitivity": "internal",
    "redaction": {"applied": True, "reason": "raw session content omitted"},
}

written_path = None
if task_id:
    log_path = Path(cwd) / ".github" / "tasks" / task_id / "logs" / "events.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    written_path = str(log_path)

print(json.dumps({
    "ok": True,
    "event_id": event["event_id"],
    "written_path": written_path,
    "requires_next_human_decision": True,
}, sort_keys=True))
