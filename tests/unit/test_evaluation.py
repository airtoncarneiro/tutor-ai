from app.learning.evaluation import EvaluationEvidence, MasteryEngine


def test_repeated_strong_evidence_increases_mastery():
    engine = MasteryEngine()
    evidence = EvaluationEvidence(concept_key="x", syntax=True, execution=True, semantics=1, requirement_satisfaction=1, reasoning=1)
    first, _ = engine.update(0.4, evidence, 1)
    second, _ = engine.update(first, evidence, 2)
    assert second > first


def test_single_weak_evidence_does_not_establish_mastery():
    evidence = EvaluationEvidence(concept_key="x", syntax=True, execution=True, semantics=.3, requirement_satisfaction=.2, reasoning=.2)
    mastery, confidence = MasteryEngine().update(0.0, evidence, 1)
    assert mastery < .5 and confidence == "low"


def test_incorrect_evidence_reduces_mastery():
    evidence = EvaluationEvidence(concept_key="x", syntax=False, execution=False, semantics=0, requirement_satisfaction=0, reasoning=0)
    mastery, confidence = MasteryEngine().update(.8, evidence, 2)
    assert mastery < .8 and confidence == "low"

