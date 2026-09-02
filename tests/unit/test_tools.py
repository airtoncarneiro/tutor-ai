from uuid import uuid4

import pytest

from app.tools.models import ExecuteSqlInput
from app.tools.registry import ToolRegistry


def test_registry_validates_and_dispatches() -> None:
    registry = ToolRegistry()
    registry.register("echo", ExecuteSqlInput, lambda sql: sql)
    assert registry.dispatch("echo", {"sql": "SELECT 1"}) == "SELECT 1"

    with pytest.raises(ValueError, match="Argumentos inválidos"):
        registry.dispatch("echo", {"sql": ""})
    with pytest.raises(KeyError, match="Ferramenta desconhecida"):
        registry.dispatch("missing", {})

