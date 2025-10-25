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

