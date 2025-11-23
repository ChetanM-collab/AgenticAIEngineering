from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from typing import Literal

class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural-language question from the user.")


class QueryResult(BaseModel):
    tool: Literal["get_news", "get_weather", "get_wiki", "direct_answer", "none"] = Field(
        description="The tool ultimately used, 'direct_answer' for LLM-only answers, or 'none'."
    )
    args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the chosen tool (or context for direct_answer).",
    )
    summary: str = Field(
        description="User-facing summary / answer.",
    )
    raw_tool_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional compact subset of the tool's JSON output.",
    )
