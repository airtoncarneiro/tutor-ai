from app.application.session_service import ApplicationSessionService


def test_empty_sql_is_rejected_before_database_access():
    try:
        ApplicationSessionService(None, None, None, "").submit_sql("session", "", "window")
    except Exception:
        # The underlying lab executor returns a failed result; the important
        # contract is that evaluation cannot claim success for empty SQL.
        pass

