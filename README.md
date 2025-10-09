# Shop API

## Uruchomienie (dev)
1. Skopiuj repo i przejdź do katalogu:
   cd shop-api
2. Uruchom:
   docker compose up --build
3. Po chwili:
- API: http://localhost:8000/docs
- DB: localhost:5432 (user: shop / pass: shop / db: shopdb)

## Migrations (Alembic)
W kontenerze app:
   docker compose exec app alembic upgrade head