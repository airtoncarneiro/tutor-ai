from app.learning.probe import AdaptiveProbe, ProbeEvidence


def test_probe_requires_multiple_concepts():
    probe = AdaptiveProbe()
    one = [ProbeEvidence(concept_key="group_by", answer="ok", correct=True, confidence=1)]
    two = one + [ProbeEvidence(concept_key="granularity", answer="ok", correct=True, confidence=1)]
    three = two + [ProbeEvidence(concept_key="aggregation", answer="ok", correct=True, confidence=1)]
    assert not probe.sufficient(one)
    assert probe.sufficient(three)
    assert probe.next_focus([ProbeEvidence(concept_key="aggregation", answer="x", correct=False, confidence=0)]) == "aggregation"
