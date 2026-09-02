"""Application models returned by persistence services."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LearningSession(BaseModel):
    session_id: UUID
    topic: str
    goal: str | None = None
    phase: str
    status: str
    scenario: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class LearningConcept(BaseModel):
    concept_id: int
    session_id: UUID
    concept_key: str
    name: str
    mastery: float
    confidence: Literal["low", "medium", "high"]
    misconception: str | None = None


class LearningEvidence(BaseModel):
    evidence_id: int
    session_id: UUID
    concept_id: int | None
    evidence_type: str
    difficulty: str | None = None
    correctness: float | None = None
    reasoning_quality: float | None = None
    attempts: int = Field(gt=0)
    assistance: str | None = None
    raw_evidence: dict[str, Any] | None = None
    created_at: datetime


class LearningEvent(BaseModel):
    event_id: int
    session_id: UUID
    event_type: str
    payload: dict[str, Any]
    created_at: datetime

