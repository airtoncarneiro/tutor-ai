import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_builds_postgres_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    settings = Settings(_env_file=None)

    assert settings.postgres_dsn == "postgresql://tutor:tutor@localhost:5432/tutor"


def test_settings_requires_llm_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)

