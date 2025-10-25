# Sensor Hub API (FastAPI + SQLAlchemy + TimescaleDB + MQTT)

Starter backend template with FastAPI, async SQLAlchemy, and a modular layout ready to work with PostgreSQL/TimescaleDB and an MQTT broker.

## Project Layout

- `app/main.py` – FastAPI entrypoint, healthcheck, database bootstrap, MQTT startup hook.
- `app/core/config.py` – Pydantic settings driven by environment variables.
- `app/db/` – async engine/session factory (`session.py`) and declarative base (`base.py`).
- `app/modules/users/*` – users module (router, service, schemas, SQLAlchemy model).
- `app/modules/sensors/*` – sensors module (router, service, schemas, models for sensors/readings).
- `app/modules/mqtt/*` – MQTT client module (manager, service, publish schema, router).
- `app/routers/routes.py` – aggregates module routers and exposes utility endpoints (`/ping`, `/items`).
- `app/utils/*` – shared helpers (pagination, etc.).
- `.env.example` – sample environment variables.
- `docker-compose.yml` – TimescaleDB, pgAdmin, and Mosquitto services for local development.
- `pyproject.toml` – Poetry-managed dependencies.
- `run.sh` / `run.ps1` – convenience scripts that install deps and run Uvicorn.

## Requirements

- Python 3.10 or 3.11 (Python 3.12+ also works with psycopg binary wheels).
- Poetry
- Docker (optional, for the compose stack).
- PostgreSQL/TimescaleDB reachable from your machine.
- MQTT broker (e.g., Eclipse Mosquitto) if you plan to publish/subscribe.

## Quickstart

```bash
cp .env.example .env
# adjust DATABASE_URL and MQTT_* variables to match your environment

# (Optional) start services with docker compose
docker compose up -d timescaledb pgadmin mqtt

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
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=sensor-hub-api
```

## Database & TimescaleDB

1. Spin up TimescaleDB (Docker example):

   ```bash
   docker run --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d timescale/timescaledb:2.15.2-pg16
   ```

2. Create the database and enable Timescale extension:

   ```sql
   CREATE DATABASE sensor_hub;
   \c sensor_hub;
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

3. Once tables exist (via migrations/startup), convert readings into a hypertable:

   ```sql
   SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);
   ```

4. Use Alembic for schema changes in production:

   ```bash
   poetry run alembic init migrations
   # configure migrations/env.py to use AsyncEngine and Base.metadata
   poetry run alembic revision --autogenerate -m "init"
   poetry run alembic upgrade head
   ```

> Startup currently runs `Base.metadata.create_all()` for development convenience. Remove it once migrations control the schema.

## MQTT broker

- `docker-compose.yml` includes a Mosquitto service with default config (`docker/mqtt/mosquitto.conf`).
- On startup the app attempts to connect to the broker; failures are logged but do not crash the API.
- Use the `/api/mqtt/publish` endpoint to publish messages via HTTP.

Example publish:

```bash
curl -X POST http://localhost:8000/api/mqtt/publish \
  -H "Content-Type: application/json" \
  -d '{"topic": "sensors/1", "payload": "42.5", "qos": 1}'
```

## Initial endpoints

- `GET /` – welcome payload
- `GET /health` – `{ "status": "ok" }`
- `GET /api/ping` – `{ "ping": "pong" }`
- `GET /api/items` – `{ "items": [] }`
- `GET /api/users`, `GET /api/users/{id}`
- `GET /api/sensors`, `GET /api/sensors/{id}`
- `POST /api/mqtt/publish` – publish MQTT messages through the backend

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
- Create a readings ingestion module that subscribes to MQTT topics and writes to TimescaleDB.
- Wire Alembic migrations to manage hypertables and schema changes.
- Add authentication/authorization per module.
- Write integration tests against containerized services.
