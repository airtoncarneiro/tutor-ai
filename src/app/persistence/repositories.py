"""Repositories for the tutor schema."""

from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb

from .database import Database
from .models import LearningConcept, LearningEvidence, LearningEvent, LearningSession


class LearningRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_session(self, session_id: UUID, topic: str, goal: str | None = None) -> LearningSession:
        with self.database.connection() as conn:
            row = conn.execute("""INSERT INTO tutor.learning_session (session_id, topic, goal)
                VALUES (%s, %s, %s) RETURNING *""", (session_id, topic, goal)).fetchone()
        return LearningSession.model_validate(dict(zip(["session_id", "topic", "goal", "phase", "status", "scenario", "created_at", "updated_at"], row)))

    def get_session(self, session_id: UUID) -> LearningSession | None:
        with self.database.connection() as conn:
            row = conn.execute("SELECT * FROM tutor.learning_session WHERE session_id = %s", (session_id,)).fetchone()
        if row is None:
            return None
        return LearningSession.model_validate(dict(zip(["session_id", "topic", "goal", "phase", "status", "scenario", "created_at", "updated_at"], row)))

    def update_phase(self, session_id: UUID, phase: str, status: str | None = None) -> LearningSession:
        with self.database.connection() as conn:
            row = conn.execute("""UPDATE tutor.learning_session SET phase=%s, status=COALESCE(%s, status), updated_at=now()
                WHERE session_id=%s RETURNING *""", (phase, status, session_id)).fetchone()
        if row is None:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        return LearningSession.model_validate(dict(zip(["session_id", "topic", "goal", "phase", "status", "scenario", "created_at", "updated_at"], row)))

    def upsert_concept(self, session_id: UUID, concept_key: str, name: str, mastery: float = 0.0, confidence: str = "low", misconception: str | None = None) -> LearningConcept:
        with self.database.connection() as conn:
            row = conn.execute("""INSERT INTO tutor.learning_concept (session_id, concept_key, name, mastery, confidence, misconception)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, concept_key) DO UPDATE SET name=EXCLUDED.name, mastery=EXCLUDED.mastery,
                confidence=EXCLUDED.confidence, misconception=EXCLUDED.misconception, updated_at=now()
                RETURNING *""", (session_id, concept_key, name, mastery, confidence, misconception)).fetchone()
        return LearningConcept.model_validate(dict(zip(["concept_id", "session_id", "concept_key", "name", "mastery", "confidence", "misconception", "created_at", "updated_at"], row)))

    def add_evidence(self, session_id: UUID, evidence_type: str, concept_id: int | None = None, **fields: Any) -> LearningEvidence:
        columns = ["session_id", "concept_id", "evidence_type"] + list(fields)
        values = [session_id, concept_id, evidence_type] + [
            Jsonb(value) if key == "raw_evidence" else value
            for key, value in fields.items()
        ]
        placeholders = ", ".join(["%s"] * len(values))
        with self.database.connection() as conn:
            row = conn.execute(f"INSERT INTO tutor.learning_evidence ({', '.join(columns)}) VALUES ({placeholders}) RETURNING *", values).fetchone()
        names = ["evidence_id", "session_id", "concept_id", "evidence_type", "difficulty", "correctness", "reasoning_quality", "attempts", "assistance", "raw_evidence", "created_at"]
        return LearningEvidence.model_validate(dict(zip(names, row)))

    def add_event(self, session_id: UUID, event_type: str, payload: dict[str, Any] | None = None) -> LearningEvent:
        with self.database.connection() as conn:
            row = conn.execute("INSERT INTO tutor.learning_event (session_id, event_type, payload) VALUES (%s, %s, %s) RETURNING *", (session_id, event_type, Jsonb(payload or {}))).fetchone()
        return LearningEvent.model_validate(dict(zip(["event_id", "session_id", "event_type", "payload", "created_at"], row)))

    def recent_evidence(self, session_id: UUID, limit: int = 10) -> list[LearningEvidence]:
        with self.database.connection() as conn:
            rows = conn.execute("SELECT * FROM tutor.learning_evidence WHERE session_id = %s ORDER BY created_at DESC LIMIT %s", (session_id, limit)).fetchall()
        names = ["evidence_id", "session_id", "concept_id", "evidence_type", "difficulty", "correctness", "reasoning_quality", "attempts", "assistance", "raw_evidence", "created_at"]
        return [LearningEvidence.model_validate(dict(zip(names, row))) for row in rows]

    def concepts(self, session_id: UUID) -> list[LearningConcept]:
        with self.database.connection() as conn:
            rows = conn.execute("SELECT * FROM tutor.learning_concept WHERE session_id = %s ORDER BY concept_key", (session_id,)).fetchall()
        names = ["concept_id", "session_id", "concept_key", "name", "mastery", "confidence", "misconception", "created_at", "updated_at"]
        return [LearningConcept.model_validate(dict(zip(names, row))) for row in rows]
