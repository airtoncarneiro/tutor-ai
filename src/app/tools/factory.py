from app.lab.service import LabService
from app.persistence.database import Database
from app.persistence.repositories import LearningRepository

from .lab_tools import register_lab_tools
from .learning_tools import register_learning_tools
from .registry import ToolRegistry


def create_registry(database: Database) -> ToolRegistry:
    registry = ToolRegistry()
    register_lab_tools(registry, LabService(database))
    register_learning_tools(registry, LearningRepository(database))
    return registry

