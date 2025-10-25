import asyncio
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.modules.sensors.service import create_reading_from_topic


logger = logging.getLogger("mqtt_ingest")


async def handle_message(topic: str, payload: str) -> None:
    """Callback de mensajes MQTT: intenta parsear lecturas de sensores.

    Espera tópicos como: sensors/<sensor_id>
    Payload esperado: número (float) o JSON con clave "value".
    """
    try:
        async with SessionLocal() as session:  # type: AsyncSession
            await create_reading_from_topic(topic=topic, payload=payload, session=session)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to ingest MQTT message topic=%s payload=%s err=%s", topic, payload, exc)
