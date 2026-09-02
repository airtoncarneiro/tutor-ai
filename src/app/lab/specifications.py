from pydantic import BaseModel, Field

from .models import LabDefinition


class LabTableSpec(BaseModel):
    name: str
    columns: list[str]


class LabSpecification(BaseModel):
    name: str
    purpose: str
    tables: list[LabTableSpec]
    relationships: list[str] = Field(default_factory=list)
    data_requirements: list[str] = Field(default_factory=list)
    pedagogical_invariants: list[str] = Field(default_factory=list)
    definition: LabDefinition


def window_functions_specification() -> LabSpecification:
    return LabSpecification(
        name="window_functions_ecommerce",
        purpose="Praticar particionamento, ordenação e ranking com Window Functions",
        tables=[
            LabTableSpec(name="customers", columns=["customer_id", "name"]),
            LabTableSpec(name="orders", columns=["order_id", "customer_id", "order_date", "amount"]),
        ],
        relationships=["orders.customer_id → customers.customer_id"],
        data_requirements=["múltiplos pedidos por cliente", "datas ordenáveis", "partições de tamanhos diferentes", "valores empatados"],
        pedagogical_invariants=["ao menos um cliente possui três pedidos", "há valores de amount empatados", "há ao menos dois clientes com quantidades diferentes de pedidos"],
        definition=LabDefinition(
            description="E-commerce para Window Functions",
            ddl=[
                "CREATE TABLE customers (customer_id integer PRIMARY KEY, name text NOT NULL)",
                "CREATE TABLE orders (order_id integer PRIMARY KEY, customer_id integer NOT NULL REFERENCES customers(customer_id), order_date date NOT NULL, amount numeric(10,2) NOT NULL)",
            ],
            seed_sql=["INSERT INTO customers VALUES (1, 'Ana'), (2, 'Bia'), (3, 'Caio')", "INSERT INTO orders VALUES (101, 1, '2026-01-01', 100.00), (102, 1, '2026-01-03', 200.00), (103, 1, '2026-01-05', 200.00), (201, 2, '2026-01-02', 50.00), (202, 2, '2026-01-04', 75.00), (301, 3, '2026-01-02', 300.00)"],
        ),
    )

