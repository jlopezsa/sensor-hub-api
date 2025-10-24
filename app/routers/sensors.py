from typing import List

from fastapi import APIRouter, Query

from app.schemas.sensor import Sensor
from app.services.sensor_service import list_sensors as svc_list_sensors, get_sensor as svc_get_sensor
from app.utils.common import paginate


router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("", response_model=List[Sensor])
def list_sensors(skip: int = Query(0, ge=0), limit: int | None = Query(None, ge=1)):
    return paginate(svc_list_sensors(), skip=skip, limit=limit)


@router.get("/{sensor_id}", response_model=Sensor)
def get_sensor(sensor_id: int):
    return svc_get_sensor(sensor_id)

