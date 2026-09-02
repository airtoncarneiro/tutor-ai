from app.application.session_service import ApplicationSessionService


def test_empty_turn_is_rejected():
    try:
        ApplicationSessionService(None, None, None, "").turn(" ")
    except ValueError as exc:
        assert "vazia" in str(exc)
    else:
        raise AssertionError("esperava erro")

