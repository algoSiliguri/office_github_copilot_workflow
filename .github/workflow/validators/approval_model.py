from validator_core import require_iso8601


def validate_approval(record, expected_kind, field, fail, kinds=None):
    if not isinstance(record, dict):
        fail(f"{field} must be an approval object")
    for key in [
        "approval_id",
        "kind",
        "requested_by",
        "approved_by",
        "approved_at",
        "decision",
        "reason",
        "expires_at",
    ]:
        if key not in record:
            fail(f"{field} missing required field: {key}")
    if not isinstance(record["approval_id"], str) or not record["approval_id"].startswith("APP-"):
        fail(f"{field}.approval_id must start with APP-")
    if kinds is not None and record["kind"] not in kinds:
        fail(f"{field}.kind is invalid")
    if expected_kind and record["kind"] != expected_kind:
        fail(f"{field}.kind must be {expected_kind}")
    if not isinstance(record["requested_by"], str) or not record["requested_by"].strip():
        fail(f"{field}.requested_by is required")
    if not isinstance(record["approved_by"], str) or not record["approved_by"].strip():
        fail(f"{field}.approved_by is required")
    require_iso8601(record["approved_at"], f"{field}.approved_at", fail)
    if record["decision"] not in {"approved", "rejected"}:
        fail(f"{field}.decision must be approved or rejected")
    if not isinstance(record["reason"], str) or len(record["reason"].strip()) < 10:
        fail(f"{field}.reason must be at least 10 characters")
    if record["expires_at"] is not None:
        require_iso8601(record["expires_at"], f"{field}.expires_at", fail)


def approval_is_approved(record, expected_kind, field, fail, kinds=None):
    validate_approval(record, expected_kind, field, fail, kinds=kinds)
    return record["decision"] == "approved"


def require_approved(record, expected_kind, field, fail, kinds=None):
    validate_approval(record, expected_kind, field, fail, kinds=kinds)
    if record["decision"] != "approved":
        fail(f"{field} must be approved")


def approvals_of_kind(records, kind):
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict) and record.get("kind") == kind]


def require_approved_kind(records, kind, field, fail, kinds=None):
    matches = approvals_of_kind(records, kind)
    if not matches:
        fail(f"{field} requires an approval of kind {kind}")
    for index, record in enumerate(matches):
        if record.get("decision") == "approved":
            validate_approval(record, kind, f"{field}[{index}]", fail, kinds=kinds)
            return record
    fail(f"{field} requires an approved approval of kind {kind}")
