from typing import List

from app.modules.sensors.schemas import Sensor


def list_sensors() -> List[Sensor]:
    return [Sensor(id=1, name="sensor-1"), Sensor(id=2, name="sensor-2")]


def get_sensor(sensor_id: int) -> Sensor:
    return Sensor(id=sensor_id, name=f"sensor-{sensor_id}")

