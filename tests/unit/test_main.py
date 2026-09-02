from app.main import main


def test_main_starts(monkeypatch, capsys) -> None:
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    main()

    assert "Adaptive SQL Tutor iniciado" in capsys.readouterr().out

