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


class InvalidThenValidLLM:
    def __init__(self):
        self.calls = 0

    def complete(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return TutorResponse(phase="PROBE", tool_calls=[ToolCall(name="execute_sql", arguments={"sql": "SELECT 1"})])
        return TutorResponse(phase="PROBE", message="Pergunta corrigida")


def test_orchestrator_returns_tool_validation_error_to_llm():
    registry = ToolRegistry()
    registry.register("inspect_lab", InspectLabInput, lambda: {"tables": []})
    client = InvalidThenValidLLM()

    result = TutorOrchestrator(client, registry, "prompt", max_iterations=2).respond("Quero aprender JOIN", {})

    assert result.message == "Pergunta corrigida"
    assert client.calls == 2


class RepeatingLLM:
    def complete(self, **kwargs):
        return TutorResponse(phase="PROBE", tool_calls=[ToolCall(name="inspect_lab")])


def test_orchestrator_stops_repeated_tool_loop():
    registry = ToolRegistry()
    registry.register("inspect_lab", InspectLabInput, lambda: {"tables": []})

    result = TutorOrchestrator(RepeatingLLM(), registry, "prompt", max_iterations=8).respond("Quero aprender JOIN", {})

    assert result.phase == "PROBE"
    assert "Não consegui concluir" in result.message


class ToolVisibilityLLM:
    def __init__(self):
        self.tools = None

    def complete(self, **kwargs):
        self.tools = [item["function"]["name"] for item in kwargs["tools"]]
        return TutorResponse(phase="PROBE", message="Pergunta diagnóstica")


def test_orchestrator_hides_lab_mutations_during_probe():
    registry = ToolRegistry()
    registry.register("create_lab", InspectLabInput, lambda: {})
    registry.register("load_learning_state", InspectLabInput, lambda: {})
    client = ToolVisibilityLLM()

    TutorOrchestrator(client, registry, "prompt").respond("Quero aprender Window Functions", {"phase": "PROBE"})

    assert client.tools == []


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


def test_openai_client_does_not_send_unsupported_response_format(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"phase":"PROBE","message":"ok"}', tool_calls=None))]
    )
    captured = {}

    class CapturingOpenAI:
        def __init__(self, **_):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        def create(self, **kwargs):
            captured.update(kwargs)
            return response

    monkeypatch.setattr(llm_client, "OpenAI", CapturingOpenAI)

    result = llm_client.OpenAIClient("deepseek/deepseek-v4-flash-0731", "key").complete(
        system_prompt="", learning_state={}, learner_message="", tools=[]
    )

    assert result.message == "ok"
    assert "response_format" not in captured


def test_openai_client_unwraps_json_encoded_object(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(
            content='"{\\"phase\\":\\"PROBE\\",\\"message\\":\\"ok\\"}"',
            tool_calls=None,
        ))]
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


def test_openai_client_normalizes_null_tool_calls(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"phase":"TEACH","message":"Vamos continuar.","tool_calls":null}', tool_calls=None))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").complete(
        system_prompt="", learning_state={}, learner_message="", tools=[]
    )

    assert result.message == "Vamos continuar."
    assert result.tool_calls == []


def test_openai_client_accepts_textual_reasoning_in_assessment(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(
            content='{"phase":"EVALUATE","semantics":0.8,"requirement_satisfaction":1.0,"reasoning":"Explicou corretamente.","feedback":"Boa solução."}',
            tool_calls=None,
        ))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").assess_sql(
        exercise="some exercise", sql="SELECT 1", result={"success": True}
    )

    assert result.reasoning == 0.5
    assert result.feedback == "Boa solução."


class TransientError(Exception):
    status_code = 503


class RetryingOpenAI:
    def __init__(self, response):
        self.calls = 0
        self.response = response
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **_):
        self.calls += 1
        if self.calls < 3:
            raise TransientError("temporary outage")
        return self.response


def test_openai_client_retries_transient_provider_failure(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"phase":"PROBE","message":"ok"}', tool_calls=None))]
    )
    fake = RetryingOpenAI(response)
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: fake)
    sleeps = []
    monkeypatch.setattr(llm_client.time, "sleep", sleeps.append)

    result = llm_client.OpenAIClient("model", "key", max_attempts=3, backoff_seconds=0.25).complete(system_prompt="", learning_state={}, learner_message="", tools=[])

    assert result.message == "ok"
    assert fake.calls == 3
    assert sleeps == [0.25, 0.5]


def test_openai_client_retries_incomplete_gateway_response(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"phase":"TEACH","message":"ok"}', tool_calls=None))]
    )

    class FlakyOpenAI:
        def __init__(self, _response):
            self.calls = 0
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        def create(self, **_):
            self.calls += 1
            if self.calls == 1:
                raise TypeError("'NoneType' object is not subscriptable")
            return response

    fake = FlakyOpenAI(response)
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: fake)
    monkeypatch.setattr(llm_client.time, "sleep", lambda _: None)

    result = llm_client.OpenAIClient("model", "key", max_attempts=2).complete(
        system_prompt="", learning_state={}, learner_message="", tools=[]
    )

    assert result.message == "ok"
    assert fake.calls == 2


def test_openai_client_maps_question_response_to_probe_message(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"question":"Qual é sua experiência?"}', tool_calls=None))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").complete(system_prompt="", learning_state={}, learner_message="", tools=[])

    assert result.phase == "PROBE"
    assert result.message == "Qual é sua experiência?"


def test_openai_client_replaces_empty_learner_response_with_probe(monkeypatch):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"phase":"PRACTICE"}', tool_calls=None))]
    )
    monkeypatch.setattr(llm_client, "OpenAI", lambda **_: FakeOpenAI(response))

    result = llm_client.OpenAIClient("model", "key").complete(system_prompt="", learning_state={}, learner_message="", tools=[])

    assert result.phase == "PROBE"
    assert result.message
