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
  </p>
</div>

---

## 🎯 Cel projektu

Projekt jest produkcjonopodobnym **REST API sklepu internetowego** w architekturze N-tier, który umożliwia pracę z relacyjną bazą danych PostgreSQL. Projekt ma na celu:

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

---

## ⚙️ Uruchomienie

a) Skopiuj repozytorium i przejdź do katalogu:
   ```bash
   cd shop-api
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

---

> © 2025 Shop REST API – Projekt edukacyjny
