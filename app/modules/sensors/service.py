from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sensors.model import Sensor as SensorModel
from app.modules.sensors.schemas import Sensor


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

