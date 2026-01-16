# FastAPI + Supabase Template

## Overview

A FastAPI + Supabase starter with async PostgreSQL access, FastAPI Users auth scaffolding, and Pydantic settings-based configuration. It is container-friendly and ready for local development with uv.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) installed
- A Supabase/PostgreSQL instance (or any Postgres database) reachable from your machine
- Alembic installed via project deps (comes with `uv sync`)

## Installation (uv)

1. Install uv if needed (one-time):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Install dependencies and create a virtual environment (managed in `.venv`):
   ```bash
   uv sync
   ```
3. (Optional) Activate the venv for interactive shells:

   ```bash
   source .venv/bin/activate
   ```

4. (Optional) Verify Alembic is available:
   ```bash
   uv run alembic --version
   ```

## Environment variables

Create a `.env` file in the project root with at least:

```bash
API_V1_STR=/api/v1
PROJECT_NAME=FastAPI Supabase Template
ENVIRONMENT=local
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
```

These map to the settings defined in [`app/core/config.py`](app/core/config.py:1).

Alembic uses [`alembic.ini`](alembic.ini:1) for connection details. Update `sqlalchemy.url` (or inject via env var) to match your database before running migrations.

## Running the API

- Start the dev server (hot reload):
  ```bash
  uv run uvicorn app.main:app --reload
  ```
- Visit interactive docs: http://localhost:8000/docs
- Health check root: http://localhost:8000/

## Database migrations (Alembic)

- Generate a new migration (autogenerate from models):
  ```bash
  uv run alembic revision --autogenerate -m "describe change"
  ```
- Apply migrations to the database:
  ```bash
  uv run alembic upgrade head
  ```
- Downgrade (optional):
  ```bash
  uv run alembic downgrade -1
  ```
- Migration scripts live in [`alembic/versions`](alembic/versions:1); template in [`alembic/script.py.mako`](alembic/script.py.mako:1); env config in [`alembic/env.py`](alembic/env.py:1).

### Notes for autogenerate

- Ensure all models are imported into [`app/db/base.py`](app/db/base.py:1) so Alembic can detect metadata changes.
- Keep `sqlalchemy.url` in sync with your `.env` database settings or pass `DATABASE_URL` when running commands.

## Project layout (high level)

- [`app/main.py`](app/main.py:1) — FastAPI app, CORS, routers, lifespan hooks
- [`app/routes/users.py`](app/routes/users.py:1) — user endpoints
- [`app/models/users.py`](app/models/users.py:1) — ORM models
- [`app/schemas/users.py`](app/schemas/users.py:1) — Pydantic schemas
- [`app/core/config.py`](app/core/config.py:1) — settings via pydantic-settings
- [`app/services/database.py`](app/services/database.py:1) — database init and connection warm-up

## Notes

- Default API prefix is `/api/v1` (configurable via `API_V1_STR`).
- Uses `fastapi-users` with async Postgres drivers (`asyncpg`/`sqlalchemy`).
- Supabase credentials must match the Postgres connection details in your `.env`.
