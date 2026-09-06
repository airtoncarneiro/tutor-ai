from .service import LabService
from collections.abc import Callable

from .models import LabDefinition
from .scenarios import (advanced_aggregation_lab, cte_lab, date_functions_lab,
                        deduplication_lab, join_lab, null_lab, optimization_lab,
                        recursive_lab, subquery_lab, transactions_lab)
from .specifications import LabSpecification, window_functions_specification


def generate_window_functions_lab(service: LabService) -> tuple[LabSpecification, object]:
    specification = window_functions_specification()
    summary = service.create_or_replace(specification.definition)
    return specification, summary


SCENARIO_GENERATORS: dict[str, Callable[[], LabDefinition]] = {
    "join": join_lab,
    "cte": cte_lab,
    "null": null_lab,
    "recursive": recursive_lab,
    "optimization": optimization_lab,
    "subqueries": subquery_lab,
    "aggregation": advanced_aggregation_lab,
    "deduplication": deduplication_lab,
    "transactions": transactions_lab,
    "date_functions": date_functions_lab,
}


def scenario_key(topic: str) -> str:
    lowered = topic.casefold()
    if "window" in lowered or "ranking" in lowered or "lag" in lowered:
        return "window_functions"
    if "recurs" in lowered:
        return "recursive"
    aliases = {
        "subqueries": ("subquer", "subconsulta"),
        # "agreg" also accepts common inflected forms and the typo
        # "agregração" entered in the GUI.
        "aggregation": ("agreg", "group by", "groupby", "grouping sets", "filter"),
        "deduplication": ("dedup", "duplicat"),
        "transactions": ("transa", "commit", "rollback"),
        "date_functions": ("data", "date_trunc", "interval"),
    }
    for key, terms in aliases.items():
        if any(term in lowered for term in terms):
            return key
    for key in SCENARIO_GENERATORS:
        if key in lowered or (key == "null" and "nulo" in lowered) or (key == "optimization" and any(term in lowered for term in ("performance", "otimiza", "otimiz"))):
            return key
    raise ValueError(f"Nenhum cenário SQL disponível para: {topic}")


def generate_topic_lab(topic: str, service: LabService) -> tuple[LabDefinition | LabSpecification, object]:
    key = scenario_key(topic)
    if key == "window_functions":
        return generate_window_functions_lab(service)
    definition = SCENARIO_GENERATORS[key]()
    return definition, service.create_or_replace(definition)
