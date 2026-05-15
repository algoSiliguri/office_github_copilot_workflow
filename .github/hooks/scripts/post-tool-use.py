#!/usr/bin/env python3
"""Summarize postToolUse results without storing raw output.

Reads official Copilot hook stdin: {timestamp, cwd, toolName, toolArgs}.
"""
import json
import subprocess
import sys


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


def changed_files_from_git(cwd):
    try:
        output = subprocess.check_output(["git", "diff", "--name-only"], cwd=cwd or None, text=True)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        return []


payload = read_payload()
tool_args = parse_tool_args(payload.get("toolArgs"))
cwd = payload.get("cwd")
tool_name = payload.get("toolName", "")

written_file = tool_args.get("file_path") or tool_args.get("path")
if written_file:
    modified_files = [str(written_file)]
else:
    modified_files = changed_files_from_git(cwd)

graph_should_be_marked_stale = bool(modified_files)
summary = f"tool completed: {tool_name}" if tool_name else "tool result summarized; raw output omitted"

print(json.dumps({
    "ok": True,
    "redacted": True,
    "summary": summary[:240],
    "modified_files": modified_files,
    "mark_graph_stale": graph_should_be_marked_stale,
    "regenerated_graph": False,
}, sort_keys=True))
