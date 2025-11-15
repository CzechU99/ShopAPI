# 📡 ETAP III – Observability (Grafana, Prometheus, Loki, Tempo)

Projekt został rozszerzony o pełny zestaw narzędzi obserwowalności:

## 🔍 Stack Monitorujący:
- **Prometheus** – metryki aplikacji i bazy danych  
- **Grafana** – dashboardy analityczne  
- **Loki** – centralizacja logów  
- **Tempo** – distributed tracing (OpenTelemetry)  
- **postgres_exporter** – metryki PostgreSQL  

## 🧩 Co zostało dodane
- Instrumentacja aplikacji FastAPI (OTel SDK – spans + metryki HTTP)
- Korelacja:
  - `correlation_id` → logi Loki
  - `trace_id` → Tempo trace
  - logi ↔ trace ↔ metryki
- Logi strukturalne JSON dla `main_api` i `external_service`

---

# 📈 ETAP IV – Load Testing (Lab 4 – Grafana k6)

Celem etapu było wykonanie serii testów obciążeniowych badających:

1. Opóźnienia po stronie usługi zewnętrznej  
2. Timeouty klienta HTTP  
3. Presję na pulę połączeń (max_connections + pool_timeout)  
4. Keep-alive i jego wpływ na reuse połączeń  
5. HTTP/1.1 vs HTTP/2  
6. Wolną bazę danych (spowolniona konfiguracją + dużymi danymi)  

Testy były wykonywane poprzez **Grafana k6 z Prometheus Remote Write**, aby pojawiały się w Grafanie jako serie metryk `k6_*`.

## 🚀 Uruchamianie testów
Przykład:
```bash
export K6_PROMETHEUS_RW_SERVER_URL="http://localhost:9090/api/v1/write"
export K6_TEST_ID="lab4-$(date +%s)"

K6_CASE="maxconn-100-pool-100ms" \
K6_RATE=20 \
K6_DURATION=60s \
k6 run -o experimental-prometheus-rw tests/k6/lab4.js
```

## 🔎 Analiza wyników
Analiza obejmowała:
- `k6_http_req_duration{p95,p99}`  
- `k6_http_req_failed`  
- Tempo traces  
- Logi Loki z korelacją `correlation_id`  
- postgres_exporter:
  - `pg_stat_activity_count`
  - `blks_read_total`
  - `buffers_hit_ratio`

## 🗂️ Wyniki i screeny
Wszystkie dashboardy, wykresy i logi zostały zebrane w:
```
docs/load-tests/
```

## 📝 Raport końcowy
Pełny raport znajduje się w:
```
docs/load-tests/REPORT.md
```
