# Sensor Hub API (FastAPI Template)

Plantilla mínima para iniciar un backend con Python y FastAPI.

## Estructura

- `app/main.py`: Punto de entrada de FastAPI (rutas raíz y health).
- `app/core/config.py`: Configuración por variables de entorno (Pydantic Settings).
- `app/api/v1/routes.py`: Rutas de ejemplo (`/ping`, `/items`).
- `.env.example`: Variables de entorno de ejemplo.
- `requirements.txt`: Dependencias básicas.
- `run.ps1` / `run.sh`: Scripts para levantar el servidor en dev.

## Requisitos

- Python 3.10+

## Configuración rápida (Poetry)

1) Copia variables de entorno: `cp .env.example .env`
2) Instala dependencias con Poetry y ejecuta:

```bash
# Linux/macOS
bash run-poetry.sh

# Windows (PowerShell)
./run-poetry.ps1
```

El servidor queda disponible en `http://localhost:8000`.

## Endpoints iniciales

- `GET /` → mensaje de bienvenida
- `GET /health` → `{ "status": "ok" }`
- `GET /api/v1/ping` → `{ "ping": "pong" }`
- `GET /api/v1/items` → `{ "items": [] }`

## Ejecutar manualmente

```bash
# Con Poetry
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Personalización siguiente

- Agrega routers por dominio (e.g., `app/api/v1/users.py`).
- Añade modelos y esquemas (Pydantic) según tu dominio.
- Integra base de datos (SQLModel/SQLAlchemy) y settings de DB.
- Configura CORS, logging y middlewares.

## Tests

Ejecuta la suite de tests con pytest:

```bash
poetry run pytest
```

Pruebas incluidas:
- `tests/test_health.py` valida `GET /health` y `GET /`.
