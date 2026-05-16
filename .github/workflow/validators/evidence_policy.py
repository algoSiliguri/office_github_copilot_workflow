_GRAPH_TERMS = ("graphify", "graph refs", "graph_refs", "graph reference", "graph context", "graph data", "architecture graph")
_PROOF_TERMS = ("correct", "passed", "valid", "verified", "proves", "proof", "test result", "no issues", "architecture is correct")
_COMMAND_TERMS = ("command", "exit", "exited", "test", "check", "validator", "release-check", "pytest", "bash", "python")


def uses_graph_as_proof(summary: str) -> bool:
    """Return True if the summary uses graph data as correctness evidence.

    Graph may appear as context without being proof; the distinction is whether
    proof language appears without any reference to a real command or check.
    """
    normalized = " ".join(str(summary).lower().split())
    if not any(term in normalized for term in _GRAPH_TERMS):
        return False
    mentions_proof = any(term in normalized for term in _PROOF_TERMS)
    mentions_command = any(term in normalized for term in _COMMAND_TERMS)
    return mentions_proof and not mentions_command
