"""Typed application configuration loaded from environment variables."""

import os
import re
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tutor"
    postgres_user: str = "tutor"
    postgres_password: SecretStr = SecretStr("tutor")

    llm_provider: str = "openai"
    llm_model: str
    llm_api_key: SecretStr
    llm_base_url: str | None = None
    llm_timeout_seconds: float = 20.0
    app_env: Literal["development", "test", "production"] = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("llm_api_key", mode="before")
    @classmethod
    def resolve_secret_reference(cls, value: object) -> object:
        """Resolve a literal ``${ENV_NAME}`` inherited from the shell.

        Some dotenv loaders expand references while Pydantic Settings gives
        precedence to an already-exported environment variable. This keeps a
        stale ``LLM_API_KEY=${OPENROUTER_API_KEY}`` from being sent as the
        bearer token when the referenced variable is available.
        """
        raw = value.get_secret_value() if isinstance(value, SecretStr) else value
        if isinstance(raw, str):
            match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", raw)
            if match:
                resolved = os.getenv(match.group(1))
                if resolved:
                    return resolved
        return value

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
