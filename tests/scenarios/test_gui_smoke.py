from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_gui_renders_core_controls(monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "55432")
    app = AppTest.from_file(Path(__file__).parents[2] / "ui/streamlit_app.py", default_timeout=10).run()
    assert not app.exception
    assert app.title[0].value == "Adaptive SQL Tutor"
    assert any(item.label == "Executar SQL" for item in app.button)
    assert any(item.label == "Escreva uma consulta SQL" for item in app.text_area)
