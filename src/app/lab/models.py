from pydantic import BaseModel, Field


class LabDefinition(BaseModel):
    description: str = ""
    ddl: list[str] = Field(default_factory=list)
    seed_sql: list[str] = Field(default_factory=list)


class SqlResult(BaseModel):
    success: bool
    columns: list[str] = Field(default_factory=list)
    rows: list[list[object]] = Field(default_factory=list)
    row_count: int = 0
    error: str | None = None


class LabColumn(BaseModel):
    name: str
    data_type: str
    nullable: bool


class LabTable(BaseModel):
    name: str
    columns: list[LabColumn]
    sample_rows: list[list[object]] = Field(default_factory=list)
    primary_key: list[str] = Field(default_factory=list)
    foreign_keys: list[dict[str, object]] = Field(default_factory=list)
    indexes: list[str] = Field(default_factory=list)


class LabSummary(BaseModel):
    tables: list[LabTable] = Field(default_factory=list)
