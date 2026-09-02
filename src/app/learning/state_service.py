from uuid import UUID

from app.persistence.models import LearningSession
from app.persistence.repositories import LearningRepository


class LearningStateService:
    def __init__(self, repository: LearningRepository) -> None:
        self.repository = repository

    def load(self, session_id: UUID) -> dict:
        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        return {
            "session": session.model_dump(mode="json"),
            "topic": session.topic,
            "goal": session.goal,
            "phase": session.phase,
            "scenario": session.scenario,
            "concepts": [concept.model_dump(mode="json") for concept in self.repository.concepts(session_id)],
            "recent_evidence": [evidence.model_dump(mode="json") for evidence in self.repository.recent_evidence(session_id)],
        }

