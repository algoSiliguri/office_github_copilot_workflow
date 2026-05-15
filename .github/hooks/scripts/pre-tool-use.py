#!/usr/bin/env python3
"""Placeholder preToolUse guard for Enhanced Local Mode."""
import json
import sys

payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
summary = str(payload.get("summary") or payload.get("command") or "")
blocked_terms = ["rm -rf", "git push", "curl ", "wget ", "pip install", "npm install"]
decision = "deny" if any(term in summary for term in blocked_terms) else "allow"
print(json.dumps({"decision": decision, "redacted": True}))
