# Sensor Hub API (FastAPI Template)

Plantilla mínima para iniciar un backend con Python y FastAPI.

## Estructura

- `app/main.py`: Punto de entrada de FastAPI (rutas raíz y health).
- `app/core/config.py`: Configuración por variables de entorno (Pydantic Settings).
- `app/routers/routes.py`: Agregador de routers y rutas utilitarias (`/ping`, `/items`).
- `app/routers/users.py`: Endpoints de usuarios.
- `app/routers/sensors.py`: Endpoints de sensores.
- `app/services/*`: Lógica de negocio simple de ejemplo.
- `app/schemas/*`: Esquemas Pydantic (entrada/salida).
- `app/models/*`: Modelos de dominio/ORM (placeholders por ahora).
- `app/utils/*`: Utilidades compartidas (e.g., paginación).
- `.env.example`: Variables de entorno de ejemplo.
- `pyproject.toml`: Gestión de dependencias con Poetry.
- `run.ps1` / `run.sh`: Scripts para levantar el servidor en dev (Poetry).

## Requisitos

- Python 3.10+
- Poetry

## Configuración rápida (Poetry)

1) Copia variables de entorno: `cp .env.example .env`
2) Instala dependencias con Poetry y ejecuta:

```bash
# Linux/macOS
bash run.sh

# Windows (PowerShell)
./run.ps1
```

El servidor queda disponible en `http://localhost:8000`.

## Endpoints iniciales

- `GET /` → mensaje de bienvenida
- `GET /health` → `{ "status": "ok" }`
- `GET /api/ping` → `{ "ping": "pong" }`
- `GET /api/items` → `{ "items": [] }`
- `GET /api/users`, `GET /api/users/{id}`
- `GET /api/sensors`, `GET /api/sensors/{id}`

## Ejecutar manualmente

```bash
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Personalización siguiente

- Extiende routers por dominio (e.g., `app/routers/`).
- Añade modelos y esquemas (Pydantic) según tu dominio.
- Integra base de datos (SQLModel/SQLAlchemy) y settings de DB.
- Configura CORS, logging y middlewares.

## Tests

```bash
poetry run pytest
```

Pruebas incluidas:
- `tests/test_health.py` valida `GET /health` y `GET /`.
