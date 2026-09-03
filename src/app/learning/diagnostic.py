"""Stateful diagnostic flow; pedagogical question generation remains with the LLM."""

from typing import Any
from uuid import UUID, uuid4

from app.persistence.models import LearningSession
from app.persistence.repositories import LearningRepository
from .probe import AdaptiveProbe, ProbeEvidence


class DiagnosticService:
    def __init__(self, repository: LearningRepository) -> None:
        self.repository = repository
        self.probe = AdaptiveProbe()

    def start(self, topic: str, goal: str | None = None) -> LearningSession:
        if not topic.strip():
            raise ValueError("O tópico de aprendizagem não pode ser vazio")
        session = self.repository.create_session(uuid4(), topic.strip(), goal)
        self.repository.add_event(session.session_id, "PROBE_STARTED", {"topic": session.topic})
        return self.repository.update_phase(session.session_id, "PROBE")

    def record_probe(self, session_id: UUID, concept_key: str, concept_name: str, *, correct: bool, reasoning_quality: float | None = None, answer: Any = None, misconception: str | None = None) -> dict:
        concept = self.repository.upsert_concept(session_id, concept_key, concept_name, misconception=misconception)
        evidence = self.repository.add_evidence(session_id, "probe_answer", concept.concept_id, difficulty="diagnostic", correctness=1.0 if correct else 0.0, reasoning_quality=reasoning_quality, raw_evidence={"answer": answer} if answer is not None else None)
        # One answer only yields partial/insufficient evidence; repeated evidence
        # and the mastery engine will refine this value in a later phase.
        mastery = 0.9 if correct and (reasoning_quality or 0.0) >= 0.8 else 0.6 if correct else 0.2
        confidence = "high" if mastery >= 0.8 else "medium" if correct else "low"
        concept = self.repository.upsert_concept(session_id, concept_key, concept_name, mastery=mastery, confidence=confidence, misconception=misconception)
        self.repository.add_event(session_id, "PROBE_EVIDENCE_RECORDED", {"concept_key": concept_key, "correct": correct})
        return {"concept": concept.model_dump(mode="json"), "evidence": evidence.model_dump(mode="json")}

    def create_baseline(self, session_id: UUID) -> dict:
        concepts = self.repository.concepts(session_id)
        baseline = []
        for concept in concepts:
            if concept.mastery >= 0.8:
                level = "mastered"
            elif concept.mastery >= 0.5:
                level = "partial"
            elif concept.mastery > 0:
                level = "insufficient"
            else:
                level = "unknown"
            baseline.append({"concept_key": concept.concept_key, "level": level})
        self.repository.update_phase(session_id, "DIAGNOSE")
        self.repository.add_event(session_id, "BASELINE_CREATED", {"concepts": baseline})
        return {"session_id": str(session_id), "concepts": baseline}

    def probe_is_sufficient(self, session_id: UUID) -> bool:
        evidence = self.repository.recent_evidence(session_id, limit=100)
        probes = [ProbeEvidence(concept_key=str(item.concept_id or "unknown"), answer="", correct=(item.correctness or 0) >= .5, confidence=item.correctness or 0) for item in evidence if item.evidence_type == "probe_answer"]
        return self.probe.sufficient(probes)
