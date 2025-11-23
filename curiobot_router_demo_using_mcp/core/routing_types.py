from typing import Any, Dict, Literal
from pydantic import BaseModel, Field

ToolName = Literal["get_news", "get_weather", "get_wiki", "direct_answer", "none"]


class RouterPlan(BaseModel):
    """LLM router's decision about which tool to call."""

    tool: ToolName = Field(
        description="Chosen tool or 'direct_answer'/'none'."
    )
    args: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the chosen tool.",
    )
    reason: str = Field(
        default="",
        description="Short explanation of why this tool was chosen.",
    )
