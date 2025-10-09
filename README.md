# Shop API

## Uruchomienie
1. Zainstaluj Docker Desktop (Windows/mac) lub Docker Engine (Linux).
2. W katalogu projektu:
   docker compose up --build

3. API:
   http://localhost:8000/docs

## Hot-reload
Kod jest montowany do kontenera (volumes), a uvicorn uruchomiony z --reload — zmiany w plikach będą restartować serwer automatycznie.

## DB
Postgres na porcie 5432 (używa danych z volume `db_data`).

