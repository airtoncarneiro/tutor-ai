from .config import Settings
from .persistence.database import Database


def main() -> None:
    settings = Settings()
    Database(settings.postgres_dsn).migrate()
    print("Migrações aplicadas com sucesso.")

