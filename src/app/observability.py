import logging
import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from time import perf_counter
from typing import Any, Iterator
from uuid import UUID, uuid4

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")
_SECRET = re.compile(r"((?:api[_-]?key|password|token|authorization)[\"']?\s*[:=]\s*[\"']?)([^\s,}\"']+)", re.I)


def start_correlation() -> str:
    value = str(uuid4())
    correlation_id.set(value)
    return value


def redact(value: Any) -> Any:
    """Remove credentials and avoid logging complete learner payloads."""
    if isinstance(value, dict):
        return {
            key: "<redacted>" if re.search(r"api[_-]?key|password|token|authorization", key, re.I)
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _SECRET.sub(r"\1<redacted>", value)
    return value


def log_event(event: str, **fields: Any) -> None:
    """Emit compact structured telemetry without secrets or full user text."""
    safe = redact(fields)
    logger.info("event=%s fields=%s", event, json.dumps(safe, ensure_ascii=False, default=str))


@contextmanager
def timed_event(event: str, **fields: Any) -> Iterator[None]:
    started = perf_counter()
    try:
        yield
    finally:
        log_event(event, duration_ms=round((perf_counter() - started) * 1000, 2), **fields)


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get()
        record.msg = _SECRET.sub(r"\1<redacted>", str(record.msg))
        return True


logger = logging.getLogger("adaptive_sql_tutor")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.addFilter(CorrelationFilter())
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s correlation_id=%(correlation_id)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
