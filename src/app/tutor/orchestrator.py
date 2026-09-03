import json
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
        tool_definitions = self.registry.definitions()
        repeated_calls: dict[str, int] = {}
        for _ in range(self.max_iterations):
            response = self.client.complete(system_prompt=self.system_prompt, learning_state=state, learner_message=learner_message, tools=tool_definitions)
            if not response.tool_calls:
                return response
            results = []
            for call in response.tool_calls:
                signature = f"{call.name}:{json.dumps(call.arguments, sort_keys=True, default=str)}"
                repeated_calls[signature] = repeated_calls.get(signature, 0) + 1
                if repeated_calls[signature] > 2:
                    return TutorResponse(
                        phase="PROBE",
                        message="Não consegui concluir a operação automaticamente. Vou reformular a próxima etapa com base no último erro.",
                    )
                try:
                    result = self.registry.dispatch(call.name, call.arguments)
                except (KeyError, ValueError) as exc:
                    result = {"success": False, "retryable": False, "error": str(exc)}
                results.append({"tool": call.name, "result": result})
            state["last_tool_results"] = results
            state["tool_results_history"] = state.get("tool_results_history", []) + results
        return TutorResponse(
            phase="PROBE",
            message="A operação excedeu o limite de tentativas automáticas. Tente novamente para continuar.",
        )
