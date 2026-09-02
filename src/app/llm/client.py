import json
from typing import Any, Protocol

from openai import OpenAI

from .schemas import TutorResponse


class LLMClient(Protocol):
    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]]) -> TutorResponse: ...


class OpenAIClient:
    def __init__(self, model: str, api_key: str) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]]) -> TutorResponse:
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=json.dumps({"learning_state": learning_state, "learner_message": learner_message}, ensure_ascii=False),
            tools=tools,
        )
        try:
            return TutorResponse.model_validate_json(response.output_text)
        except Exception as exc:
            raise ValueError(f"Resposta estruturada inválida do LLM: {exc}") from exc

