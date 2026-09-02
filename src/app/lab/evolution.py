from pydantic import BaseModel, Field

from .models import LabSummary
from .service import LabService


class LabExtensionRequest(BaseModel):
    reason: str = Field(min_length=1)
    required_tables: list[str] = Field(default_factory=list)
    ddl: list[str] = Field(default_factory=list)
    dml: list[str] = Field(default_factory=list)


class LabEvolutionService:
    def __init__(self, lab: LabService) -> None:
        self.lab = lab

    def needs_extension(self, required_tables: list[str]) -> bool:
        existing = {table.name for table in self.lab.inspect().tables}
        return any(table not in existing for table in required_tables)

    def extend(self, request: LabExtensionRequest) -> LabSummary:
        if not self.needs_extension(request.required_tables):
            raise ValueError("A extensão solicitada não é necessária para as tabelas informadas")
        return self.lab.extend(request.ddl, request.dml)

