from .models import LabDefinition


def join_lab() -> LabDefinition:
    return LabDefinition(description="JOIN com registros correspondentes e não correspondentes", ddl=["CREATE TABLE customers (id integer primary key, name text not null)", "CREATE TABLE orders (id integer primary key, customer_id integer, total numeric)"] , seed_sql=["INSERT INTO customers VALUES (1, 'Ana'), (2, 'Bia'), (3, 'Caio')", "INSERT INTO orders VALUES (10, 1, 100), (11, 1, 50), (12, 2, 80), (13, 99, 20)"])


def cte_lab() -> LabDefinition:
    return LabDefinition(description="CTE para separar etapas de uma análise", ddl=["CREATE TABLE sales (id integer primary key, region text, total numeric)"] , seed_sql=["INSERT INTO sales VALUES (1, 'Norte', 100), (2, 'Norte', 200), (3, 'Sul', 50)"])


def null_lab() -> LabDefinition:
    return LabDefinition(description="Semântica de NULL", ddl=["CREATE TABLE contacts (id integer primary key, email text)"] , seed_sql=["INSERT INTO contacts VALUES (1, 'ana@example.com'), (2, NULL)"])


def recursive_lab() -> LabDefinition:
    return LabDefinition(description="Hierarquia para CTE recursiva", ddl=["CREATE TABLE org (id integer primary key, parent_id integer, name text)"] , seed_sql=["INSERT INTO org VALUES (1, NULL, 'CEO'), (2, 1, 'Engenharia'), (3, 2, 'Dados')"])


def optimization_lab() -> LabDefinition:
    return LabDefinition(description="Distribuição para exercícios de otimização", ddl=["CREATE TABLE events (id integer primary key, category text, payload text)", "CREATE INDEX events_category_idx ON events(category)"], seed_sql=["INSERT INTO events VALUES (1, 'sql', 'a'), (2, 'python', 'b'), (3, 'sql', 'c')"])
