from pathlib import Path
from types import SimpleNamespace

import app.llm.client as llm_client
from streamlit.testing.v1 import AppTest


def test_gui_renders_core_controls(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "55432")
    app = AppTest.from_file(Path(__file__).parents[2] / "ui/streamlit_app.py", default_timeout=10).run()
    assert not app.exception
    assert app.title[0].value == "Adaptive SQL Tutor AI"
    assert any(item.label == "Iniciar aprendizado" for item in app.button)
    assert any(item.label == "O que você quer aprender?" for item in app.text_input)
    assert any("laboratório SQL aparecerá" in item.value for item in app.info)


class DeterministicOpenAI:
    calls = 0
    outcome = "strong"

    def __init__(self, **kwargs):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        DeterministicOpenAI.calls += 1
        correct = DeterministicOpenAI.outcome == "strong"
        answer = "Domino" if correct else "Não sei"
        responses = [
            {"phase": "PROBE", "message": "Qual é sua experiência com GROUP BY?"},
            {"phase": "PROBE", "message": "Evidência registrada.", "diagnostic_evidence": [{"concept_key": "group_by", "concept_name": "GROUP BY", "answer": answer, "correct": correct, "confidence": 0.9 if correct else 0.2}]},
            {"phase": "PROBE", "message": "Evidência registrada.", "diagnostic_evidence": [{"concept_key": "granularity", "concept_name": "Granularidade", "answer": answer, "correct": correct, "confidence": 0.9 if correct else 0.2}]},
            {"phase": "PROBE", "message": "Evidência registrada.", "diagnostic_evidence": [{"concept_key": "aggregation", "concept_name": "Agregação", "answer": answer, "correct": correct, "confidence": 0.9 if correct else 0.2}]},
        ]
        payload = responses[min(DeterministicOpenAI.calls - 1, len(responses) - 1)]
        message = SimpleNamespace(content=__import__("json").dumps(payload), tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_gui_window_functions_flow_and_sql_evaluation(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "55432")
    monkeypatch.setattr(llm_client, "OpenAI", DeterministicOpenAI)
    DeterministicOpenAI.calls = 0
    DeterministicOpenAI.outcome = "strong"
    app = AppTest.from_file(Path(__file__).parents[2] / "ui/streamlit_app.py", default_timeout=15).run()

    app.text_input[0].set_value("Quero aprender Window Functions")
    next(item for item in app.button if item.label == "Iniciar aprendizado").click().run()
    for answer in ["Domino GROUP BY", "Domino granularidade", "Domino agregação"]:
        app.chat_input[0].set_value(answer).run()

    assert not app.exception
    assert any("TEACH" in item.value for item in app.markdown)

    next(item for item in app.button if item.label == "Executar SQL").click().run()
    assert any("Digite uma consulta SQL" in item.value for item in app.warning)

    app.text_area[0].set_value("SELECT customer_id, amount FROM orders ORDER BY amount DESC")
    next(item for item in app.button if item.label == "Executar SQL").click().run()
    assert any("6 linha(s)" in item.value for item in app.caption)
    assert any(item.label == "Avaliar esta tentativa" for item in app.button)

    next(item for item in app.button if item.label == "Avaliar esta tentativa").click().run()
    assert any("Avaliação registrada" in item.value for item in app.success)

    app.text_area[0].set_value("SELECT coluna_inexistente FROM orders")
    next(item for item in app.button if item.label == "Executar SQL").click().run()
    assert any("does not exist" in item.value for item in app.error)


def test_gui_weak_prerequisites_show_remediation_path(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "55432")
    monkeypatch.setattr(llm_client, "OpenAI", DeterministicOpenAI)
    DeterministicOpenAI.calls = 0
    DeterministicOpenAI.outcome = "weak"
    app = AppTest.from_file(Path(__file__).parents[2] / "ui/streamlit_app.py", default_timeout=15).run()

    app.text_input[0].set_value("Quero aprender Window Functions")
    next(item for item in app.button if item.label == "Iniciar aprendizado").click().run()
    for answer in ["Não sei GROUP BY", "Não sei granularidade", "Não sei agregação"]:
        app.chat_input[0].set_value(answer).run()

    assert not app.exception
    assert any("aggregation" in item.value for item in app.markdown)
