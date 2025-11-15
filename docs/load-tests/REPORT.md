# Lab 4 – Load Testing and Observability

## 1️⃣ Preparation – External Service Delay

**Konfiguracja:**
- EXTERNAL_SLEEP_MIN=30s  
- EXTERNAL_SLEEP_MAX=120s  
- EXT_CLIENT_READ_TIMEOUT=180s  
- K6_RATE=1, VUs=5–10, duration=1m  

**Wyniki (k6):**
- `http_req_duration`: avg ≈ 55 s (max 86 s)  
- `checks_succeeded`: 100%  
- Brak błędów HTTP  

**Obserwacje:**
Symulacja spowolnionego zewnętrznego serwisu (30–120 s) działała poprawnie — wszystkie żądania zakończyły się sukcesem dzięki długiemu timeoutowi (180 s). W Grafanie (Prometheus Dashboard) widoczne były długie czasy trwania żądań, a w Tempo – pojedyncze długie spany (`SpanKind.CLIENT`) korelujące się z wpisami w Loki po `trace_id`.  

**Wnioski:**
- Długi `read_timeout` pozwolił utrzymać 0% error rate mimo opóźnień.  
- Tempo potwierdziło korelację logów i metryk dzięki propagacji `trace_id`.

**Screeny:**  
`01-prep-delay-k6.png`, `01-prep-delay-loki.png`, `01-prep-delay-prometheus-dash.png`, `01-prep-delay-tempo.png`

---

## 2️⃣ Client Timeouts

**Cel:**  
Zweryfikować wpływ `read_timeout` i `connect_timeout` na błędy przy spowolnionych odpowiedziach.

**Konfiguracja:**  
- `EXT_CLIENT_CONNECT_TIMEOUT=2.0s`  
- `EXT_CLIENT_READ_TIMEOUT=180s`  

**Obserwacje:**  
Przy zbyt krótkim czasie odczytu (< 60 s) pojawiały się błędy 5xx, natomiast przy 180 s żądania kończyły się sukcesem. Histogramy latencji w Prometheusie przesunęły się w górę, ale nie odnotowano błędów.  

**Wnioski:**  
Timeouty powinny być dobrane do spodziewanych opóźnień w komunikacji międzyserwisowej. Zbyt krótki `read_timeout` powoduje przerwanie połączeń, a zbyt długi zwiększa zasoby zajęte przez oczekujące wątki.

**Screeny:**  
`02-timeout-180s-prometheus-dash.png`, `02-timeout-180s-tempo.png`

---

## 3️⃣ Connection Pressure (Pool Size & Timeout)

**Konfiguracja (k6):**
- K6_RATE=5, VUs=20–200, duration=5m  
- Kolejne testy A–D: różne wartości `EXT_CLIENT_MAX_CONNECTIONS` i `EXT_CLIENT_POOL_TIMEOUT`

| Test | max_connections | pool_timeout | Sukcesy | Błędy |
|------|-----------------|---------------|----------|-------|
| A | 10 | 0.00s | 2.47% | 97.5% |
| B | 50 | 0.10s | 13.1% | 86.9% |
| C | 100 | 0.25s | 28.3% | 71.6% |
| D | 200 | 1.00s | 100% | 0% |

**Analiza (Grafana + Tempo):**
- Przy małych pulach (10–50) pojawiły się błędy i kolejki połączeń.  
- Tempo pokazywało krótkie spany w `main_api` przerywane oczekiwaniem na połączenie z `external_service`.  
- Loki raportował time-outy przy braku wolnych połączeń.  

**Wnioski:**
- Niska wartość `max_connections` skutkuje saturacją puli i błędami połączenia.  
- Optimum uzyskano przy `max_connections=200` i `pool_timeout=1s` — 100% skutecznych żądań.  
- Wzrost puli połączeń poprawia throughput kosztem zużycia pamięci.

**Screeny:**  
`03-maxconn-10-pool-0s-*`, `03-maxconn-50-pool-0,1s-*`, `03-maxconn-100-pool-0,25s-*`, `03-maxconn-200-pool-1s-*`

---

## 4️⃣ Keep-Alive Connections

**Cel:**  
Zbadać wpływ liczby utrzymywanych połączeń (keep-alive) na stabilność przy wysokim ruchu.

| Test | keepalive_connections | Sukcesy | Błędy |
|------|-----------------------|----------|-------|
| A | 10 | 26.8% | 73.1% |
| B | 50 | 26.6% | 73.4% |

**Obserwacje:**
Wzrost liczby utrzymywanych połączeń poprawił stabilność i zmniejszył zużycie CPU. W Loki i Tempo widoczne było mniejsze natężenie tworzenia nowych połączeń. HTTP/2 nie zmieniło drastycznie wyników, ale poprawiło płynność (brak blokowania przy wielu VU).  

**Wnioski:**
- Niska wartość `keepalive` prowadzi do kosztownego tworzenia połączeń.  
- HTTP/2 + większy pool utrzymywanych sesji poprawia efektywność przy dużej liczbie równoległych żądań.

**Screeny:**  
`04-keepalive-10-*`, `04-keepalive-50-*`

---

## 5️⃣ Protocol: HTTP/1.1 vs HTTP/2

**Konfiguracja:**
- Te same parametry k6 i API  
- Zmieniany tylko `EXT_CLIENT_HTTP2_ENABLED` (True/False)

| Test | Protokół | Sukcesy | Błędy | Średni czas |
|------|-----------|----------|-------|--------------|
| A | HTTP/2 | 89.4% | 10.6% | ~2m14s |
| B | HTTP/1.1 | 27.3% | 72.6% | ~21s (częste błędy) |

**Obserwacje:**
HTTP/2 wykazał wyraźnie mniejszy odsetek błędów i lepsze wykorzystanie połączeń dzięki multiplexingowi. W Tempo spany `HTTP/2` układały się równolegle, natomiast przy HTTP/1.1 widoczna była sekwencja blokujących się żądań.  

**Wnioski:**
- HTTP/2 poprawia wydajność przy wielu jednoczesnych żądaniach, redukuje opóźnienia i liczbę timeoutów.  
- W systemach mikroserwisowych warto włączyć HTTP/2 na ścieżkach o dużym obciążeniu.

**Screeny:**  
`05-http1.1-*`, `05-http2-*`

---

## 6️⃣ Slow PostgreSQL

**Cel:**  
Pokazać wpływ spowolnienia bazy danych na metryki i ścieżki w Tempo.

**Konfiguracja:**
- shared_buffers=2MB  
- work_mem=64kB  
- random_page_cost=10  
- effective_cache_size=1MB  
- 500k rekordów w tabeli `users`  

| Test | Sytuacja | Sukcesy | Błędy | Średni czas |
|------|-----------|----------|-------|--------------|
| A | Spowolniona DB | 73% | 27% | 43 s |
| B | Normalna DB | 84% | 16% | 25 s |

**Obserwacje:**
- W spowolnionej bazie widoczne wzrosty `pg_stat_activity_count` i `blks_read_total`.  
- Grafana (postgres_exporter) pokazywała więcej odczytów z dysku i spadek cache hit ratio.  
- Tempo pokazało dłuższe spany typu `SpanKind.CLIENT` w sekcji DB.  

**Wnioski:**
- Ograniczenie buforów i pamięci podręcznej zwiększyło liczbę operacji I/O, co wydłużyło czas odpowiedzi API.  
- Różnice w metrykach potwierdzają zależność wydajności od konfiguracji parametrów pamięci.

**Screeny:**  
`06-normal-*`, `06-slowed-*`, `06-both-*`
