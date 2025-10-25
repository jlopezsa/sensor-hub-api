from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import import_models


def _make_engine() -> AsyncEngine:
    return create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)


engine = _make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI que entrega una sesión de BD."""

    async with SessionLocal() as session:
        yield session


def init_models() -> None:
    """Importa modelos para poblar metadata."""

    import_models()

