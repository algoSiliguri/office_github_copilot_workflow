import json
import sys
from datetime import datetime
from pathlib import Path


def make_validator(name):
    """Return (fail, require) bound to the given validator name prefix."""
    def fail(message):
        print(f"{name}: FAIL: {message}", file=sys.stderr)
        sys.exit(1)

    def require(condition, message):
        if not condition:
            fail(message)

    return fail, require


def load_json(path, fail):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"missing required file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def require_iso8601(value, field, fail):
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        fail(f"{field} must be ISO 8601")
