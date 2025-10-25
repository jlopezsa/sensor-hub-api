import logging

from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, init_models
from app.routers.routes import router as api_router
from app.modules.mqtt.manager import get_mqtt_manager
from app.modules.mqtt.ingest import handle_message as mqtt_handle_message


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
        manager = get_mqtt_manager()
        manager.register_message_handler(mqtt_handle_message)
        await manager.connect()
        # Suscribirse a tópicos configurados
        topics = (settings.MQTT_SUBSCRIBE_TOPICS or "").split(",")
        for raw in topics:
            topic = raw.strip()
            if topic:
                await manager.subscribe(topic)
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
