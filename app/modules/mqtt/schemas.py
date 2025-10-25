from pydantic import BaseModel, Field


class PublishMessage(BaseModel):
    topic: str = Field(..., min_length=1)
    payload: str
    qos: int = Field(0, ge=0, le=2)
    retain: bool = False

