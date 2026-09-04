import pytest

from app.config import Settings
from app.lab.generators import generate_topic_lab
from app.lab.service import LabService
from app.persistence.database import Database


@pytest.mark.parametrize(
    ("topic", "expected_table"),
    [
        ("JOIN", "customers"),
        ("subqueries", "orders"),
        ("agregações avançadas", "sales"),
        ("deduplicação", "customer_events"),
        ("transações", "accounts"),
        ("funções de data", "appointments"),
        ("CTE recursiva", "org"),
    ],
)
def test_extended_topic_provisions_real_lab(monkeypatch, topic, expected_table):
    monkeypatch.setenv("POSTGRES_PORT", "55432")
    settings = Settings()
    database = Database(settings.postgres_dsn)
    database.migrate()
    summary = generate_topic_lab(topic, LabService(database))[1]
    assert expected_table in {table.name for table in summary.tables}
