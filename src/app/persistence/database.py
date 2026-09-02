"""Small PostgreSQL access layer and migration runner."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg


class Database:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(self.dsn) as connection:
            yield connection

    def migrate(self, migrations_dir: Path | str = "migrations") -> None:
        directory = Path(migrations_dir)
        migrations = sorted(directory.glob("*.sql"))
        if not migrations:
            raise FileNotFoundError(f"Nenhuma migração encontrada em {directory}")
        with self.connection() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS public.schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())")
            applied = {row[0] for row in connection.execute("SELECT version FROM public.schema_migrations")}
            for migration in migrations:
                if migration.name in applied:
                    continue
                connection.execute(migration.read_text(encoding="utf-8"))
                connection.execute("INSERT INTO public.schema_migrations (version) VALUES (%s)", (migration.name,))

