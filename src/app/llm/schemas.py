from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: Literal["create_lab", "execute_sql", "inspect_lab", "extend_lab", "reset_lab", "load_learning_state", "save_learning_evidence"]
    arguments: dict[str, Any] = Field(default_factory=dict)


class DiagnosticEvidence(BaseModel):
    concept_key: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)
    answer: str = ""
    correct: bool
    confidence: float = Field(ge=0, le=1)


class TutorResponse(BaseModel):
    phase: Literal["INTENT", "PROBE", "DIAGNOSE", "PLAN", "TEACH", "PRACTICE", "EVALUATE", "ADAPT", "REVIEW", "APPLY", "TRANSFER_TEST"]
    message: str | None = None
    current_concept: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    diagnostic_evidence: list[DiagnosticEvidence] = Field(default_factory=list)
