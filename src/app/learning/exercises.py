from typing import Literal

from pydantic import BaseModel, Field

from app.lab.models import SqlResult
from app.lab.service import LabService


ExerciseMode = Literal["EXECUTE", "BUILD", "DEBUG", "MODIFY"]


class SqlExercise(BaseModel):
    mode: ExerciseMode
    instruction: str
    concept: str
    tutor_sql: str | None = None
    baseline_sql: str | None = None
    requirement: str | None = None


class ExerciseAttempt(BaseModel):
    mode: ExerciseMode
    submitted_sql: str
    result: SqlResult
    requirement: str | None = None


class ExerciseService:
    def __init__(self, lab: LabService) -> None:
        self.lab = lab

    def execute(self, exercise: SqlExercise) -> ExerciseAttempt:
        if not exercise.tutor_sql:
            raise ValueError("Exercício EXECUTE exige tutor_sql")
        result = SqlResult.model_validate(self.lab.execute(exercise.tutor_sql))
        return ExerciseAttempt(mode=exercise.mode, submitted_sql=exercise.tutor_sql, result=result, requirement=exercise.instruction)

    def submit(self, exercise: SqlExercise, sql: str) -> ExerciseAttempt:
        if not sql.strip():
            raise ValueError("A consulta enviada não pode ser vazia")
        result = SqlResult.model_validate(self.lab.execute(sql))
        return ExerciseAttempt(mode=exercise.mode, submitted_sql=sql, result=result, requirement=exercise.requirement or exercise.instruction)
