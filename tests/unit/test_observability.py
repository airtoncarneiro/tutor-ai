import logging
from app.observability import CorrelationFilter, correlation_id, redact


def test_log_filter_redacts_secrets():
    token = correlation_id.set("test-correlation")
    try:
        record = logging.LogRecord("x", logging.INFO, "", 1, "api_key=secret", (), None)
        CorrelationFilter().filter(record)
        assert "secret" not in record.msg and record.correlation_id == "test-correlation"
    finally:
        correlation_id.reset(token)


def test_redact_handles_json_style_secrets():
    safe = redact({"api_key": "secret", "nested": {"token": "abc", "value": "ok"}})
    assert safe == {"api_key": "<redacted>", "nested": {"token": "<redacted>", "value": "ok"}}
