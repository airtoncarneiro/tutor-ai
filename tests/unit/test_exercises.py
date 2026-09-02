from app.learning.exercises import ExerciseService, SqlExercise
from app.lab.models import SqlResult


def test_build_returns_sql_and_real_result():
    class Lab:
        def execute(self, sql):
            return SqlResult(success=True, columns=["x"], rows=[[1]], row_count=1)
    attempt = ExerciseService(Lab()).submit(SqlExercise(mode="BUILD", instruction="retorne 1", concept="sql", requirement="resultado 1"), "SELECT 1")
    assert attempt.submitted_sql == "SELECT 1"
    assert attempt.result.rows == [[1]]


def test_execute_requires_tutor_query():
    class Lab:
        def execute(self, sql): raise AssertionError("não deveria executar")
    try:
        ExerciseService(Lab()).execute(SqlExercise(mode="EXECUTE", instruction="x", concept="sql"))
    except ValueError as exc:
        assert "tutor_sql" in str(exc)
    else:
        raise AssertionError("esperava erro de validação")
