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
    <img alt="Pytest" src="https://img.shields.io/badge/Tests-pytest-5A63F0?logo=pytest&logoColor=white">
    <br>
    <img alt="OpenTelemetry" src="https://img.shields.io/badge/OpenTelemetry-000000?logo=opentelemetry&logoColor=white">
    <img alt="Grafana" src="https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white">
    <img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white">
    <img alt="Loki" src="https://img.shields.io/badge/Loki-4A90E2?logo=grafana&logoColor=white">
    <img alt="Tempo" src="https://img.shields.io/badge/Tempo-1F60C4?logo=grafana&logoColor=white">
    <img alt="Promtail" src="https://img.shields.io/badge/Promtail-7D64FF?logo=grafana&logoColor=white">
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

#### ETAP II:
- Integrację testów jednostkowych i integracyjnych z rzeczywistą bazą PostgreSQL (Docker)
- Testy integracyjne z izolowaną bazą testową, rollback lub czyszczenie po każdym teście 

#### ETAP III:
- Dodanie drugiej usługi HTTP (**External Service**) i wywołanie jej z głównego API w normalnym przepływie (`/api/v1/external/proxy`).
- Pełna obserwowalność: **OpenTelemetry** (traces/metrics/logs) + **Grafana + Tempo + Loki + Prometheus**.
- **Correlation ID**: generowany dla każdego żądania w `app`, propagowany do `external_service` (nagłówek `X-Correlation-Id`) i zwracany w odpowiedzi; obecny w logach.
- Tracing: spany serwerowe FastAPI i klienckie (Requests) z propagacją kontekstu między usługami.
- Metryki: standardowe HTTP + histogramy opóźnień DB (`db_query_duration_seconds`), licznik błędów zewnętrznej usługi (`ext_service_failures_total`).
- Logi: JSON z polami `timestamp, level, message, trace_id, span_id, correlation_id, http.method, http.route, http.status` wysyłane do **Loki** (Promtail).

<br>

Obsługuje następujące encje:
- **Users** – użytkownicy systemu  
- **Products** – produkty w sklepie  
- **Reviews** – recenzje produktów przez użytkowników  
- **Tags** – tagi produktów  
- **Categories** – kategorie produktów  
- **Orders** – zamówienia złożone przez użytkowników 

<br>

Projekt jest w fazie **rozwojowej** i będzie stopniowo rozbudowywany o kolejne funkcjonalności.

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
- **pytest / unittest / testcontainers** – testy jednostkowe i integracyjne  
- **OpenTelemetry** – śledzenie, metryki i logi  
- **Grafana** – wizualizacja (dashboardy, Explore)  
- **Tempo** – magazyn trace’ów  
- **Loki + Promtail** – zbieranie i przegląd logów  
- **Prometheus** – metryki aplikacji i bazy  
- **postgres_exporter** – metryki PostgreSQL  

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
- API/SWAGGER UI: localhost:8000/docs
- DB: localhost:5432 (user: shop | pass: shop | db: shopdb)
- PGADMIN: localhost:8080 (email: admin@admin.com | pass: admin)
- DB_TEST: localhost:5433 (user: testshop | pass: testshop | db: testshopdb)
- External Service: localhost:8001
- Prometheus: localhost:9090
- Grafana: localhost:3000 (login: admin / hasło: admin — domyślnie)
- Tempo UI/API: localhost:3200
- Loki API: localhost:3100

---

## 🔭 Observability

- Traces: eksport przez OTLP HTTP do `tempo:4318` (Tempo), spany FastAPI (serwer) i Requests (klient).  
- Metrics: `/metrics` w `app` i `external_service` (Prometheus FastAPI Instrumentator); histogramy DB i licznik błędów zewnętrznej usługi.  
- Logs: JSON do stdout + Promtail → Loki; pola korelacyjne (`trace_id`, `span_id`, `correlation_id`) w każdym logu żądania.  
- Grafana: gotowy dashboard „Shop API Observability”.  

#### Szybki start (Grafana → Explore)
- Prometheus: wybierz datasource `Prometheus`, wpisz np. `sum(rate(http_requests_total[5m])) by (code, method)`.
- Loki: wybierz `Loki`, filtruj `{container="app"}` i zawężaj po `correlation_id` lub `level`.
- Tempo: wybierz `Tempo`, filtruj `service.name = "main_api"` lub `"external_service"` i przeglądaj trace’y.

Wskazówka: aby kliknąć z logu do konkretnego trace’a, w Grafana → Data sources → Loki dodaj „Derived field”:  
Name: `trace_id`, Regex: `"trace_id"\s*:\s*"([a-f0-9]{32})"`, Data source: `Tempo`.

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

> © 2025 Shop REST API – Projekt edukacyjny
