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
        """Choose the least reliable concept, preferring low-confidence evidence."""
        if not evidence:
            return "group_by"
        weak = [item for item in evidence if not item.correct or item.confidence < 0.5]
        if weak:
            return min(weak, key=lambda item: (item.correct, item.confidence)).concept_key
        return "window_semantics"

    def summary(self, evidence: list[ProbeEvidence]) -> dict[str, object]:
        by_concept: dict[str, list[ProbeEvidence]] = {}
        for item in evidence:
            by_concept.setdefault(item.concept_key, []).append(item)
        concepts = {
            key: {
                "attempts": len(items),
                "correct_rate": round(sum(item.correct for item in items) / len(items), 3),
                "confidence": round(sum(item.confidence for item in items) / len(items), 3),
                "needs_follow_up": any(not item.correct or item.confidence < 0.5 for item in items),
            }
            for key, items in by_concept.items()
        }
        return {"sufficient": self.sufficient(evidence), "next_focus": self.next_focus(evidence), "concepts": concepts}
