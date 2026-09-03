"""Contextual scenario, dependency graph and short-horizon planning."""

from typing import Any
from uuid import UUID

from app.persistence.repositories import LearningRepository
from app.lab.generators import generate_topic_lab
from app.lab.service import LabService


class PlanningService:
    def __init__(self, repository: LearningRepository) -> None:
        self.repository = repository

    def create_scenario(self, session_id: UUID, *, level: str, target_capabilities: list[str], strengths: list[str], gaps: list[str], strategy: dict[str, Any], lab_requirements: list[str], dependencies: list[dict[str, str]]) -> dict[str, Any]:
        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        scenario = {"topic": session.topic, "goal": session.goal, "level": level, "target_capabilities": target_capabilities, "strengths": strengths, "gaps": gaps, "strategy": strategy, "lab_requirements": lab_requirements, "knowledge_graph": {"dependencies": dependencies}}
        self.repository.update_scenario(session_id, scenario)
        self.repository.add_event(session_id, "SCENARIO_CREATED", {"topic": session.topic})
        return scenario

    def build_path(self, session_id: UUID) -> dict[str, Any]:
        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        concepts = self.repository.concepts(session_id)
        insufficient = [c for c in concepts if c.mastery < 0.5]
        partial = [c for c in concepts if 0.5 <= c.mastery < 0.8]
        current = insufficient[0] if insufficient else partial[0] if partial else None
        candidates = [{"concept": c.concept_key, "priority": round(1 - c.mastery, 3)} for c in concepts if c != current]
        path = {"current": current.concept_key if current else None, "next": sorted(candidates, key=lambda item: item["priority"], reverse=True)[:3], "near_future": [{"concept": "target_topic", "priority": 0.5}]}
        scenario = dict(session.scenario or {})
        scenario["learning_path"] = path
        self.repository.update_scenario(session_id, scenario, phase="PLAN")
        self.repository.add_event(session_id, "PATH_CREATED", path)
        return path

    def provision_lab(self, session_id: UUID, lab_service: LabService) -> object:
        session = self.repository.get_session(session_id)
        if session is None:
            raise ValueError(f"Sessão não encontrada: {session_id}")
        definition, summary = generate_topic_lab(session.topic, lab_service)
        lab_description = definition.description if hasattr(definition, "description") else definition.definition.description
        self.repository.add_event(session_id, "LAB_CREATED", {"description": lab_description})
        return summary
