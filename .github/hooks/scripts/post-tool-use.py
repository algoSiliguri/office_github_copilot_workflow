#!/usr/bin/env python3
"""Placeholder postToolUse summarizer for Enhanced Local Mode."""
import json
import sys

payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
print(json.dumps({"ok": True, "redacted": True, "summary": "postToolUse summary omitted", "received_keys": sorted(payload.keys())}))
