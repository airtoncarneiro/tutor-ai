from app.lab.specifications import window_functions_specification


def test_window_lab_spec_has_required_invariants():
    spec = window_functions_specification()
    assert {table.name for table in spec.tables} == {"customers", "orders"}
    assert any("empat" in invariant for invariant in spec.pedagogical_invariants)
    assert len(spec.definition.seed_sql) == 2
import pytest

from app.lab.models import LabDefinition
from app.lab.service import LabService


class FakeConnection:
    def __init__(self):
        self.statements = []
        self.rollbacks = 0

    def execute(self, statement, params=None):
        self.statements.append(statement)
        if "salary salary" in statement:
            raise RuntimeError('syntax error at or near "INT"')
        if "VALUES (1), (1)" in statement:
            raise RuntimeError('duplicate key value violates unique constraint')

    def rollback(self):
        self.rollbacks += 1


class FakeConnectionContext:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, *_):
        return False


class FakeDatabase:
    def __init__(self):
        self.connection_instance = FakeConnection()

    def connection(self):
        return FakeConnectionContext(self.connection_instance)


def test_invalid_lab_ddl_is_rejected_before_replacement():
    database = FakeDatabase()
    service = LabService(database)

    with pytest.raises(ValueError, match="validação PostgreSQL falhou"):
        service.create_or_replace(LabDefinition(ddl=["CREATE TABLE employees (salary salary INT)"]))

    assert "DROP SCHEMA IF EXISTS lab CASCADE" not in database.connection_instance.statements
    assert database.connection_instance.rollbacks == 1


def test_invalid_lab_extension_is_rejected_before_apply():
    database = FakeDatabase()
    service = LabService(database)

    with pytest.raises(ValueError, match="Extensão do Learning Lab inválida"):
        service.extend(dml=["INSERT INTO employees (employee_id) VALUES (1), (1)"])

    assert database.connection_instance.statements == ["SET search_path TO lab", "INSERT INTO employees (employee_id) VALUES (1), (1)"]
    assert database.connection_instance.rollbacks == 1
