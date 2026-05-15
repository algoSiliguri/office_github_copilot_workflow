#!/usr/bin/env python3
"""Write a redacted v1 event summary to the active task log.

Reads official Copilot hook stdin: {timestamp, cwd, toolName, toolArgs}.
COPILOT_HOOK_EVENT env var carries the hook event name set by workflow-hooks.json.
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

HOOK_EVENT_TO_CATEGORY = {
    "sessionStart": "session.started",
    "sessionEnd": "session.ended",
    "userPromptSubmitted": "command.invoked",
    "preToolUse": "tool.requested",
    "postToolUse": "tool.approved",
    "agentStop": "session.ended",
    "errorOccurred": "error.occurred",
}


def read_payload():
    if sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def parse_tool_args(raw):
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
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
hook_event = os.environ.get("COPILOT_HOOK_EVENT", "userPromptSubmitted")
tool_args = parse_tool_args(payload.get("toolArgs"))
cwd = payload.get("cwd", ".")
task_id = read_active_task(cwd)
tool_name = payload.get("toolName", "")
category = HOOK_EVENT_TO_CATEGORY.get(hook_event, "command.invoked")

summary = f"{hook_event}: {tool_name}" if tool_name else hook_event

file_refs = [str(tool_args["file_path"])] if tool_args.get("file_path") else []
cmd_refs = [tool_args["command"]] if tool_args.get("command") else []

event = {
    "schema_version": "event.schema.v1",
    "event_id": str(uuid.uuid4()),
    "timestamp": ts_to_iso(payload.get("timestamp")),
    "task_id": task_id,
    "session_id": None,
    "category": category,
    "phase": None,
    "source": "hook",
    "summary": summary[:240],
    "refs": {
        "artifact_paths": [],
        "file_paths": file_refs,
        "graph_refs": [],
        "command_refs": cmd_refs,
    },
    "sensitivity": "internal",
    "redaction": {
        "applied": True,
        "reason": "raw prompt/response/tool content omitted",
    },
}

written_path = None
if task_id:
    log_path = Path(cwd) / ".github" / "tasks" / task_id / "logs" / "events.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    written_path = str(log_path)

print(json.dumps({"ok": True, "event_id": event["event_id"], "written_path": written_path}, sort_keys=True))
