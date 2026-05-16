import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

PHASES = {"setup", "plan", "execute", "verify", "review", "evaluate"}
SECRET_KEYS = ("secret", "token", "password", "credential", "api_key", "apikey", "authorization")
SECRET_VALUE_RE = re.compile(r"(token|password|secret|api[_-]?key|authorization)=([^\s]+)", re.IGNORECASE)


def read_payload(stdin):
    if stdin.isatty():
        return {}
    try:
        data = json.load(stdin)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def first(payload, *keys, default=None):
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def normalize_event_name(value):
    mapping = {
        "SessionStart": "sessionStart",
        "UserPromptSubmit": "userPromptSubmitted",
        "UserPromptSubmitted": "userPromptSubmitted",
        "PreToolUse": "preToolUse",
        "PostToolUse": "postToolUse",
        "AgentStop": "agentStop",
        "SessionEnd": "sessionEnd",
    }
    return mapping.get(value, value)


def parse_tool_args(raw):
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"raw": str(raw)}
    except Exception:
        return {"raw": str(raw)}


def normalize_payload(payload, hook_event=None):
    event_name = normalize_event_name(
        hook_event
        or os.environ.get("COPILOT_HOOK_EVENT")
        or first(payload, "hookEventName", "hook_event_name", "eventName", "event_name", default="")
        or "userPromptSubmitted"
    )
    tool_args = parse_tool_args(first(payload, "toolArgs", "tool_args", default={}))
    prompt = first(payload, "prompt", "userPrompt", "user_prompt", default="")
    command = first(tool_args, "command", "cmd", default="")
    file_paths = extract_file_paths(tool_args)
    phase = normalize_phase(first(payload, "phase", default=None) or infer_phase(prompt, command))
    return {
        "raw": payload,
        "hook_event": event_name,
        "timestamp": first(payload, "timestamp", "time", default=None),
        "cwd": first(payload, "cwd", "workspace_dir", "workspaceDir", default=".") or ".",
        "session_id": first(payload, "sessionId", "session_id", default=None),
        "tool_name": first(payload, "toolName", "tool_name", default="") or "",
        "tool_args": tool_args,
        "prompt": prompt,
        "command": command,
        "target_files": file_paths,
        "phase": phase,
    }


def normalize_phase(value):
    if not value:
        return None
    text = str(value).strip().lower().lstrip("/")
    return text if text in PHASES else None


def infer_phase(prompt, command):
    text = f"{prompt or ''} {command or ''}".lower()
    for phase in ("setup", "plan", "execute", "verify", "review", "evaluate"):
        if f"/{phase}" in text:
            return phase
    if "check-verification" in text:
        return "verify"
    if "check-plan" in text:
        return "plan"
    return None


def ts_to_iso(ts):
    if not ts:
        return datetime.now(timezone.utc).isoformat()
    try:
        numeric = float(ts)
        if numeric > 100000000000:
            numeric = numeric / 1000
        return datetime.fromtimestamp(numeric, tz=timezone.utc).isoformat()
    except Exception:
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()


def read_active_task(cwd):
    state_path = Path(cwd or ".") / ".github" / "workflow" / "state.json"
    try:
        with state_path.open(encoding="utf-8") as fh:
            return json.load(fh).get("active_task")
    except Exception:
        return None


def log_path_for(cwd, task_id):
    if task_id:
        return Path(cwd) / ".github" / "tasks" / task_id / "logs" / "events.jsonl"
    return Path(cwd) / ".github" / "tasks" / "_orphans" / "logs" / "events.jsonl"


def write_event(cwd, event):
    log_path = log_path_for(cwd, event.get("task_id"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    return str(log_path)


def risk_level(categories):
    high = {"destructive_shell", "secret_or_credential_access", "workflow_governance_edits", "git_push"}
    medium = {"network_commands", "dependency_installation", "graph_regeneration", "phase_sensitive_without_task"}
    if any(category in high for category in categories):
        return "high"
    if any(category in medium for category in categories):
        return "medium"
    return "low"


def extract_file_paths(tool_args):
    paths = []
    for key in ("file_path", "path", "target_file"):
        val = tool_args.get(key)
        if val:
            paths.append(str(val))
    for key in ("file_paths", "paths", "target_files"):
        val = tool_args.get(key)
        if isinstance(val, list):
            paths.extend(str(item) for item in val if item)
    return sorted(set(paths))


def redact_value(value):
    if value is None:
        return ""
    text = str(value)
    text = SECRET_VALUE_RE.sub(lambda match: f"{match.group(1)}=<redacted>", text)
    return text[:240]


def redact_dict(data):
    redacted = {}
    for key, value in (data or {}).items():
        key_text = str(key)
        if any(secret in key_text.lower() for secret in SECRET_KEYS):
            redacted[key_text] = "<redacted>"
        elif isinstance(value, (dict, list)):
            redacted[key_text] = "<redacted-complex>"
        else:
            redacted[key_text] = redact_value(value)
    return redacted


def event_record(normalized, *, task_id, event_type, decision="observe", reason="", risk="low", target_files=None):
    return {
        "schema_version": "event.schema.v1",
        "event_id": str(uuid.uuid4()),
        "task_id": task_id,
        "phase": normalized.get("phase"),
        "timestamp": ts_to_iso(normalized.get("timestamp")),
        "event_type": event_type,
        "tool_name": normalized.get("tool_name") or "",
        "target_files": target_files if target_files is not None else normalized.get("target_files", []),
        "decision": decision,
        "reason": redact_value(reason),
        "risk": risk,
        "redacted": True,
        "session_id": normalized.get("session_id"),
    }
