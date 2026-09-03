from types import SimpleNamespace

from app.application.session_service import ApplicationSessionService
from app.llm.schemas import DiagnosticEvidence, TutorResponse


def test_empty_turn_is_rejected():
    try:
        ApplicationSessionService(None, None, None, "").turn(" ")
    except ValueError as exc:
        assert "vazia" in str(exc)
    else:
        raise AssertionError("esperava erro")


def test_tutor_response_supports_diagnostic_evidence():
    response = TutorResponse(
        phase="PROBE",
        message="Qual é sua experiência?",
        diagnostic_evidence=[DiagnosticEvidence(concept_key="group_by", concept_name="GROUP BY", correct=False, confidence=0.2)],
    )

    assert response.diagnostic_evidence[0].concept_key == "group_by"
