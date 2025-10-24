from fastapi import APIRouter

from app.routers.users import router as users_router
from app.routers.sensors import router as sensors_router


router = APIRouter()

# Agregador de routers por dominio
router.include_router(users_router)
router.include_router(sensors_router)


@router.get("/ping", tags=["utils"])
def ping():
    return {"ping": "pong"}


@router.get("/items", tags=["items"])
def list_items():
    return {"items": []}

