from types import SimpleNamespace

import app.llm.client as llm_client
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


class FakeOpenAI:
    def __init__(self, response):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **_: response))


def test_openai_client_normalizes_list_content(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=[{"type": "text", "text": '{"phase":"PROBE","message":"ok"}'}], tool_calls=None))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").complete(system_prompt="", learning_state={}, learner_message="", tools=[])

    assert result.phase == "PROBE"
    assert result.message == "ok"


def test_openai_client_normalizes_structured_tool_arguments(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(
            content=None,
            tool_calls=[SimpleNamespace(function=SimpleNamespace(name="inspect_lab", arguments={}))],
        ))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").complete(system_prompt="", learning_state={}, learner_message="", tools=[])

    assert result.tool_calls[0].name == "inspect_lab"
    assert result.tool_calls[0].arguments == {}
