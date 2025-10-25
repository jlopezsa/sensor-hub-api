from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.modules.sensors.schemas import Sensor, SensorReading
from app.modules.sensors.service import (
    get_sensor as svc_get_sensor,
    list_readings as svc_list_readings,
    list_sensors as svc_list_sensors,
)
from app.utils.common import paginate


router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("", response_model=List[Sensor])
async def list_sensors(
    skip: int = Query(0, ge=0),
    limit: int | None = Query(None, ge=1),
    session: AsyncSession = Depends(get_session),
):
    sensors = await svc_list_sensors(session=session)
    return paginate(sensors, skip=skip, limit=limit)


@router.get("/{sensor_id}", response_model=Sensor)
async def get_sensor(sensor_id: int, session: AsyncSession = Depends(get_session)):
    sensor = await svc_get_sensor(sensor_id=sensor_id, session=session)
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")
    return sensor


@router.get("/{sensor_id}/readings", response_model=List[SensorReading])
async def get_readings(
    sensor_id: int,
    since: Optional[datetime] = Query(None, description="ISO-8601 datetime filter"),
    limit: Optional[int] = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    return await svc_list_readings(sensor_id=sensor_id, since=since, limit=limit, session=session)

