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
    return LabDefinition(description="Distribuição para exercícios de otimização de consultas", ddl=["CREATE TABLE events (id integer primary key, category text, payload text)", "CREATE TABLE event_batches (batch_id integer primary key, category text, event_count integer not null)"], seed_sql=["INSERT INTO events VALUES (1, 'sql', 'a'), (2, 'python', 'b'), (3, 'sql', 'c'), (4, 'sql', 'd'), (5, 'data', 'e')", "INSERT INTO event_batches VALUES (1, 'sql', 3), (2, 'python', 1), (3, 'data', 1)"])


def subquery_lab() -> LabDefinition:
    return LabDefinition(description="Subqueries escalares, correlacionadas e com EXISTS", ddl=["CREATE TABLE customers (id integer primary key, name text not null)", "CREATE TABLE orders (id integer primary key, customer_id integer not null, total numeric not null)"], seed_sql=["INSERT INTO customers VALUES (1, 'Ana'), (2, 'Bia'), (3, 'Caio')", "INSERT INTO orders VALUES (10, 1, 100), (11, 1, 200), (12, 2, 80)"])


def advanced_aggregation_lab() -> LabDefinition:
    return LabDefinition(description="Agregações avançadas com FILTER e GROUPING SETS", ddl=["CREATE TABLE sales (id integer primary key, region text not null, category text not null, total numeric not null)"], seed_sql=["INSERT INTO sales VALUES (1, 'Norte', 'livros', 100), (2, 'Norte', 'cursos', 200), (3, 'Norte', 'livros', 50), (4, 'Sul', 'livros', 80), (5, 'Sul', 'cursos', 120), (6, 'Leste', 'cursos', 90)"])


def deduplication_lab() -> LabDefinition:
    return LabDefinition(description="Deduplicação por chave natural e data de ingestão", ddl=["CREATE TABLE customer_events (id integer primary key, customer_id integer not null, event_type text not null, occurred_at timestamptz not null, payload text)"], seed_sql=["INSERT INTO customer_events VALUES (1, 10, 'email', '2026-01-01 09:00+00', 'old'), (2, 10, 'email', '2026-01-01 10:00+00', 'new'), (3, 20, 'purchase', '2026-01-02 09:00+00', 'only'), (4, 20, 'purchase', '2026-01-02 09:05+00', 'retry')"])


def transactions_lab() -> LabDefinition:
    return LabDefinition(description="Transações: saldos, lançamentos e consistência", ddl=["CREATE TABLE accounts (account_id integer primary key, owner text not null, balance numeric(10,2) not null)", "CREATE TABLE ledger (entry_id integer primary key, account_id integer not null, amount numeric(10,2) not null, occurred_at timestamptz not null)"], seed_sql=["INSERT INTO accounts VALUES (1, 'Ana', 1000), (2, 'Bia', 500)", "INSERT INTO ledger VALUES (1, 1, 1000, '2026-01-01 09:00+00'), (2, 1, -100, '2026-01-02 09:00+00'), (3, 2, 500, '2026-01-01 09:00+00')"])


def date_functions_lab() -> LabDefinition:
    return LabDefinition(description="Funções de data, períodos e intervalos", ddl=["CREATE TABLE appointments (id integer primary key, customer_id integer not null, scheduled_at timestamptz not null, status text not null)"], seed_sql=["INSERT INTO appointments VALUES (1, 10, '2026-01-05 10:00+00', 'done'), (2, 10, '2026-01-20 11:30+00', 'cancelled'), (3, 20, '2026-02-03 09:00+00', 'done'), (4, 20, '2026-03-12 15:00+00', 'done'), (5, 30, '2026-03-30 16:00+00', 'scheduled')"])
