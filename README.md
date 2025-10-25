# Sensor Hub API (FastAPI + SQLAlchemy + TimescaleDB)

Starter backend template with FastAPI, asynchronous SQLAlchemy, and a modular structure ready to talk to PostgreSQL/TimescaleDB.

## Project Layout

- `app/main.py` – FastAPI entrypoint, healthcheck, and database bootstrap.
- `app/core/config.py` – environment driven settings.
- `app/db/` – async engine/session factory (`session.py`) and declarative base (`base.py`).
- `app/modules/users/*` – users module (router, service, schemas, model).
- `app/modules/sensors/*` – sensors module (router, service, schemas, model & readings).
- `app/routers/routes.py` – aggregates module routers and utility endpoints (`/ping`, `/items`).
- `app/utils/*` – shared helpers (pagination, etc.).
- `.env.example` – sample environment variables.
- `pyproject.toml` – Poetry dependencies.
- `run.sh` / `run.ps1` – dev scripts using Poetry.

## Requirements

- Python 3.10 or 3.11 (psycopg binaries cover Windows/macOS/Linux; Python 3.12+ works too).
- Poetry
- PostgreSQL/TimescaleDB reachable from your machine.
- On Windows: nothing extra needed (psycopg-binary ships wheels).

## Quickstart

```bash
cp .env.example .env
# adjust DATABASE_URL to point to your PostgreSQL/Timescale instance

# Linux/macOS
bash run.sh

# Windows (PowerShell)
./run.ps1
```

The API will be available at `http://localhost:8000`.

## Environment variables

```ini
APP_NAME=Sensor Hub API
DEBUG=true
API_PREFIX=/api
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/sensor_hub
```

## Database and TimescaleDB setup

1. Spin up TimescaleDB (Docker example):

   ```bash
   docker run --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d timescale/timescaledb:2.15.2-pg16
   ```

2. Create the database and enable the extension:

   ```sql
   CREATE DATABASE sensor_hub;
   \c sensor_hub;
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

3. After the tables exist (via migrations or startup), convert readings into a hypertable:

   ```sql
   SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);
   ```

4. Use Alembic for production migrations (already listed as dependency):

   ```bash
   poetry run alembic init migrations
   # configure migrations/env.py to use AsyncEngine and Base.metadata
   poetry run alembic revision --autogenerate -m "init"
   poetry run alembic upgrade head
   ```

> Startup currently calls `Base.metadata.create_all()` for convenience. Remove it once you rely on migrations.

> Windows tip: `psycopg[binary]` viene con binarios precompilados. Si prefieres la versión “c” (`psycopg[c]`), instala Visual Studio Build Tools primero.

## Initial endpoints

- `GET /` – welcome payload
- `GET /health` – `{ "status": "ok" }`
- `GET /api/ping` – `{ "ping": "pong" }`
- `GET /api/items` – `{ "items": [] }`
- `GET /api/users`, `GET /api/users/{id}`
- `GET /api/sensors`, `GET /api/sensors/{id}`

## Manual run

```bash
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
poetry run pytest
```

## Suggested next steps

- Add POST/PUT/DELETE endpoints using transactions (`AsyncSession`).
- Create a dedicated readings module with bulk inserts optimized for TimescaleDB.
- Wire Alembic migrations to manage hypertables and schema changes.
- Add authentication/authorization per module.
- Write integration tests hitting a containerized database.
