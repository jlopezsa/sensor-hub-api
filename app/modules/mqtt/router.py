from fastapi import APIRouter, status

from app.modules.mqtt.schemas import PublishMessage
from app.modules.mqtt.service import publish_message


router = APIRouter(prefix="/mqtt", tags=["mqtt"])


@router.post("/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish(payload: PublishMessage):
    await publish_message(payload)
    return {"detail": "message sent"}

