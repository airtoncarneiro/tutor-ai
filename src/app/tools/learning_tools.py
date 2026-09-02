from app.persistence.repositories import LearningRepository
from app.learning.state_service import LearningStateService
from .models import LoadLearningStateInput, SaveLearningEvidenceInput
from .registry import ToolRegistry


def register_learning_tools(registry: ToolRegistry, repository: LearningRepository) -> None:
    state_service = LearningStateService(repository)
    registry.register("load_learning_state", LoadLearningStateInput, lambda **kwargs: state_service.load(kwargs["session_id"]))

    def save(**kwargs):
        session_id = kwargs.pop("session_id")
        return repository.add_evidence(session_id, **kwargs).model_dump(mode="json")

    registry.register("save_learning_evidence", SaveLearningEvidenceInput, save)

