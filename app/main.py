import logging

from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, init_models
from app.routers.routes import router as api_router
from app.modules.mqtt.manager import get_mqtt_manager


app = FastAPI(title=settings.APP_NAME, version="0.1.0", debug=settings.DEBUG)

logger = logging.getLogger("sensor_hub_api")


@app.get("/", tags=["root"])
def read_root():
    return {"app": settings.APP_NAME, "message": "Bienvenido"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def on_startup() -> None:
    """Inicializa metadata y crea tablas en ausencia de migraciones."""

    init_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await get_mqtt_manager().connect()
        logger.info("Connected to MQTT broker at %s:%s", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
    except Exception as exc:  # noqa: BLE001
        logger.warning("MQTT connection failed: %s", exc)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    try:
        await get_mqtt_manager().disconnect()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Error during MQTT disconnect: %s", exc)
    await engine.dispose()
