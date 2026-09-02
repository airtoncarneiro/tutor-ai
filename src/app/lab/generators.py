from .service import LabService
from .specifications import LabSpecification, window_functions_specification


def generate_window_functions_lab(service: LabService) -> tuple[LabSpecification, object]:
    specification = window_functions_specification()
    summary = service.create_or_replace(specification.definition)
    return specification, summary

