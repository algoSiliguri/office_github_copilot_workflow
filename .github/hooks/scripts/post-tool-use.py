#!/usr/bin/env python3
"""Summarize postToolUse results without storing raw output."""
import json
import subprocess
import sys

from hooklib import event_record, normalize_payload, read_active_task, read_payload, write_event


def changed_files_from_git(cwd):
    try:
        output = subprocess.check_output(["git", "diff", "--name-only"], cwd=cwd or None, text=True)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        return []


payload = read_payload(sys.stdin)
normalized = normalize_payload(payload, "postToolUse")
task_id = read_active_task(normalized["cwd"])
target_files = normalized["target_files"] or changed_files_from_git(normalized["cwd"])
tool_name = normalized["tool_name"]

event_type = "tool.allowed"
if target_files:
    event_type = "file.edit_attempt"
if normalized["command"]:
    event_type = "command.execution_attempt"
if "check-verification" in normalized["command"]:
    event_type = "verification.command_execution"

event = event_record(
    normalized,
    task_id=task_id,
    event_type=event_type,
    decision="observe",
    reason="post-tool result summarized; raw output omitted",
    risk="low",
    target_files=target_files,
)
event["metadata"] = {
    "hook_event": normalized["hook_event"],
    "mark_graph_stale": bool(target_files),
    "regenerated_graph": False,
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
    "redacted": True,
    "summary": f"tool completed: {tool_name}"[:240] if tool_name else "tool result summarized",
    "modified_files": target_files,
    "mark_graph_stale": bool(target_files),
    "regenerated_graph": False,
    "error": error,
}, sort_keys=True))
