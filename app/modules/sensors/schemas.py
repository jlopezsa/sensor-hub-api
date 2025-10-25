from pydantic import BaseModel, ConfigDict


class Sensor(BaseModel):
    id: int
    name: str
    location: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SensorReading(BaseModel):
    sensor_id: int
    timestamp: str
    value: float

    model_config = ConfigDict(from_attributes=True)

