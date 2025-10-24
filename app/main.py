from fastapi import FastAPI

from app.api.v1.routes import router as api_v1_router
from app.core.config import settings


app = FastAPI(title=settings.APP_NAME, version="0.1.0", debug=settings.DEBUG)


@app.get("/", tags=["root"])
def read_root():
    return {"app": settings.APP_NAME, "message": "Bienvenido"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(api_v1_router, prefix=settings.API_V1_STR)

