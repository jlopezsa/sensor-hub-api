from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sensors.model import Sensor as SensorModel
from app.modules.sensors.model import SensorReading as SensorReadingModel
from app.modules.sensors.schemas import Sensor, SensorReading


async def list_sensors(session: AsyncSession) -> List[Sensor]:
    result = await session.execute(select(SensorModel))
    sensors = result.scalars().all()
    return [Sensor.model_validate(sensor) for sensor in sensors]


async def get_sensor(sensor_id: int, session: AsyncSession) -> Sensor | None:
    result = await session.execute(select(SensorModel).where(SensorModel.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if sensor is None:
        return None
    return Sensor.model_validate(sensor)


async def create_reading(sensor_id: int, value: float, session: AsyncSession, *, ts: Optional[datetime] = None) -> None:
    reading = SensorReadingModel(sensor_id=sensor_id, value=value)
    if ts is not None:
        reading.timestamp = ts
    session.add(reading)
    await session.commit()


async def create_reading_from_topic(topic: str, payload: str, session: AsyncSession) -> None:
    """Parsea topic/payload y crea lectura si coincide con el patrón sensors/<id>."""
    if not topic.startswith("sensors/"):
        return
    _, _, id_part = topic.partition("/")
    try:
        sensor_id = int(id_part)
    except ValueError:
        return
    ts: Optional[datetime] = None
    try:
        value = float(payload)
    except ValueError:
        import json
        try:
            data = json.loads(payload)
            value = float(data.get("value"))
            raw_ts = data.get("timestamp")
            if raw_ts:
                # Soportar 'Z' (UTC) y offsets ISO8601
                if isinstance(raw_ts, str):
                    ts = _parse_iso_datetime(raw_ts)
        except Exception:
            return
    await create_reading(sensor_id=sensor_id, value=value, session=session, ts=ts)


def _parse_iso_datetime(s: str) -> Optional[datetime]:
    try:
        # Reemplaza 'Z' con +00:00 para fromisoformat
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


async def list_readings(
    sensor_id: int,
    session: AsyncSession,
    *,
    since: Optional[datetime] = None,
    limit: Optional[int] = 100,
) -> List[SensorReading]:
    stmt = select(SensorReadingModel).where(SensorReadingModel.sensor_id == sensor_id)
    if since is not None:
        stmt = stmt.where(SensorReadingModel.timestamp >= since)
    # Más recientes primero
    from sqlalchemy import desc

    stmt = stmt.order_by(desc(SensorReadingModel.timestamp))
    if limit is not None and limit > 0:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    readings = result.scalars().all()
    return [
        SensorReading(sensor_id=r.sensor_id, timestamp=r.timestamp, value=r.value)
        for r in readings
    ]


# NOTE: Override previous implementation to support string IDs, JSON payloads, and timestamps
async def create_reading_from_topic(topic: str, payload: str, session: AsyncSession) -> None:  # type: ignore[override]
    """Parsea topic/payload y crea lectura si coincide con el patrón sensors/<identificador>.

    - <identificador> puede ser numérico (id) o de texto (name) del sensor.
    - Payload soportado:
        * Número (float) directo -> value
        * JSON con clave "value" y opcionalmente "timestamp" (ISO8601 o epoch ms/s)
        * Si el JSON contiene "sensorId", se prioriza para resolver el sensor
    - No se crea el sensor automáticamente: solo guarda si el sensor ya existe.
    """
    import logging as _logging
    import json as _json

    logger = _logging.getLogger("sensors.service")
    if not topic.startswith("sensors/"):
        return

    # Identificador inicial desde el tópico
    _, _, id_part = topic.partition("/")
    identifier: Optional[str] = (id_part or "").strip() or None

    # Intentar parseo del payload
    ts: Optional[datetime] = None
    value: Optional[float] = None
    payload_data: Optional[dict[str, object]] = None

    # 1) payload como número plano
    try:
        value = float(payload)
    except ValueError:
        # 2) payload como JSON
        try:
            payload_data = _json.loads(payload)
        except Exception:
            # payload no reconocido
            return

    if payload_data is not None:
        try:
            if "sensorId" in payload_data and isinstance(payload_data["sensorId"], str):
                identifier = payload_data["sensorId"].strip() or identifier
            if "value" in payload_data:
                value = float(payload_data["value"])  # puede lanzar
            raw_ts = payload_data.get("timestamp")
            if raw_ts is not None:
                ts = _parse_any_timestamp(raw_ts)
        except Exception:
            return

    if value is None:
        # no hay valor válido que guardar
        return

    # Resolver sensor_id por id numérico o por nombre
    sensor_id = await _resolve_sensor_id(identifier, session)
    if sensor_id is None:
        # No crear sensores automáticamente por ahora
        logger.info("Ignoring reading for unknown sensor identifier=%s", identifier)
        return

    await create_reading(sensor_id=sensor_id, value=value, session=session, ts=ts)


def _parse_any_timestamp(raw: object) -> Optional[datetime]:
    """Acepta ISO-8601, epoch en segundos o milisegundos.

    Heurística:
    - str -> intentar ISO
    - int/float:
        * >= 1e12 -> epoch ms
        * >= 1e9  -> epoch s
        * otro    -> ignorar (probablemente contador no epoch)
    """
    from datetime import timezone as _tz

    try:
        if isinstance(raw, str):
            return _parse_iso_datetime(raw)
        if isinstance(raw, (int, float)):
            v = float(raw)
            if v >= 1e12:
                # milisegundos
                return datetime.fromtimestamp(v / 1000.0, tz=_tz.utc)
            if v >= 1e9:
                # segundos
                return datetime.fromtimestamp(v, tz=_tz.utc)
            return None
    except Exception:
        return None
    return None


async def _resolve_sensor_id(identifier: Optional[str], session: AsyncSession) -> Optional[int]:
    """Devuelve el id de sensor si existe, resolviendo por id numérico o por nombre exacto."""
    if not identifier:
        return None
    # Intentar id numérico directo
    try:
        sensor_id = int(identifier)
        result = await session.execute(select(SensorModel.id).where(SensorModel.id == sensor_id))
        row = result.first()
        if row is not None:
            return sensor_id
    except ValueError:
        pass
    # Resolver por nombre
    result = await session.execute(select(SensorModel).where(SensorModel.name == identifier))
    sensor = result.scalar_one_or_none()
    if sensor is None:
        return None
    return sensor.id
