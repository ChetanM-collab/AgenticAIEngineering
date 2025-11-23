from typing import Any, Dict


def make_direct_answer(
    summary: str,
    reason: str,
    ok: bool = True,
    extra_args: Dict[str, Any] | None = None,
    extra_raw: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Helper to construct a 'direct_answer' style payload.

    This matches the QueryResult shape and keeps error/edge cases consistent.
    """
    return {
        "tool": "direct_answer",
        "args": {"reason": reason, **(extra_args or {})},
        "summary": summary,
        "raw_tool_output": {"ok": ok, **(extra_raw or {})},
    }
