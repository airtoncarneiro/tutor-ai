import logging
import re
from contextvars import ContextVar
from uuid import UUID, uuid4

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")
_SECRET = re.compile(r"(api[_-]?key|password|token)=([^\s,}]+)", re.I)


def start_correlation() -> str:
    value = str(uuid4())
    correlation_id.set(value)
    return value


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get()
        record.msg = _SECRET.sub(r"\1=<redacted>", str(record.msg))
        return True


logger = logging.getLogger("adaptive_sql_tutor")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.addFilter(CorrelationFilter())
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s correlation_id=%(correlation_id)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
