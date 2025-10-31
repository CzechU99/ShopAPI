import time
from prometheus_client import Histogram
from sqlalchemy import event


DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Latency of DB cursor executions",
    ["statement"],
)


def setup_db_metrics(engine):
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, params, context, executemany):
        context._query_start_time = time.perf_counter()
        context._statement_label = (statement or "").split()[0][:32] or "unknown"

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, params, context, executemany):
        start = getattr(context, "_query_start_time", None)
        label = getattr(context, "_statement_label", "unknown")
        if start is not None:
            DB_QUERY_DURATION.labels(statement=label).observe(time.perf_counter() - start)

