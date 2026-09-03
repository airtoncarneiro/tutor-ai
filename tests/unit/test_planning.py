from app.learning.planning import PlanningService


def test_path_prioritizes_insufficient_concept():
    class Repo:
        def get_session(self, _): return type("S", (), {"topic": "JOIN", "goal": None, "scenario": {}})()
        def concepts(self, _): return [type("C", (), {"concept_key": "aggregation", "mastery": 0.2})(), type("C", (), {"concept_key": "joins", "mastery": 0.8})()]
        def update_scenario(self, *args, **kwargs): pass
        def add_event(self, *args): pass
    path = PlanningService(Repo()).build_path("id")
    assert path["current"] == "aggregation"
    assert path["next"][0]["concept"] == "joins"


def test_strong_prerequisites_leave_no_remediation_current_concept():
    class Repo:
        def get_session(self, _): return type("S", (), {"topic": "Window Functions", "goal": None, "scenario": {}})()
        def concepts(self, _): return [type("C", (), {"concept_key": "aggregation", "mastery": 0.9})(), type("C", (), {"concept_key": "group_by", "mastery": 0.9})()]
        def update_scenario(self, *args, **kwargs): pass
        def add_event(self, *args): pass

    path = PlanningService(Repo()).build_path("id")

    assert path["current"] is None
