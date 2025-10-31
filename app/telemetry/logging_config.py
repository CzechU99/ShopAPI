import json
import logging
from datetime import datetime, timezone


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

    root.addFilter(ServiceFilter())

