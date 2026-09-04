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


def test_settings_resolves_secret_reference_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")

    settings = Settings(
        _env_file=None,
        llm_model="test-model",
        llm_api_key="${OPENROUTER_API_KEY}",
        llm_base_url="https://openrouter.ai/api/v1/",
    )

    assert settings.llm_api_key.get_secret_value() == "sk-or-test"
