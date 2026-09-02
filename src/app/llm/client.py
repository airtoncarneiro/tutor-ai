import json
import re
from typing import Any, Protocol

from openai import OpenAI

from .schemas import TutorResponse


class LLMClient(Protocol):
    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]]) -> TutorResponse: ...


class OpenAIClient:
    def __init__(self, model: str, api_key: str, base_url: str | None = None) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]]) -> TutorResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps({"learning_state": learning_state, "learner_message": learner_message}, ensure_ascii=False)},
            ],
            tools=tools,
            response_format={"type": "json_object"},
        )
        try:
            message = response.choices[0].message
            tool_calls = []
            for call in message.tool_calls or []:
                tool_calls.append({"name": call.function.name, "arguments": json.loads(call.function.arguments)})
            content = message.content or ""
            # Gemma may include an explicit reasoning block before the answer.
            content = re.sub(r"<thought>.*?</thought>", "", content, flags=re.S).strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I).strip()
            payload = json.loads(content) if content else {"phase": "PRACTICE", "tool_calls": tool_calls}
            payload["tool_calls"] = tool_calls or payload.get("tool_calls", [])
            return TutorResponse.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"Resposta estruturada inválida do LLM: {exc}") from exc
