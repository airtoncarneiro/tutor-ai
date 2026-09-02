from app.lab.specifications import window_functions_specification


def test_window_lab_spec_has_required_invariants():
    spec = window_functions_specification()
    assert {table.name for table in spec.tables} == {"customers", "orders"}
    assert any("empat" in invariant for invariant in spec.pedagogical_invariants)
    assert len(spec.definition.seed_sql) == 2

