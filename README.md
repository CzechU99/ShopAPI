# Shop API

## Uruchomienie (dev)
1. Skopiuj repo i przejdź do katalogu:
   cd shop-api
2. Uruchom:
   docker compose up --build
3. Po chwili:
- API: localhost:8000/docs
- DB: localhost:5432 (user: shop | pass: shop | db: shopdb)
- PGADMIN: localhost:8080 (email: admin@admin.com | pass: admin)

## Migrations (Alembic)
W kontenerze app:
   docker compose exec app alembic upgrade head