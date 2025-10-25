from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa para los modelos SQLAlchemy."""


def import_models() -> None:
    """Importa módulos que definen modelos para registrar metadata."""

    # Importaciones tardías para evitar ciclos al iniciar la app
    from app.modules.users import model as users_model  # noqa F401
    from app.modules.sensors import model as sensors_model  # noqa F401

