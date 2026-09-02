from app.lab.evolution import LabExtensionRequest, LabEvolutionService


def test_extension_is_detected_when_table_is_missing():
    class Lab:
        def inspect(self): return type("S", (), {"tables": []})()
    assert LabEvolutionService(Lab()).needs_extension(["events"])


def test_extension_request_requires_reason():
    try:
        LabExtensionRequest(reason="", required_tables=["events"])
    except Exception:
        pass
    else:
        raise AssertionError("reason deveria ser obrigatório")

