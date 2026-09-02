from app.lab.models import LabDefinition
from app.lab.service import LabService
from .models import CreateLabInput, ExecuteSqlInput, ExtendLabInput
from .registry import ToolRegistry


def register_lab_tools(registry: ToolRegistry, service: LabService) -> None:
    registry.register("create_lab", CreateLabInput, lambda **kwargs: service.create_or_replace(LabDefinition(**kwargs)).model_dump(mode="json"))
    registry.register("execute_sql", ExecuteSqlInput, lambda **kwargs: service.execute(kwargs["sql"]).model_dump(mode="json"))
    registry.register("inspect_lab", __import__("app.tools.models", fromlist=["InspectLabInput"]).InspectLabInput, lambda **_: service.inspect().model_dump(mode="json"))
    registry.register("extend_lab", ExtendLabInput, lambda **kwargs: service.extend(**kwargs).model_dump(mode="json"))
    registry.register("reset_lab", __import__("app.tools.models", fromlist=["ResetLabInput"]).ResetLabInput, lambda **_: service.reset().model_dump(mode="json"))

