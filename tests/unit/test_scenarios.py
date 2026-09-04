from app.lab.generators import scenario_key
from app.lab.scenarios import (advanced_aggregation_lab, cte_lab, date_functions_lab,
                               deduplication_lab, join_lab, null_lab,
                               optimization_lab, recursive_lab, subquery_lab,
                               transactions_lab)
from app.learning.scenario_exercises import exercises_for


def test_join_lab_contains_unmatched_row():
    definition = join_lab()
    assert any("customers" in statement for statement in definition.ddl)
    assert any("99" in statement for statement in definition.seed_sql)


def test_cte_lab_contains_multiple_regions():
    assert "Norte" in cte_lab().seed_sql[0] and "Sul" in cte_lab().seed_sql[0]

def test_extended_scenarios_have_pedagogical_edges():
    assert "NULL" in null_lab().seed_sql[0]
    assert "parent_id" in recursive_lab().definition.ddl[0] if hasattr(recursive_lab(), "definition") else "parent_id" in recursive_lab().ddl[0]
    assert "INDEX" not in " ".join(optimization_lab().ddl).upper()


def test_topics_select_their_pedagogical_lab():
    assert scenario_key("Quero aprender JOIN") == "join"
    assert scenario_key("Quero aprender CTE recursiva") == "recursive"
    assert scenario_key("Quero aprender semântica de NULL") == "null"
    assert scenario_key("Quero aprender otimização") == "optimization"
    assert scenario_key("Quero aprender subqueries") == "subqueries"
    assert scenario_key("Quero aprender agregações avançadas") == "aggregation"
    assert scenario_key("Quero aprender agregração") == "aggregation"
    assert scenario_key("Quero aprender deduplicação") == "deduplication"
    assert scenario_key("Quero aprender transações") == "transactions"
    assert scenario_key("Quero aprender funções de data") == "date_functions"


def test_extended_labs_have_required_pedagogical_data():
    assert "EXISTS" in subquery_lab().description.upper()
    assert "FILTER" in advanced_aggregation_lab().description.upper()
    assert "retry" in " ".join(deduplication_lab().seed_sql)
    assert "ledger" in " ".join(transactions_lab().ddl)
    assert "2026-03" in " ".join(date_functions_lab().seed_sql)


def test_extended_topics_have_executable_requirements():
    assert exercises_for("subqueries")[0].requirement
    assert exercises_for("agregações")[0].concept == "advanced_aggregation"
    assert exercises_for("deduplicação")[0].concept == "deduplication"
    assert exercises_for("transações")[0].concept == "transactions"
    assert exercises_for("funções de data")[0].concept == "date_functions"
    assert exercises_for("Window Functions")[0].concept == "window_semantics"
    assert exercises_for("agregração")[0].concept == "advanced_aggregation"
