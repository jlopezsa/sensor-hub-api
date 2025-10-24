from pydantic import BaseModel


class Sensor(BaseModel):
    id: int
    name: str

