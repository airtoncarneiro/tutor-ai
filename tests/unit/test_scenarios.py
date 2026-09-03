from app.lab.generators import scenario_key
from app.lab.scenarios import cte_lab, join_lab, null_lab, recursive_lab, optimization_lab


def test_join_lab_contains_unmatched_row():
    definition = join_lab()
    assert any("customers" in statement for statement in definition.ddl)
    assert any("99" in statement for statement in definition.seed_sql)


def test_cte_lab_contains_multiple_regions():
    assert "Norte" in cte_lab().seed_sql[0] and "Sul" in cte_lab().seed_sql[0]

def test_extended_scenarios_have_pedagogical_edges():
    assert "NULL" in null_lab().seed_sql[0]
    assert "parent_id" in recursive_lab().definition.ddl[0] if hasattr(recursive_lab(), "definition") else "parent_id" in recursive_lab().ddl[0]
    assert "INDEX" in optimization_lab().ddl[1]


def test_topics_select_their_pedagogical_lab():
    assert scenario_key("Quero aprender JOIN") == "join"
    assert scenario_key("Quero aprender CTE recursiva") == "cte"
    assert scenario_key("Quero aprender semântica de NULL") == "null"
    assert scenario_key("Quero aprender otimização") == "optimization"
