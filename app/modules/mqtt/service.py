from app.modules.mqtt.manager import get_mqtt_manager
from app.modules.mqtt.schemas import PublishMessage


async def publish_message(payload: PublishMessage) -> None:
    manager = get_mqtt_manager()
    await manager.publish(
        topic=payload.topic,
        payload=payload.payload,
        qos=payload.qos,
        retain=payload.retain,
    )
