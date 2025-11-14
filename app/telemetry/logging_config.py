import json
import logging
from datetime import datetime, timezone

from opentelemetry import trace


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Base fields
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Optional structured fields
        for key in (
            "service",
            "trace_id",
            "span_id",
            "correlation_id",
            "http_method",
            "http_route",
            "http_status",
            "error_type",
        ):
            value = getattr(record, key, None)
            if value is not None:
                log[key] = value

        return json.dumps(log, ensure_ascii=False)


def setup_json_logging(service_name: str) -> None:
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Clear other handlers to avoid duplicate lines
    root.handlers = [handler]

    # Attach service name via LoggerAdapter-like pattern
    class ServiceFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "service"):
                record.service = service_name
            return True

    class TraceContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            # Do not overwrite explicit values set via `extra`
            has_trace = getattr(record, "trace_id", None)
            has_span = getattr(record, "span_id", None)
            if has_trace and has_span:
                return True

            span = trace.get_current_span()
            ctx = span.get_span_context() if span else None
            if ctx and ctx.is_valid:
                if not has_trace:
                    record.trace_id = format(ctx.trace_id, "032x")
                if not has_span:
                    record.span_id = format(ctx.span_id, "016x")
            return True

    root.addFilter(ServiceFilter())
    root.addFilter(TraceContextFilter())

