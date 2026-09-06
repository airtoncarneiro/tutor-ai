import json
import re
import time
from collections.abc import Mapping
from typing import Any, Protocol

from openai import OpenAI

from app.observability import log_event, timed_event

from .schemas import SqlAssessment, TutorResponse


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


def _structured_payload(content: str) -> dict[str, Any]:
    """Decode provider JSON while tolerating common compatible-gateway wrappers.

    Some OpenAI-compatible gateways return the model's JSON object as a JSON
    string (for example, ``"{\\"phase\\": ...}"``) instead of returning the
    object directly.  The internal contract remains strict: after at most one
    safe unwrap, the payload must still be a JSON object.
    """
    if not content:
        return {}

    decoded: Any = json.loads(content)
    if isinstance(decoded, str):
        decoded = json.loads(decoded)
    if not isinstance(decoded, dict):
        raise ValueError("a resposta estruturada deve ser um objeto JSON")
    return decoded


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
                    )
                log_event("llm_response", model=self.model, attempt=attempt + 1, tool_count=len(getattr(response.choices[0].message, "tool_calls", None) or []))
                break
            except Exception as exc:
                status = getattr(exc, "status_code", None)
                # Some OpenAI-compatible gateways intermittently return an
                # incomplete body that the SDK surfaces as TypeError. Treat
                # that transport/decoding failure like a transient outage;
                # request validation and authentication errors remain
                # non-retryable.
                retryable = status in {429, 500, 502, 503, 504} or exc.__class__.__name__ in {"APIConnectionError", "APITimeoutError", "TypeError"}
                log_event("llm_failure", model=self.model, attempt=attempt + 1, status=status, retryable=retryable)
                if not retryable:
                    raise
                if attempt == self.max_attempts - 1:
                    raise LLMProviderUnavailableError("O provedor LLM está temporariamente indisponível após as tentativas configuradas.") from exc
                time.sleep(self.backoff_seconds * (2 ** attempt))
        try:
            assert response is not None
            choices = getattr(response, "choices", None)
            if not choices:
                raise ValueError("o provedor não retornou nenhuma escolha")
            message = getattr(choices[0], "message", None)
            if message is None:
                raise ValueError("o provedor não retornou uma mensagem do tutor")
            tool_calls = []
            for call in getattr(message, "tool_calls", None) or []:
                function = getattr(call, "function", None)
                if function is None:
                    raise ValueError("a chamada de ferramenta retornada pelo provedor é inválida")
                tool_calls.append({"name": function.name, "arguments": _tool_arguments(function.arguments)})
            content = _content_as_text(message.content)
            # Gemma may include an explicit reasoning block before the answer.
            content = re.sub(r"<thought>.*?</thought>", "", content, flags=re.S).strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I).strip()
            payload = _structured_payload(content) if content else {"phase": "PRACTICE", "tool_calls": tool_calls}
            # Some OpenAI-compatible models use `question` for a learner-facing
            # diagnostic prompt and omit the phase; map that safe equivalent to
            # the internal TutorResponse contract.
            payload.setdefault("phase", "PROBE" if payload.get("question") else "PRACTICE")
            if not payload.get("message") and isinstance(payload.get("question"), str):
                payload["message"] = payload["question"]
            payload["tool_calls"] = tool_calls or payload.get("tool_calls") or []
            if not payload.get("message") and not payload["tool_calls"]:
                payload["phase"] = "PROBE"
                payload["message"] = "Antes de começarmos: qual é sua experiência atual com SQL e com GROUP BY?"
            return TutorResponse.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"Resposta estruturada inválida do LLM: {exc}") from exc

    def assess_sql(self, *, exercise: str, sql: str, result: dict[str, Any], learner_reasoning: str = "") -> SqlAssessment:
        """Assess executable SQL using the real result and exercise context."""
        response = self.complete(
            system_prompt=(
                "Você é um avaliador de SQL. Responda SOMENTE com um objeto JSON "
                "válido, sem markdown, contendo exatamente as chaves phase, "
                "semantics, requirement_satisfaction, reasoning e feedback. "
                "Use phase EVALUATE e valores entre 0 e 1 nos três critérios. "
                "Não confunda execução bem-sucedida com solução correta."
            ),
            learning_state={"phase": "EVALUATE", "exercise": exercise, "submitted_sql": sql, "sql_result": result},
            learner_message=(
                "Avalie esta tentativa usando obrigatoriamente o contexto abaixo.\n"
                f"ENUNCIADO: {exercise}\n"
                f"SQL ESCRITO PELO ALUNO: {sql}\n"
                f"RESULTADO REAL DO POSTGRESQL: {result}\n"
                f"JUSTIFICATIVA DO ALUNO: {learner_reasoning or '(não fornecida)'}"
            ),
            tools=[],
        )
        if response.semantics is None or response.requirement_satisfaction is None or response.reasoning is None:
            raise ValueError("o LLM não retornou os critérios estruturados de avaliação")

        def score(value: float | str) -> float:
            return float(value) if isinstance(value, (int, float)) else 0.5

        textual_reasoning = response.reasoning if isinstance(response.reasoning, str) else None
        return SqlAssessment(
            semantics=score(response.semantics),
            requirement_satisfaction=score(response.requirement_satisfaction),
            reasoning=score(response.reasoning),
            feedback=response.feedback or textual_reasoning or response.message or "Avaliação concluída.",
        )

    def resolve_topic(self, learner_message: str) -> str | None:
        """Classify an unknown learning request into a supported topic."""
        supported = {
            "window_functions", "join", "cte", "null", "recursive",
            "optimization", "subqueries", "aggregation", "deduplication",
            "transactions", "date_functions",
        }
        response = self.complete(
            system_prompt=(
                "Classifique o pedido em JSON TutorResponse. Coloque em "
                "current_concept exatamente um destes valores: "
                + ", ".join(sorted(supported))
                + ". Se nenhum for adequado, use null. Não ensine SQL."
            ),
            learning_state={"phase": "INTENT"},
            learner_message=learner_message,
            tools=[],
        )
        return response.current_concept if response.current_concept in supported else None
