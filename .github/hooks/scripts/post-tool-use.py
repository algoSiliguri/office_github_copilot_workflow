#!/usr/bin/env python3
"""Summarize postToolUse results without storing raw transcripts."""
import json
import subprocess
import sys


def read_payload():
    if sys.stdin.isatty():
        return {}
    return json.load(sys.stdin)


def changed_files_from_git():
    try:
        output = subprocess.check_output(["git", "diff", "--name-only"], text=True)
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


payload = read_payload()
modified_files = payload.get("modified_files")
if not isinstance(modified_files, list):
    modified_files = changed_files_from_git()

graph_should_be_marked_stale = bool(modified_files)
summary = payload.get("summary") or "tool result summarized; raw output omitted"
summary = " ".join(str(summary).split())[:240]

print(json.dumps({
    "ok": True,
    "redacted": True,
    "summary": summary,
    "modified_files": modified_files,
    "mark_graph_stale": graph_should_be_marked_stale,
    "regenerated_graph": False
}, sort_keys=True))
