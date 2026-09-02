from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[type[BaseModel], Callable[..., Any]]] = {}

    def register(self, name: str, input_model: type[BaseModel], handler: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError(f"Ferramenta já registrada: {name}")
        self._tools[name] = (input_model, handler)

    def dispatch(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise KeyError(f"Ferramenta desconhecida: {name}")
        model, handler = self._tools[name]
        try:
            validated = model.model_validate(arguments)
        except ValidationError as exc:
            raise ValueError(f"Argumentos inválidos para {name}: {exc}") from exc
        return handler(**validated.model_dump())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def definitions(self) -> list[dict[str, Any]]:
        return [{"type": "function", "function": {"name": name, "description": f"Executa a ferramenta {name}", "parameters": model.model_json_schema()}} for name, (model, _) in self._tools.items()]
