import json
import re
from collections.abc import Mapping
from typing import Any, Protocol

from openai import OpenAI

from .schemas import TutorResponse


def _content_as_text(content: Any) -> str:
    """Normalize OpenAI-compatible text content into a JSON-parsable string."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, Mapping):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
            else:
                text = getattr(block, "text", None)
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content)


def _tool_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    if not isinstance(arguments, dict):
        raise ValueError("os argumentos da ferramenta devem ser um objeto JSON")
    return arguments


class LLMClient(Protocol):
    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]]) -> TutorResponse: ...


class OpenAIClient:
    def __init__(self, model: str, api_key: str, base_url: str | None = None, timeout: float = 45.0) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=0)

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
                tool_calls.append({"name": call.function.name, "arguments": _tool_arguments(call.function.arguments)})
            content = _content_as_text(message.content)
            # Gemma may include an explicit reasoning block before the answer.
            content = re.sub(r"<thought>.*?</thought>", "", content, flags=re.S).strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I).strip()
            payload = json.loads(content) if content else {"phase": "PRACTICE", "tool_calls": tool_calls}
            payload["tool_calls"] = tool_calls or payload.get("tool_calls", [])
            return TutorResponse.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"Resposta estruturada inválida do LLM: {exc}") from exc
