# Lab 5 – Messaging Scenarios vs Baseline

| Scenario | Broker | Max RPS | p50 Latency | p95 Latency | p99 Latency |
| --- | --- | --- | --- | --- | --- |
| Baseline (Lab 4) | none | _TBD_ | _TBD_ ms | _TBD_ ms | _TBD_ ms |
| Async Upstream (A) | Kafka | _TBD_ | _TBD_ ms | _TBD_ ms | _TBD_ ms |
| Async Upstream (A) | RabbitMQ | _TBD_ | _TBD_ ms | _TBD_ ms | _TBD_ ms |
| Async Downstream (B) | Kafka | _TBD_ | _TBD_ ms | _TBD_ ms | _TBD_ ms |
| Async Downstream (B) | RabbitMQ | _TBD_ | _TBD_ ms | _TBD_ ms | _TBD_ ms |

Update the table with real measurements after running the five required k6 scenarios (baseline + 2 brokers × 2 messaging patterns). Capture the metrics from the Grafana k6 dashboard or directly from the Prometheus RW feed.

### Quick interpretation template

- **Highest RPS:** _fill after tests_  
- **Latency observations:** Describe how async upstream vs downstream compare to the baseline, and note differences between Kafka and RabbitMQ (e.g., queueing overhead, worker throughput).  
- **Worker impact:** Mention any differences observed in worker traces/logs/metrics (Tempo + Loki screenshots should highlight correlation IDs across API and worker).
