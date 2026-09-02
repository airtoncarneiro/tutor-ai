from app.learning.diagnostic import DiagnosticService


class FakeRepo:
    def __init__(self): self.events = []

    def create_session(self, session_id, topic, goal):
        from app.persistence.models import LearningSession
        from datetime import datetime, timezone
        return LearningSession(session_id=session_id, topic=topic, goal=goal, phase="INTENT", status="active", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))

    def add_event(self, *args): self.events.append(args)
    def update_phase(self, session_id, phase, status=None):
        session = self.create_session(session_id, "JOIN", None); session.phase = phase; return session


def test_start_enters_probe_without_lab():
    repo = FakeRepo()
    session = DiagnosticService(repo).start(" JOIN ")
    assert session.phase == "PROBE"
    assert repo.events[0][1] == "PROBE_STARTED"

