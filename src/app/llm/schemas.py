from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: Literal["create_lab", "execute_sql", "inspect_lab", "extend_lab", "reset_lab", "load_learning_state", "save_learning_evidence"]
    arguments: dict[str, Any] = Field(default_factory=dict)


class TutorResponse(BaseModel):
    phase: Literal["INTENT", "PROBE", "DIAGNOSE", "PLAN", "TEACH", "PRACTICE", "EVALUATE", "ADAPT", "REVIEW", "APPLY", "TRANSFER_TEST"]
    message: str | None = None
    current_concept: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)

