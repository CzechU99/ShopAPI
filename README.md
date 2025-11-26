<h2 align="center"><strong>Shop REST API (N-Tier)</strong></h2>

<div align="center">
  <p>
    <img alt="Status" src="https://img.shields.io/badge/status-in%20development-orange">
    <img alt="License" src="https://img.shields.io/badge/license-private-lightgrey">
  </p>
  <p>
    <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white">
    <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white">
    <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-FF0000?logo=sqlalchemy&logoColor=white">
    <img alt="Alembic" src="https://img.shields.io/badge/Alembic-003366?logoColor=white">
    <img alt="Swagger" src="https://img.shields.io/badge/Swagger-85EA2D?logo=swagger&logoColor=black">
    <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white">
    <img alt="Postman" src="https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white">
    <img alt="Pytest" src="https://img.shields.io/badge/Tests-Pytest-5A63F0?logo=pytest&logoColor=white">
    </br>
    <img alt="OpenTelemetry" src="https://img.shields.io/badge/OpenTelemetry-000000?logo=opentelemetry&logoColor=white">
    <img alt="Load Testing" src="https://img.shields.io/badge/Load_Testing-black?logo=speedtest&logoColor=white">
    <img alt="Grafana" src="https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white">
    <img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white">
    <img alt="Loki" src="https://img.shields.io/badge/Loki-4A90E2?logo=grafana&logoColor=white">
    <img alt="Tempo" src="https://img.shields.io/badge/Tempo-1F60C4?logo=grafana&logoColor=white">
    <img alt="k6" src="https://img.shields.io/badge/Grafana k6-7D64FF?logo=k6&logoColor=white">
  </p>
</div>

---

## 🎯 Cel projektu

Projekt jest produkcjonopodobnym **REST API sklepu internetowego** w architekturze N-tier, który umożliwia pracę z relacyjną bazą danych PostgreSQL. Projekt ma na celu:

#### ETAP I:
- Zaprojektowanie relacyjnego modelu danych z co najmniej **5 tabelami**, obejmującymi:
  - ≥ 2 relacje jeden-do-wielu  
  - ≥ 1 relację wiele-do-wielu (z tabelą pośrednią)  
  - klucze główne i obce z zachowaniem ON DELETE  
  - unikalne i wymagane pola, ograniczenia CHECK  
  - indeksy dla często wyszukiwanych pól  
- Implementację **N-tier API** (API/Presentation → Service/Business → Data Access/Repository → Database)  
- Umożliwienie **CRUD** dla przynajmniej 3 encji i odczytu dla pozostałych  
- Walidację danych wejściowych i obsługę błędów HTTP  
- Wersjonowanie API (np. `/api/v1/...`)  

Obsługuje następujące encje:
- **Users** – użytkownicy systemu  
- **Products** – produkty w sklepie  
- **Reviews** – recenzje produktów przez użytkowników  
- **Tags** – tagi produktów  
- **Categories** – kategorie produktów  
- **Orders** – zamówienia złożone przez użytkowników 

<br>

#### ETAP II:
- Integrację testów jednostkowych i integracyjnych z rzeczywistą bazą PostgreSQL (Docker)
- Testy integracyjne z izolowaną bazą testową, rollback lub czyszczenie po każdym teście 

<br>

#### ETAP III:
- Dodanie drugiej usługi HTTP (**External Service**) i wywołanie jej z głównego API w normalnym przepływie (`/api/v1/external/proxy`).
- Pełna obserwowalność **OpenTelemetry** (traces/metrics/logs) + **Grafana + Tempo + Loki + Prometheus**.
- **Correlation ID** generowany dla każdego żądania w `app`, propagowany do `external_service` i zwracany w odpowiedzi.
- Spany serwerowe FastAPI i klienckie (Requests) z propagacją kontekstu między usługami.
- Standardowe HTTP + histogramy opóźnień DB (`db_query_duration_seconds`), licznik błędów zewnętrznej usługi (`ext_service_failures_total`).
- JSON z polami `timestamp, level, message, trace_id, span_id, correlation_id, http.method, http.route, http.status` wysyłane do **Loki** (Promtail).

<br>

#### ETAP IV:
Celem etapu było wykonanie serii testów obciążeniowych badających:
- Opóźnienia po stronie usługi zewnętrznej  
- Timeouty klienta HTTP  
- Presję na pulę połączeń (max_connections + pool_timeout)  
- Keep-alive i jego wpływ na reuse połączeń  
- HTTP/1.1 vs HTTP/2  
- Wolną bazę danych (spowolniona konfiguracją + dużymi danymi)  

Testy wykonywane poprzez **Grafana k6 z Prometheus Remote Write**, aby pojawiały się w Grafanie jako serie metryk `k6_*`.

---

## 🧱 Technologie

- **Python 3.11+** – backend  
- **FastAPI** – framework REST API  
- **SQLAlchemy** – ORM do PostgreSQL  
- **Alembic** – migracje schematu bazy danych  
- **PostgreSQL** – relacyjna baza danych  
- **Swagger UI** – dokumentacja i testowanie API  
- **Postman** – testy i kolekcje API  
- **Docker** – konteneryzacja aplikacji i bazy danych  
- **Pytest / Unittest / Testcontainers** – testy jednostkowe i integracyjne  
- **OpenTelemetry** – śledzenie, metryki i logi  
- **Grafana** – wizualizacja (dashboardy, Explore)  
- **Tempo** – magazyn trace’ów  
- **Loki + Promtail** – zbieranie i przegląd logów  
- **Prometheus** – metryki aplikacji i bazy  
- **Postgres_exporter** – metryki PostgreSQL  

---

## ⚙️ Uruchomienie

a) Skopiuj repozytorium i przejdź do katalogu:
   ```bash
   cd ShopAPI
   ```

b) Uruchom:
   ```bash
   docker compose up --build
   ```

c) W kontenerze `app`, aby wgrać migrację bazy danych:
   ```bash
   docker compose exec app alembic upgrade head
   ```

<br>

Po chwili:
- MAIN API: localhost:8000
- SWAGGER UI: localhost:8000/docs
- DATABASE: localhost:5432 (user: shop | pass: shop | db: shopdb)
- POSTGRESQL ADMIN: localhost:8080 (email: admin@admin.com | pass: admin)
- DB_TEST: localhost:5433 (user: testshop | pass: testshop | db: testshopdb)
- EXTERNAL API: localhost:8001
- PROMETHEUS: localhost:9090
- GRAFANA: localhost:3000 (login: admin / hasło: admin)
- TEMPO: localhost:3200
- LOKI API: localhost:3100

---

## 🧪 Testy

- Testy jednostkowe sprawdzają logikę serwisów z mockowanymi repozytoriami.
- Testy integracyjne uruchamiają się na kontenerze PostgreSQL testowym (db_test) i:
  - wykonują rzeczywiste zapytania SQL
  - używają transakcji i rollback po każdym teście lub czyszczą dane
  - są idempotentne i niezależne od kolejności uruchamiania
- Weryfikują m.in.:
  - tworzenie i pobieranie użytkowników
  - CRUD produktów i zamówień
  - poprawne przeliczanie kwot zamówień
  - zachowanie ograniczeń bazy danych

<br>

Przykład uruchomienia testów:

a) Pamiętaj o uruchomieniu kontenera z bazą danych do testów `db_test`

b) Wykonanie testów za pomocą polecenia:
```env
docker compose exec app pytest -v
```

---

## 🔭 Observability

- Traces: eksport przez OTLP HTTP do `tempo:4318` (Tempo), spany FastAPI (serwer) i Requests (klient).  
- Metrics: `/metrics` w `app` i `external_service` (Prometheus FastAPI Instrumentator); histogramy DB i licznik błędów zewnętrznej usługi.  
- Logs: JSON + Promtail → Loki; pola korelacyjne (`trace_id`, `span_id`, `correlation_id`) w każdym logu żądania.  
- Grafana: gotowy dashboard „Shop API Observability”.

<br>

#### Grafana → Explore/Dashboard
- ID gotowych dashboard'ów do importu: PROMETHEUS:18030 | POSTGRES_EXPORTER:9628
- Prometheus: wybierz datasource `Prometheus`, wpisz np. `sum(rate(http_requests_total))`.
- Loki: wybierz `Loki`, filtruj `{container="shop-app-1"}` i zawężaj po `correlation_id` lub `level`.
- Tempo: wybierz `Tempo`, filtruj `service.name = "main_api"` lub `"external_service"` i przeglądaj trace’y.

---

## 📈 Load Testing (Grafana K6)

#### 🌐 Konfigruacja klienta HTTP:

| Zmienna | Opis | Domyślna wartość |
| --- | --- | --- |
| `EXT_CLIENT_READ_TIMEOUT` | Timeout na odczyt/odpowiedź (w sekundach) | `180` |
| `EXT_CLIENT_CONNECT_TIMEOUT` | Timeout na ustanowienie połączenia TCP | `2` |
| `EXT_CLIENT_WRITE_TIMEOUT` | Timeout na wysłanie danych (body upload) | `5` |
| `EXT_CLIENT_POOL_TIMEOUT` | Maksymalny czas oczekiwania na wolne połączenie z puli (s) | `0.05` |
| `EXT_CLIENT_MAX_CONNECTIONS` | Maksymalna liczba jednoczesnych połączeń HTTP (httpx) | `100` |
| `EXT_CLIENT_MAX_KEEPALIVE_CONNECTIONS` | Rozmiar puli keep-alive | `20` |
| `EXT_CLIENT_KEEPALIVE_EXPIRY` | Maksymalny czas bezczynności połączenia keep-alive (s) | `5` |
| `EXT_CLIENT_HTTP2_ENABLED` | Włączenie/wyłączenie HTTP/2 (`true` / `false`) | `true` |

<br>

#### 🚀 Uruchamianie testów:
```bash
export K6_PROMETHEUS_RW_SERVER_URL="http://localhost:9090/api/v1/write"
export K6_PROMETHEUS_RW_TREND_STATS="p(95),p(99),min,max"
export K6_PROMETHEUS_RW_TREND_AS_NATIVE_HISTOGRAM="true"   

K6_CASE="case_name" k6 run -o experimental-prometheus-rw --tag testid="test_id_name" tests/k6/lab4.js
```
<br>

#### 🔎 Analiza wyników:
- `k6_http_req_duration{p95,p99}`  
- `k6_http_req_failed`  
- Tempo traces  
- Logi Loki z korelacją `correlation_id`  
- postgres_exporter:
  - `pg_stat_activity_count`
  - `blks_read_total`
  - `buffers_hit_ratio`

<br>

#### 🗂️ Wyniki i screeny:
Wszystkie dashboardy, wykresy i logi zostały zebrane w:
```bash
docs/load-tests/
```

<br>

#### 📝 Raport końcowy:
Pełny raport znajduje się w:
```
docs/load-tests/REPORT.md
```

---

## 📨 Lab 5 – Async Messaging Scenarios

Lab 5 rozszerza architekturę z Lab 4 o dwa warianty komunikacji asynchronicznej:

- **Scenario A / Async Upstream:** API tylko wrzuca komunikat do kolejki (Kafka lub RabbitMQ) i natychmiast zwraca `202 Accepted`. Worker pobiera wiadomość, wywołuje External API i zapisuje wynik w Postgresie.
- **Scenario B / Async Downstream:** API nadal wykonuje połączenie HTTP do External API, ale zapis do bazy zleca poprzez kolejkę i worker.

### Nowe komponenty

- **Kafka + Zookeeper** – Bitnami images (`kafka:9092`), dwa topiki: `external_async_upstream`, `external_async_downstream`.
- **RabbitMQ** – obraz `rabbitmq:3-management` (`5672`, `15672` UI), dwie kolejki o analogicznych nazwach.
- **Worker (`worker/main.py`)** – współdzielony kod z aplikacją (SQLAlchemy + `ExternalResultService`). Uruchamiany z parametrami:
  - `MESSAGE_BROKER={kafka|rabbitmq}`
  - `JOB_SCENARIO={async_upstream|async_downstream}`
- **External API bez sztucznego `sleep`** – serwis `external_service` pobiera teraz dane z publicznego API (`jsonplaceholder.typicode.com`) i zwraca realny czas pobrania w polu `remote_delay_ms`.

Domyślna definicja w `docker-compose.yml` (profil `worker`) odpala worker w trybie `kafka + async_upstream`. Przykłady:

```bash
# Worker dla scenariusza A na Kafka
docker compose --profile worker up worker

# Worker dla scenariusza B na RabbitMQ
MESSAGE_BROKER=rabbitmq JOB_SCENARIO=async_downstream \
  docker compose run --rm worker python worker/main.py
```

### API endpoints

| Endpoint | Opis |
| --- | --- |
| `GET /api/v1/external/proxy` | Baseline z Lab 4 (bez MQ). |
| `POST /api/v1/external/fetch/async-upstream?broker={kafka|rabbitmq}` | Scenario A – zwraca `202` z `correlation_id`. |
| `POST /api/v1/external/fetch/async-downstream?broker={kafka|rabbitmq}` | Scenario B – odpowiedź zawiera wynik External API, zapis do DB dzieje się asynchronicznie. |

Każda ścieżka propaguje `X-Correlation-Id`, tagi scenariusza oraz dane do Prometheusa/Loki/Tempo.

### k6 – nowe skrypty

Plik `tests/k6/lab5.js` przyjmuje zmienne środowiskowe:

```bash
K6_SCENARIO=async_upstream \
K6_BROKER=kafka \
K6_CASE="lab5-upstream-kafka" \
k6 run -o experimental-prometheus-rw tests/k6/lab5.js
```

Obsługiwane scenariusze: `baseline`, `async_upstream`, `async_downstream`. Dla wariantów asynchronicznych ustaw `K6_BROKER` na `kafka` lub `rabbitmq`.

### Dokumentacja i artefakty

- `docs/messaging-load-tests/RESULTS.md` – tabela porównawcza (RPS, p50/p95/p99) dla 5 biegów: baseline, A/B z Kafka i RabbitMQ.
- `docs/messaging-load-tests/*.png` – zrzuty z Grafany (k6 dashboard) oraz para Loki+Tempo z korelacją `correlation_id`.
- README (ten rozdział) opisuje też jak przełączać brokera i scenariusze.

Po uruchomieniu testów uzupełnij tabelę wyników oraz dodaj screeny zgodnie z wymaganiami labu.

---

> © 2025 Shop REST API – Projekt edukacyjny
