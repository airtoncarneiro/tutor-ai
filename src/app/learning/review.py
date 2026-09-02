from pydantic import BaseModel, Field


class ApplyProblem(BaseModel):
    title: str
    context: str
    requirements: list[str] = Field(min_length=1)
    concepts: list[str] = Field(min_length=1)
    stages: list[str] = ["ANALYZE", "PROPOSE", "JUSTIFY", "IMPLEMENT", "EXECUTE", "VALIDATE", "CRITIQUE"]
    solution: str | None = None


class TransferTest(BaseModel):
    title: str
    context: str
    requirements: list[str] = Field(min_length=1)
    concepts: list[str] = Field(min_length=1)
    reference_context: str


class ReviewService:
    def review_concepts(self, concepts: list[dict]) -> list[dict]:
        return sorted(concepts, key=lambda concept: concept.get("mastery", 0))

    def create_apply_problem(self, topic: str) -> ApplyProblem:
        return ApplyProblem(title=f"Análise multi-conceito: {topic}", context="Uma loja precisa analisar o comportamento de compra de seus clientes.", requirements=["calcule uma métrica por cliente", "compare cada registro com seu grupo", "justifique a ordenação"], concepts=["aggregation", "partition-by", "ordering"])

    def create_transfer_test(self, problem: ApplyProblem) -> TransferTest:
        return TransferTest(title="Transferência: operações logísticas", context="Uma operação logística analisa entregas por centro e por data.", requirements=["calcule a posição de cada entrega no centro", "identifique a entrega anterior", "explique o resultado"], concepts=problem.concepts, reference_context=problem.context)

