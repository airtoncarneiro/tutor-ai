from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.persistence.repositories import LearningRepository


class EvaluationEvidence(BaseModel):
    concept_key: str
    syntax: bool
    execution: bool
    semantics: float = Field(ge=0, le=1)
    requirement_satisfaction: float = Field(ge=0, le=1)
    reasoning: float = Field(ge=0, le=1)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    independent: bool = True

    @property
    def correctness(self) -> float:
        return round((0.10 * self.syntax + 0.20 * self.execution + 0.30 * self.semantics + 0.25 * self.requirement_satisfaction + 0.15 * self.reasoning), 3)


class MasteryEngine:
    """V1 formula: new = previous*0.7 + evidence_score*0.3.

    Independence raises confidence; assisted or incorrect evidence lowers it.
    The conservative weight prevents a single answer from establishing mastery.
    """

    def update(self, previous: float, evidence: EvaluationEvidence, evidence_count: int) -> tuple[float, str]:
        score = evidence.correctness * (1.0 if evidence.independent else 0.8)
        mastery = max(0.0, min(1.0, previous * 0.7 + score * 0.3))
        confidence = "high" if evidence_count >= 3 and score >= 0.8 else "medium" if evidence_count >= 1 and score >= 0.5 else "low"
        return round(mastery, 3), confidence


class EvaluationService:
    def __init__(self, repository: LearningRepository, engine: MasteryEngine | None = None) -> None:
        self.repository = repository
        self.engine = engine or MasteryEngine()

    def evaluate(self, session_id: UUID, evidence: EvaluationEvidence) -> dict:
        concepts = {c.concept_key: c for c in self.repository.concepts(session_id)}
        concept = concepts.get(evidence.concept_key)
        if concept is None:
            raise ValueError(f"Conceito não encontrado: {evidence.concept_key}")
        prior_evidence = self.repository.recent_evidence(session_id, limit=1000)
        count = sum(1 for item in prior_evidence if item.concept_id == concept.concept_id) + 1
        mastery, confidence = self.engine.update(concept.mastery, evidence, count)
        updated = self.repository.upsert_concept(session_id, concept.concept_key, concept.name, mastery, confidence)
        saved = self.repository.add_evidence(session_id, "evaluation", concept.concept_id, difficulty=evidence.difficulty, correctness=evidence.correctness, reasoning_quality=evidence.reasoning, assistance="independent" if evidence.independent else "assisted", raw_evidence=evidence.model_dump())
        self.repository.add_event(session_id, "MASTERY_UPDATED", {"concept": concept.concept_key, "mastery": mastery})
        action = "advance" if mastery >= 0.8 else "practice" if mastery >= 0.5 else "remediate"
        self.repository.add_event(session_id, "PATH_CHANGED", {"concept": concept.concept_key, "action": action})
        return {"concept": updated.model_dump(mode="json"), "evidence": saved.model_dump(mode="json"), "next_action": action}

