from fastapi import APIRouter

from app.modules.users.router import router as users_router
from app.modules.sensors.router import router as sensors_router
from app.modules.mqtt.router import router as mqtt_router


router = APIRouter()

# Agregador de routers por dominio
router.include_router(users_router)
router.include_router(sensors_router)
router.include_router(mqtt_router)


@router.get("/ping", tags=["utils"])
def ping():
    return {"ping": "pong"}


@router.get("/items", tags=["items"])
def list_items():
    return {"items": []}
