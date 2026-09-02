"""Typed application configuration loaded from environment variables."""

from typing import Literal

from pydantic import SecretStr
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
    app_env: Literal["development", "test", "production"] = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

