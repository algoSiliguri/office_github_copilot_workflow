#!/usr/bin/env python3
"""Placeholder agentStop finalizer for Enhanced Local Mode."""
import json
import sys

payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
print(json.dumps({"ok": True, "redacted": True, "requires_next_human_decision": True, "received_keys": sorted(payload.keys())}))
