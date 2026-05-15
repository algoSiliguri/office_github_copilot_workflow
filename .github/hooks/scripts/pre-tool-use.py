#!/usr/bin/env python3
"""Enhanced Local preToolUse guard.

The guard is intentionally conservative. It returns JSON for Copilot hook
integration or direct fixture tests; it does not mutate workflow state.
"""
import json
import sys

RISK_PATTERNS = {
    "destructive_shell": ["rm -rf", "git reset --hard", "git clean -fd", "mkfs", "chmod -R 777"],
    "network_commands": ["curl ", "wget ", "ssh ", "scp ", "rsync ", "gh api", "git clone"],
    "dependency_installation": ["pip install", "npm install", "yarn add", "pnpm add", "brew install", "uv tool install"],
    "graph_regeneration": ["graphify update", "graphify .", "graphify --"],
    "git_push": ["git push"],
    "secret_or_credential_access": [".env", "id_rsa", "secrets", "credential", "token"],
}
GOVERNANCE_PREFIXES = (
    ".github/copilot-instructions.md",
    ".github/instructions/",
    ".github/skills/",
    ".github/agents/",
    ".github/hooks/",
    ".github/workflow/",
    "AGENTS.md",
)


def read_payload():
    if sys.stdin.isatty():
        return {}
    return json.load(sys.stdin)


def text(payload):
    parts = [
        payload.get("summary"),
        payload.get("command"),
        payload.get("tool_name"),
        " ".join(payload.get("file_paths", []) if isinstance(payload.get("file_paths"), list) else []),
    ]
    return " ".join(str(part or "") for part in parts).lower()


def planned_files(payload):
    return set(str(path) for path in payload.get("approved_files", []) if path)


def requested_files(payload):
    return set(str(path) for path in payload.get("file_paths", []) if path)


payload = read_payload()
haystack = text(payload)
approval = payload.get("human_approval") or {}
approved = approval.get("approved") is True
categories = []

for category, patterns in RISK_PATTERNS.items():
    if any(pattern in haystack for pattern in patterns):
        categories.append(category)

for path in requested_files(payload):
    if path.startswith(GOVERNANCE_PREFIXES):
        categories.append("workflow_governance_edits")

planned = planned_files(payload)
requested = requested_files(payload)
if planned and requested - planned and payload.get("operation") in {"write", "edit", "delete"}:
    categories.append("unplanned_file_edit")

categories = sorted(set(categories))
decision = "allow"
reason = "no risky category detected"
if categories and not approved:
    decision = "deny"
    reason = "human approval required"
elif categories and approved:
    decision = "allow"
    reason = "explicit human approval recorded"

print(json.dumps({
    "decision": decision,
    "risk_categories": categories,
    "reason": reason,
    "redacted": True
}, sort_keys=True))
