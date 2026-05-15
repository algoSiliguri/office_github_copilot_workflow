#!/usr/bin/env python3
"""Write a redacted v1 event summary for Enhanced Local Mode.

Input is a Copilot hook-like JSON object. Raw prompts, responses, tool
transcripts, and full shell output are intentionally ignored.
"""
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_CATEGORIES = {
    "session.started",
    "session.ended",
    "command.invoked",
    "skill.selected",
    "graph.context_used",
    "plan.step_started",
    "plan.step_completed",
    "tool.requested",
    "tool.approved",
    "tool.denied",
    "shell.command_run",
    "file.modified",
    "verification.command_run",
    "verification.result",
    "human.approval_requested",
    "human.approval_recorded",
    "assumption.recorded",
    "deviation.recorded",
    "review.finding",
    "evaluation.finding",
    "error.occurred",
}
PHASES = {"setup", "plan", "execute", "verify", "evaluate"}
SOURCES = {"hook", "command", "validator", "human"}
SENSITIVITY = {"public", "internal", "sensitive"}


def read_payload():
    if sys.stdin.isatty():
        return {}
    return json.load(sys.stdin)


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def compact_summary(payload):
    summary = payload.get("summary") or payload.get("redacted_summary") or payload.get("event") or "redacted event"
    summary = " ".join(str(summary).split())
    return summary[:240]


def event_from_payload(payload):
    refs = payload.get("refs") if isinstance(payload.get("refs"), dict) else {}
    category = payload.get("category", "command.invoked")
    phase = payload.get("phase", "plan")
    source = payload.get("source", "hook")
    sensitivity = payload.get("sensitivity", "internal")
    return {
        "schema_version": "event.schema.v1",
        "event_id": str(payload.get("event_id") or uuid.uuid4()),
        "timestamp": str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        "task_id": payload.get("task_id"),
        "session_id": payload.get("session_id"),
        "category": category if category in ALLOWED_CATEGORIES else "command.invoked",
        "phase": phase if phase in PHASES else "plan",
        "source": source if source in SOURCES else "hook",
        "summary": compact_summary(payload),
        "refs": {
            "artifact_paths": as_list(refs.get("artifact_paths")),
            "file_paths": as_list(refs.get("file_paths")),
            "graph_refs": as_list(refs.get("graph_refs")),
            "command_refs": as_list(refs.get("command_refs")),
        },
        "sensitivity": sensitivity if sensitivity in SENSITIVITY else "internal",
        "redaction": {
            "applied": True,
            "reason": str(payload.get("redaction_reason") or "raw prompt/response/tool content omitted"),
        },
    }


def append_event(event):
    task_id = event.get("task_id")
    if not task_id:
        return None
    log_path = Path(".github/tasks") / task_id / "logs" / "events.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return str(log_path)


payload = read_payload()
event = event_from_payload(payload)
written_path = append_event(event) if payload.get("write_log", True) else None
print(json.dumps({"ok": True, "event": event, "written_path": written_path}, sort_keys=True))
