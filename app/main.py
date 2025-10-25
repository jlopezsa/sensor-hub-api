from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, init_models
from app.routers.routes import router as api_router


app = FastAPI(title=settings.APP_NAME, version="0.1.0", debug=settings.DEBUG)


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


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await engine.dispose()
