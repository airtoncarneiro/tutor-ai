"""Small, deterministic exercise catalog for the extended SQL scenarios."""

from app.learning.exercises import SqlExercise


def exercises_for(topic: str) -> list[SqlExercise]:
    lowered = topic.casefold()
    if "window" in lowered or "ranking" in lowered or "lag" in lowered:
        return [SqlExercise(
            mode="BUILD",
            concept="window_semantics",
            instruction="Na tabela lab.orders, mostre cada pedido com o nome do cliente, o valor do pedido e a posição do pedido dentro de cada cliente, ordenada do maior para o menor valor.",
            requirement="usar uma função de janela, particionar por customer_id e ordenar por amount DESC",
        )]
    if "subquer" in lowered:
        return [SqlExercise(mode="BUILD", concept="subqueries", instruction="Encontre clientes que possuem ao menos um pedido acima de 100 usando uma subquery.", requirement="filtrar clientes com EXISTS ou IN")]
    if "agreg" in lowered:
        return [SqlExercise(mode="BUILD", concept="advanced_aggregation", instruction="Calcule o total por região e categoria e inclua o total geral.", requirement="usar GROUPING SETS ou uma estratégia equivalente")]
    if "dedup" in lowered or "duplicat" in lowered:
        return [SqlExercise(mode="BUILD", concept="deduplication", instruction="Retorne somente o evento mais recente por cliente e tipo.", requirement="usar ROW_NUMBER ou DISTINCT ON com ordenação temporal")]
    if "transa" in lowered or "commit" in lowered or "rollback" in lowered:
        return [SqlExercise(mode="BUILD", concept="transactions", instruction="Compare o saldo registrado com a soma dos lançamentos por conta.", requirement="usar agregação e identificar divergências sem alterar dados")]
    if "data" in lowered or "date" in lowered or "interval" in lowered:
        return [SqlExercise(mode="BUILD", concept="date_functions", instruction="Agrupe os agendamentos por mês e calcule o intervalo desde o agendamento anterior.", requirement="usar DATE_TRUNC e LAG")]
    return []
