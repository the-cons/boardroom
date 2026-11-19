# Boardroom — learning Django

> **📚 Learning project — not production code.**
> I built this step by step while learning Django (coming from Java/Spring Boot and Rust),
> following a guided tutorial with [Claude](https://claude.ai) as my tutor. The code is mine, typed and debugged
> by hand, but the structure and exercises came from the tutorial. It exists to practise the framework,
> not to be a finished product.

A toy governance tracker for funds and legal entities: entities, the people involved in them, and an API on top.

## What I practised

- Django project / app structure (`entities`, `people`, `accounts`, `core`, `demo`)
- Models, migrations and the Django ORM on PostgreSQL
- The Django admin
- Django REST Framework — serializers, views, permissions
- Settings via environment variables (`django-environ`)
- A custom management command for seeding demo data
- Authentication
- Docker Compose for local development, `just` recipes for everyday commands

## Stack

Python 3.13 · Django · Django REST Framework · PostgreSQL 18 · Docker Compose · uv · just

## Running it

```bash
cp .env.example .env        # then set SECRET_KEY
just up-d                   # Django + Postgres in Docker
just migrate
just seed                   # demo data
```

The app runs on http://localhost:8000. Run `just` to see all recipes.

---

[Constantin Theis](https://portfolio.ths.lu)
