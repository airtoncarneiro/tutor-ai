from typing import Any

from app.llm.client import LLMClient
from app.llm.schemas import TutorResponse
from app.tools.registry import ToolRegistry


class TutorOrchestrator:
    def __init__(self, client: LLMClient, registry: ToolRegistry, system_prompt: str, max_iterations: int = 8) -> None:
        self.client = client
        self.registry = registry
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

    def respond(self, learner_message: str, learning_state: dict[str, Any]) -> TutorResponse:
        state = dict(learning_state)
        tool_definitions = [{"type": "function", "function": {"name": name, "description": f"Executa a ferramenta {name}", "parameters": {"type": "object", "additionalProperties": True}}} for name in self.registry.names]
        for _ in range(self.max_iterations):
            response = self.client.complete(system_prompt=self.system_prompt, learning_state=state, learner_message=learner_message, tools=tool_definitions)
            if not response.tool_calls:
                return response
            results = []
            for call in response.tool_calls:
                result = self.registry.dispatch(call.name, call.arguments)
                results.append({"tool": call.name, "result": result})
            state["last_tool_results"] = results
        raise RuntimeError(f"LLM excedeu o máximo de {self.max_iterations} iterações")
