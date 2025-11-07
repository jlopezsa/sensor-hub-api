from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
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


# Final override: support DHT11_temperature/DHT11_humidity style names
async def create_reading_from_topic(topic: str, payload: str, session: AsyncSession) -> None:  # type: ignore[override]
    import logging as _logging
    import json as _json

    logger = _logging.getLogger("sensors.service")
    if not topic.startswith("sensors/"):
        return

    # Identificador exacto desde el tÃ³pico (puede incluir sufijos)
    _, _, id_part = topic.partition("/")
    topic_identifier: Optional[str] = (id_part or "").strip() or None
    topic_metric: Optional[str] = None
    base_from_topic: Optional[str] = None
    if topic_identifier and "_" in topic_identifier:
        base_from_topic, _, suffix = topic_identifier.partition("_")
        base_from_topic = base_from_topic or None
        topic_metric = (suffix or "").strip().lower() or None

    # Parseo del payload
    ts: Optional[datetime] = None
    value: Optional[float] = None
    identifier_from_payload: Optional[str] = None
    metric: Optional[str] = None

    try:
        value = float(payload)
    except ValueError:
        try:
            data = _json.loads(payload)
        except Exception:
            return
        try:
            if "value" in data:
                value = float(data["value"])  # puede lanzar
            sid = data.get("sensorId")
            if isinstance(sid, str):
                identifier_from_payload = sid.strip() or None
            t = data.get("type")
            if isinstance(t, str):
                metric = t.strip().lower() or None
            raw_ts = data.get("timestamp")
            if raw_ts is not None:
                ts = _parse_any_timestamp(raw_ts)
        except Exception:
            return

    if value is None:
        return

    # Construir candidatos en orden de prioridad
    candidates: list[str] = []
    # 1) nombre completo del tÃ³pico (con sufijo)
    if topic_identifier and "_" in topic_identifier:
        candidates.append(topic_identifier)
    # 2) sensorId + type del payload
    if identifier_from_payload and metric:
        candidates.append(f"{identifier_from_payload}_{metric}")
    # 3) sensorId + sufijo del tÃ³pico
    if identifier_from_payload and topic_metric:
        candidates.append(f"{identifier_from_payload}_{topic_metric}")
    # 4) nombre simple del tÃ³pico
    if topic_identifier:
        candidates.append(topic_identifier)
    # 5) base del tÃ³pico (sin sufijo)
    if base_from_topic:
        candidates.append(base_from_topic)
    # 6) solo sensorId
    if identifier_from_payload:
        candidates.append(identifier_from_payload)

    # de-duplicar preservando orden
    ordered: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            ordered.append(c)

    sensor_id: Optional[int] = None
    logger.debug("MQTT ingest candidates=%s topic=%s", ordered, topic)
    for cand in ordered:
        sid = await _resolve_sensor_id2(cand, session)
        if sid is not None:
            sensor_id = sid
            logger.info("MQTT ingest matched sensor '%s' -> id=%s", cand, sid)
            break

    if sensor_id is None:
        logger.info("Ignoring reading for unknown sensor candidates=%s", ordered)
        return

    await create_reading(sensor_id=sensor_id, value=value, session=session, ts=ts)




def _parse_any_timestamp(raw: object) -> Optional[datetime]:
    """Acepta ISO-8601, epoch en segundos o milisegundos.

    HeurÃ­stica:
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


async def _resolve_sensor_id2(identifier: Optional[str], session: AsyncSession) -> Optional[int]:
    """Versión robusta: resuelve por id, nombre exacto o nombre case-insensitive."""
    if not identifier:
        return None
    try:
        sensor_id = int(identifier)
        result = await session.execute(select(SensorModel.id).where(SensorModel.id == sensor_id))
        row = result.first()
        if row is not None:
            return sensor_id
    except ValueError:
        pass
    # exacto
    result = await session.execute(select(SensorModel).where(SensorModel.name == identifier))
    sensor = result.scalar_one_or_none()
    if sensor is not None:
        return sensor.id
    # case-insensitive
    try:
        lowered = identifier.lower()
        result = await session.execute(select(SensorModel).where(func.lower(SensorModel.name) == lowered))
        sensor = result.scalar_one_or_none()
        if sensor is not None:
            return sensor.id
    except Exception:
        pass
    return None

async def _resolve_sensor_id(identifier: Optional[str], session: AsyncSession) -> Optional[int]:
    """Devuelve el id de sensor si existe, resolviendo por id numÃ©rico o por nombre exacto."""
    if not identifier:
        return None
    # Intentar id numÃ©rico directo
    try:
        sensor_id = int(identifier)
        result = await session.execute(select(SensorModel.id).where(SensorModel.id == sensor_id))
        row = result.first()
        if row is not None:
            return sensor_id
    except ValueError:
        pass
    # Resolver por nombre exacto\r\n    result = await session.execute(select(SensorModel).where(SensorModel.name == identifier))\r\n    sensor = result.scalar_one_or_none()\r\n    if sensor is not None:\r\n        return sensor.id\r\n    # Resolver por nombre case-insensitive\r\n    try:\r\n        lowered = identifier.lower()\r\n        result = await session.execute(select(SensorModel).where(func.lower(SensorModel.name) == lowered))\r\n        sensor = result.scalar_one_or_none()\r\n        if sensor is not None:\r\n            return sensor.id\r\n    except Exception:\r\n        pass\r\n    return None

