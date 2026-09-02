"""Deterministic services for provisioning and querying the lab schema."""

import re
from typing import Iterable

from app.persistence.database import Database

from .models import LabDefinition, LabSummary, LabTable, LabColumn, SqlResult


_FORBIDDEN = re.compile(r"\b(tutor\.|public\.schema_migrations|create\s+schema|drop\s+schema)\b", re.I)


def _validate_lab_sql(statements: Iterable[str]) -> None:
    for statement in statements:
        if _FORBIDDEN.search(statement):
            raise ValueError("SQL do Learning Lab não pode acessar a schema tutor nem criar/remover schemas")


class LabService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_or_replace(self, definition: LabDefinition) -> LabSummary:
        _validate_lab_sql([*definition.ddl, *definition.seed_sql])
        ddl = ";\n".join(definition.ddl)
        seed = ";\n".join(definition.seed_sql)
        with self.database.connection() as conn:
            conn.execute("DROP SCHEMA IF EXISTS lab CASCADE")
            conn.execute("CREATE SCHEMA lab")
            conn.execute("SET search_path TO lab")
            for statement in definition.ddl:
                conn.execute(statement)
            for statement in definition.seed_sql:
                conn.execute(statement)
            conn.execute("SET search_path TO public")
            conn.execute("""INSERT INTO tutor.lab_baseline (baseline_id, ddl, seed_sql)
                VALUES (1, %s, %s) ON CONFLICT (baseline_id) DO UPDATE
                SET ddl=EXCLUDED.ddl, seed_sql=EXCLUDED.seed_sql, updated_at=now()""", (ddl, seed))
        return self.inspect()

    def reset(self) -> LabSummary:
        with self.database.connection() as conn:
            row = conn.execute("SELECT ddl, seed_sql FROM tutor.lab_baseline WHERE baseline_id=1").fetchone()
        if row is None:
            raise ValueError("Nenhum baseline do Learning Lab foi criado")
        return self.create_or_replace(LabDefinition(ddl=[part.strip() for part in row[0].split(";") if part.strip()], seed_sql=[part.strip() for part in row[1].split(";") if part.strip()]))

    def extend(self, ddl: list[str] | None = None, dml: list[str] | None = None) -> LabSummary:
        statements = [*(ddl or []), *(dml or [])]
        _validate_lab_sql(statements)
        with self.database.connection() as conn:
            conn.execute("SET search_path TO lab")
            for statement in statements:
                conn.execute(statement)
            conn.execute("SET search_path TO public")
        return self.inspect()

    def execute(self, sql: str) -> SqlResult:
        _validate_lab_sql([sql])
        try:
            with self.database.connection() as conn:
                conn.execute("SET search_path TO lab")
                cursor = conn.execute(sql)
                if cursor.description is None:
                    return SqlResult(success=True)
                columns = [column.name for column in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return SqlResult(success=True, columns=columns, rows=rows, row_count=len(rows))
        except Exception as exc:
            return SqlResult(success=False, error=str(exc))

    def inspect(self) -> LabSummary:
        with self.database.connection() as conn:
            tables = conn.execute("""SELECT table_name FROM information_schema.tables
                WHERE table_schema='lab' AND table_type='BASE TABLE' ORDER BY table_name""").fetchall()
            result = []
            for (name,) in tables:
                columns = conn.execute("""SELECT column_name, data_type, is_nullable='YES'
                    FROM information_schema.columns WHERE table_schema='lab' AND table_name=%s ORDER BY ordinal_position""", (name,)).fetchall()
                pks = conn.execute("""SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid=i.indrelid
                    AND a.attnum=ANY(i.indkey) WHERE i.indrelid=%s::regclass AND i.indisprimary""", (f'lab.{name}',)).fetchall()
                indexes = conn.execute("SELECT indexname FROM pg_indexes WHERE schemaname='lab' AND tablename=%s ORDER BY indexname", (name,)).fetchall()
                result.append(LabTable(name=name, columns=[LabColumn(name=c[0], data_type=c[1], nullable=c[2]) for c in columns], primary_key=[p[0] for p in pks], indexes=[i[0] for i in indexes]))
        return LabSummary(tables=result)
