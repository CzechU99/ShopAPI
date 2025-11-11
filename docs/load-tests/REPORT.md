# Lab 4 – Load Testing Report

> Replace the placeholder notes below with your real observations once you finish running k6 and collecting Grafana evidence.

## 1. External Service Delay Baseline
- **Config:** External delay range = 30–120s, Main API default HTTP/2 client.
- **Observation notes:** _p50/p95 latency, total throughput, any saturation seen in Prometheus histograms_
- **Interesting trace/log links:** _Loki query, Tempo trace ID_

## 2. Client Timeouts Raised to 180s
- **Config tweak:** `EXT_CLIENT_READ_TIMEOUT=180` (already default) with short connect/write timeouts.
- **Results:** _Did slow calls complete? Was error rate ≈0? Capture k6 latency panels._

## 3. Connection Pressure (max connections & pool timeout)
Document at least three runs, e.g. `case="maxconn-10-pool-0ms"`, `case="maxconn-100-pool-100ms"`, `case="maxconn-200-pool-1s"`.
- **Breaking point:** _Which combination produced connection errors first?_
- **Evidence:** _Screenshots list_

## 4. Keep-Alive Pool Tuning
Pick a fixed `EXT_CLIENT_MAX_CONNECTIONS` and vary `EXT_CLIENT_MAX_KEEPALIVE_CONNECTIONS`.
- **Compare:** _Latency deltas, reuse observed in Tempo spans_

## 5. HTTP/1.1 vs HTTP/2
- **Config:** toggle `EXT_CLIENT_HTTP2_ENABLED=true/false`.
- **Notes:** _Mention head-of-line blocking/parallelism differences._

## 6. Intentionally Slow PostgreSQL
- **Technique used:** _e.g., `shared_buffers=16MB`, `synchronous_commit=on`, `fsync=on` + `pg_sleep` trigger_.
- **Effect:** _How much slower did `/api/v1/external/proxy` become once DB queries stalled?_

## PromQL Cheat Sheet
Use/cite the PromQL expressions that helped you analyze runs:
- `histogram_quantile(0.95, sum(rate(k6_http_req_duration_seconds_bucket{testid="$testid"}[5m])) by (le))`
- `sum(rate(k6_http_reqs_total{testid="$testid", status!~"2.."}[1m]))`
- `sum(rate(http_server_duration_seconds_bucket{le="+Inf", service="main_api"}[5m])) by (status)`

Add more queries here as needed.
