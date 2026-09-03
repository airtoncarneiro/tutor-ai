from app.lab.models import LabDefinition
from app.lab.service import LabService
from .models import CreateLabInput, ExecuteSqlInput, ExtendLabInput
from .registry import ToolRegistry


def register_lab_tools(registry: ToolRegistry, service: LabService) -> None:
    def create(**kwargs):
        try:
            return {"success": True, "lab": service.create_or_replace(LabDefinition(**kwargs)).model_dump(mode="json")}
        except Exception as exc:
            return {"success": False, "retryable": True, "error": str(exc)}

    registry.register("create_lab", CreateLabInput, create)
    registry.register("execute_sql", ExecuteSqlInput, lambda **kwargs: service.execute(kwargs["sql"]).model_dump(mode="json"))
    registry.register("inspect_lab", __import__("app.tools.models", fromlist=["InspectLabInput"]).InspectLabInput, lambda **_: service.inspect().model_dump(mode="json"))
    def extend(**kwargs):
        try:
            return {"success": True, "lab": service.extend(**kwargs).model_dump(mode="json")}
        except Exception as exc:
            return {"success": False, "retryable": True, "error": str(exc)}

    registry.register("extend_lab", ExtendLabInput, extend)
    registry.register("reset_lab", __import__("app.tools.models", fromlist=["ResetLabInput"]).ResetLabInput, lambda **_: service.reset().model_dump(mode="json"))
