from pydantic import BaseModel, Field


class ProbeEvidence(BaseModel):
    concept_key: str = Field(min_length=1)
    answer: str
    correct: bool
    confidence: float = Field(ge=0, le=1)


class AdaptiveProbe:
    def sufficient(self, evidence: list[ProbeEvidence], minimum: int = 3) -> bool:
        return len(evidence) >= minimum and len({item.concept_key for item in evidence}) >= 2

    def next_focus(self, evidence: list[ProbeEvidence]) -> str:
        weak = [item for item in evidence if not item.correct or item.confidence < 0.5]
        return weak[-1].concept_key if weak else "window_semantics"

