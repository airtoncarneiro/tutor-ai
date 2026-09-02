from app.llm.schemas import ToolCall, TutorResponse
from app.tutor.orchestrator import TutorOrchestrator
from app.tools.registry import ToolRegistry
from app.tools.models import InspectLabInput


class FakeLLM:
    def __init__(self):
        self.calls = 0

    def complete(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return TutorResponse(phase="PROBE", tool_calls=[ToolCall(name="inspect_lab")])
        if self.calls == 2:
            return TutorResponse(phase="PROBE", tool_calls=[ToolCall(name="inspect_lab")])
        return TutorResponse(phase="PROBE", message="Qual é o resultado?")


def test_orchestrator_runs_sequential_tool_calls():
    registry = ToolRegistry()
    registry.register("inspect_lab", InspectLabInput, lambda: {"tables": []})
    client = FakeLLM()
    result = TutorOrchestrator(client, registry, "prompt", max_iterations=3).respond("Quero aprender JOIN", {})
    assert result.message == "Qual é o resultado?"
    assert client.calls == 3
