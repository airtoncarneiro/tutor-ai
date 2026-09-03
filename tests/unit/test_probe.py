from app.learning.probe import AdaptiveProbe, ProbeEvidence


def test_probe_requires_multiple_concepts():
    probe = AdaptiveProbe()
    one = [ProbeEvidence(concept_key="group_by", answer="ok", correct=True, confidence=1)]
    two = one + [ProbeEvidence(concept_key="granularity", answer="ok", correct=True, confidence=1)]
    three = two + [ProbeEvidence(concept_key="aggregation", answer="ok", correct=True, confidence=1)]
    assert not probe.sufficient(one)
    assert probe.sufficient(three)
    assert probe.next_focus([ProbeEvidence(concept_key="aggregation", answer="x", correct=False, confidence=0)]) == "aggregation"


def test_probe_summary_prioritizes_low_confidence_evidence():
    probe = AdaptiveProbe()
    evidence = [ProbeEvidence(concept_key="group_by", answer="", correct=True, confidence=.9), ProbeEvidence(concept_key="aggregation", answer="", correct=False, confidence=.2)]
    summary = probe.summary(evidence)
    assert summary["next_focus"] == "aggregation"
    assert summary["concepts"]["aggregation"]["needs_follow_up"] is True
