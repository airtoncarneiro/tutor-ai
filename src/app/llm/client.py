import json
import re
import time
from collections.abc import Mapping
from typing import Any, Protocol

from openai import OpenAI

from app.observability import log_event, timed_event

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
    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]], conversation: list[dict[str, Any]] | None = None) -> TutorResponse: ...


class LLMProviderUnavailableError(RuntimeError):
    """Sanitized error raised after exhausting transient provider retries."""


class OpenAIClient:
    def __init__(self, model: str, api_key: str, base_url: str | None = None, timeout: float = 45.0, max_attempts: int = 3, backoff_seconds: float = 1.0) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts deve ser positivo")
        self.model = model
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=0)

    def complete(self, *, system_prompt: str, learning_state: dict[str, Any], learner_message: str, tools: list[dict[str, Any]], conversation: list[dict[str, Any]] | None = None) -> TutorResponse:
        messages = [{"role": "system", "content": system_prompt}]
        for item in conversation or []:
            messages.append({"role": item["role"], "content": item["content"]})
        messages.append({"role": "user", "content": json.dumps({"learning_state": learning_state, "learner_message": learner_message}, ensure_ascii=False)})
        response = None
        for attempt in range(self.max_attempts):
            try:
                with timed_event("llm_request", provider="openai_compatible", model=self.model, attempt=attempt + 1):
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools,
                        response_format={"type": "json_object"},
                    )
                log_event("llm_response", model=self.model, attempt=attempt + 1, tool_count=len(getattr(response.choices[0].message, "tool_calls", None) or []))
                break
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                retryable = status in {429, 500, 502, 503, 504} or exc.__class__.__name__ in {"APIConnectionError", "APITimeoutError"}
                log_event("llm_failure", model=self.model, attempt=attempt + 1, status=status, retryable=retryable)
                if not retryable:
                    raise
                if attempt == self.max_attempts - 1:
                    raise LLMProviderUnavailableError("O provedor LLM está temporariamente indisponível após as tentativas configuradas.") from exc
                time.sleep(self.backoff_seconds * (2 ** attempt))
        try:
            assert response is not None
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
            if not isinstance(payload, dict):
                raise ValueError("a resposta estruturada deve ser um objeto JSON")
            # Some OpenAI-compatible models use `question` for a learner-facing
            # diagnostic prompt and omit the phase; map that safe equivalent to
            # the internal TutorResponse contract.
            payload.setdefault("phase", "PROBE" if payload.get("question") else "PRACTICE")
            if not payload.get("message") and isinstance(payload.get("question"), str):
                payload["message"] = payload["question"]
            payload["tool_calls"] = tool_calls or payload.get("tool_calls", [])
            if not payload.get("message") and not payload["tool_calls"]:
                payload["phase"] = "PROBE"
                payload["message"] = "Antes de começarmos: qual é sua experiência atual com SQL e com GROUP BY?"
            return TutorResponse.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"Resposta estruturada inválida do LLM: {exc}") from exc
