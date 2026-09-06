from typing import Any
from uuid import UUID

from app.learning.diagnostic import DiagnosticService
from app.learning.evaluation import EvaluationEvidence, EvaluationService
from app.learning.planning import PlanningService
from app.learning.probe import AdaptiveProbe, ProbeEvidence
from app.learning.scenario_exercises import exercises_for
from app.lab.generators import scenario_key
from app.lab.service import LabService
from app.learning.state_service import LearningStateService
from app.llm.client import LLMClient
from app.llm.schemas import TutorResponse
from app.persistence.database import Database
from app.persistence.repositories import LearningRepository
from app.tools.factory import create_registry
from app.tutor.orchestrator import TutorOrchestrator
from app.observability import logger, start_correlation


def _fallback_probe_evidence(message: str, evidence_count: int) -> dict[str, Any]:
    """Compatibility fallback when a provider omits structured probe evidence."""
    weak_markers = ("não sei", "nao sei", "não conheço", "nao conheco", "dificuldade", "confuso")
    strong_markers = ("domino", "entendo", "sei explicar", "tenho experiência", "tenho experiencia")
    lowered = message.lower()
    weak = any(marker in lowered for marker in weak_markers)
    strong = any(marker in lowered for marker in strong_markers)
    correct = strong and not weak
    concepts = [("group_by", "GROUP BY"), ("granularity", "Granularidade"), ("aggregation", "Agregação")]
    concept_key, concept_name = concepts[evidence_count % len(concepts)]
    return {"concept_key": concept_key, "concept_name": concept_name, "answer": message, "correct": correct, "reasoning_quality": 0.2 if weak or not strong else 0.9}


class ApplicationSessionService:
    """Single application boundary for a persisted learner conversation."""

    def __init__(self, database: Database, repository: LearningRepository, client: LLMClient, prompt: str) -> None:
        self.database, self.repository, self.client, self.prompt = database, repository, client, prompt

    def turn(self, message: str, session_id: UUID | None = None) -> tuple[UUID, TutorResponse]:
        request_id = start_correlation()
        logger.info("learner turn started correlation_id=%s", request_id)
        if not message.strip():
            raise ValueError("A mensagem do aluno não pode ser vazia")
        existing_session = session_id is not None
        if session_id is None:
            topic = self._resolve_topic(message)
            session_id = DiagnosticService(self.repository).start(topic).session_id
        state = LearningStateService(self.repository).load(session_id)
        if state.get("phase") not in {"INTENT", "PROBE", "DIAGNOSE"}:
            try:
                state["lab_context"] = LabService(self.database).inspect().model_dump(mode="json")
            except Exception as exc:
                logger.info("lab context unavailable: %s", type(exc).__name__)
        self.repository.add_event(session_id, "LEARNER_MESSAGE", {"message": message})
        response = TutorOrchestrator(self.client, create_registry(self.database), self.prompt).respond(message, state)
        diagnostic = DiagnosticService(self.repository)
        for item in response.diagnostic_evidence:
            diagnostic.record_probe(
                session_id,
                item.concept_key,
                item.concept_name,
                correct=item.correct,
                reasoning_quality=item.confidence,
                answer=item.answer or message,
                misconception=item.misconception,
            )
        if existing_session and response.phase == "PROBE" and not response.diagnostic_evidence:
            probe_count = sum(1 for item in self.repository.recent_evidence(session_id, limit=100) if item.evidence_type == "probe_answer")
            fallback = _fallback_probe_evidence(message, probe_count)
            diagnostic.record_probe(session_id, **fallback)
        self.repository.add_event(session_id, "TUTOR_RESPONSE", {"phase": response.phase, "message": response.message or ""})
        updated_state = self.state(session_id)
        if response.phase == "PROBE" and len(updated_state.get("recent_evidence", [])) >= 3:
            diagnostic.create_baseline(session_id)
            self.prepare_learning(session_id)
        return session_id, response

    def _resolve_topic(self, message: str) -> str:
        """Return a supported canonical topic, using the LLM only when needed."""
        try:
            return scenario_key(message)
        except ValueError:
            resolver = getattr(self.client, "resolve_topic", None)
            if resolver is not None:
                resolved = resolver(message)
                if resolved:
                    return resolved
            return message

    def state(self, session_id: UUID) -> dict[str, Any]:
        return LearningStateService(self.repository).load(session_id)

    def prepare_learning(self, session_id: UUID) -> dict[str, Any]:
        """Complete the deterministic post-PROBE transition and provision the lab."""
        state = self.state(session_id)
        planner = PlanningService(self.repository)
        scenario = state.get("scenario") or {}
        if not scenario:
            concepts = state.get("concepts", [])
            strengths = [item["concept_key"] for item in concepts if item["mastery"] >= 0.8]
            gaps = [item["concept_key"] for item in concepts if item["mastery"] < 0.5]
            concept_keys = {item["concept_id"]: item["concept_key"] for item in concepts}
            probe_evidence = [
                ProbeEvidence(
                    concept_key=concept_keys.get(item.get("concept_id"), "unknown"),
                    answer="",
                    correct=(item.get("correctness") or 0) >= 0.5,
                    confidence=item.get("reasoning_quality") or 0.0,
                )
                for item in state.get("recent_evidence", [])
                if item.get("evidence_type") == "probe_answer"
            ]
            scenario = planner.create_scenario(session_id, level="beginner" if gaps else "intermediate", target_capabilities=["partition data", "rank rows"], strengths=strengths, gaps=gaps, strategy={"preferred_exercises": ["REMEDIATE", "BUILD"] if gaps else ["BUILD", "DEBUG"]}, lab_requirements=["ties", "temporal ordering"], dependencies=[{"prerequisite": "aggregation", "concept": "window_semantics"}])
            scenario["diagnostic_summary"] = AdaptiveProbe().summary(probe_evidence)
            scenario["initial_exercises"] = [exercise.model_dump() for exercise in exercises_for(state["topic"])]
            self.repository.update_scenario(session_id, scenario)
        elif not scenario.get("initial_exercises"):
            # Backfill exercises for sessions created before the exercise
            # catalog was exposed in the GUI.
            scenario["initial_exercises"] = [
                exercise.model_dump() for exercise in exercises_for(state["topic"])
            ]
            self.repository.update_scenario(session_id, scenario)
        exercise_concepts = {
            exercise.get("concept")
            for exercise in scenario.get("initial_exercises", [])
            if exercise.get("concept")
        }
        known_concepts = {concept.concept_key for concept in self.repository.concepts(session_id)}
        for concept_key in exercise_concepts - known_concepts:
            self.repository.upsert_concept(
                session_id,
                concept_key,
                concept_key.replace("_", " ").title(),
            )
        planner.build_path(session_id)
        planner.provision_lab(session_id, LabService(self.database))
        self.repository.update_phase(session_id, "TEACH")
        return self.state(session_id)

    def submit_sql(self, session_id: UUID, sql: str, concept_key: str, requirement_satisfaction: float = 0.0, semantics: float = 0.0, reasoning: float = 0.0, independent: bool = True) -> dict[str, Any]:
        if not sql.strip():
            raise ValueError("A consulta SQL não pode ser vazia")
        result = LabService(self.database).execute(sql)
        state = self.state(session_id)
        exercise = ((state.get("scenario") or {}).get("initial_exercises") or [])
        exercise_text = exercise[0].get("instruction", "") if exercise else ""
        assessment = None
        assessor = getattr(self.client, "assess_sql", None)
        if assessor is not None:
            try:
                assessment = assessor(
                    exercise=exercise_text,
                    sql=sql,
                    result=result.model_dump(mode="json"),
                )
            except Exception as exc:
                logger.info("automatic SQL assessment unavailable: %s", type(exc).__name__)
        if concept_key not in {concept.concept_key for concept in self.repository.concepts(session_id)}:
            self.repository.upsert_concept(
                session_id,
                concept_key,
                concept_key.replace("_", " ").title(),
            )
        evaluation = EvaluationService(self.repository).evaluate(session_id, EvaluationEvidence(
            concept_key=concept_key,
            syntax=result.success,
            execution=result.success,
            semantics=assessment.semantics if assessment else (semantics if result.success else 0.0),
            requirement_satisfaction=assessment.requirement_satisfaction if assessment else requirement_satisfaction,
            reasoning=assessment.reasoning if assessment else reasoning,
            independent=independent,
            feedback=assessment.feedback if assessment else None,
        ))
        evaluation["sql"] = sql
        evaluation["result"] = result.model_dump(mode="json")
        evaluation["feedback"] = assessment.feedback if assessment else None
        return evaluation
