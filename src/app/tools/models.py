from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.lab.models import LabDefinition, LabSummary, SqlResult


class CreateLabInput(LabDefinition):
    pass


class ExecuteSqlInput(BaseModel):
    sql: str = Field(min_length=1)


class InspectLabInput(BaseModel):
    pass


class ExtendLabInput(BaseModel):
    ddl: list[str] = Field(default_factory=list)
    dml: list[str] = Field(default_factory=list)


class ResetLabInput(BaseModel):
    pass


class LoadLearningStateInput(BaseModel):
    session_id: UUID


class SaveLearningEvidenceInput(BaseModel):
    session_id: UUID
    concept_id: int | None = None
    evidence_type: str = Field(min_length=1)
    difficulty: str | None = None
    correctness: float | None = Field(default=None, ge=0, le=1)
    reasoning_quality: float | None = Field(default=None, ge=0, le=1)
    attempts: int = Field(default=1, ge=1)
    assistance: str | None = None
    raw_evidence: dict[str, Any] | None = None


class ToolError(BaseModel):
    error: str


ToolName = Literal[
    "create_lab", "execute_sql", "inspect_lab", "extend_lab", "reset_lab",
    "load_learning_state", "save_learning_evidence",
]

