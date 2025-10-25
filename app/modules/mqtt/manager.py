from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Optional, Awaitable
from uuid import uuid4

from gmqtt import Client as GMQTTClient

from app.core.config import settings


MessageHandler = Callable[[str, str], Optional[Awaitable[None]]]


class MQTTManager:
    """Mantiene la conexión con el broker MQTT usando gmqtt."""

    def __init__(self) -> None:
        self._client: Optional[GMQTTClient] = None
        self._connected = asyncio.Event()
        self._on_message: Optional[MessageHandler] = None

    async def connect(self) -> None:
        if self._client is not None:
            return

        client_id = settings.MQTT_CLIENT_ID or f"sensor-hub-{uuid4()}"
        client = GMQTTClient(client_id)

        if settings.MQTT_USERNAME:
            client.set_auth_credentials(settings.MQTT_USERNAME, settings.MQTT_PASSWORD or "")

        client.on_connect = self._handle_connect
        client.on_disconnect = self._handle_disconnect
        client.on_message = self._handle_message

        self._client = client
        await client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
        await self._connected.wait()

    async def disconnect(self) -> None:
        if self._client is None:
            return

        await self._client.disconnect()
        self._client = None
        self._connected.clear()

    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> None:
        await self._ensure_connected()
        assert self._client is not None
        self._client.publish(topic, payload, qos=qos, retain=retain)

    async def subscribe(self, topic: str, qos: int = 0) -> None:
        await self._ensure_connected()
        assert self._client is not None
        self._client.subscribe(topic, qos)

    def register_message_handler(self, handler: MessageHandler) -> None:
        self._on_message = handler

    async def _ensure_connected(self) -> None:
        if self._client is None:
            await self.connect()
        await self._connected.wait()

    def _handle_connect(self, _client: GMQTTClient, _flags, _rc, _properties) -> None:
        self._connected.set()

    def _handle_disconnect(self, _client: GMQTTClient, _packet, _exc: Optional[BaseException]) -> None:
        self._connected.clear()

    def _handle_message(self, client: GMQTTClient, topic: str, payload: str, qos, properties) -> None:
        if not self._on_message:
            return
        handler = self._on_message
        # gmqtt passes payload as bytes
        payload_str = payload.decode("utf-8") if isinstance(payload, (bytes, bytearray)) else str(payload)
        if inspect.iscoroutinefunction(handler):
            asyncio.create_task(handler(topic, payload_str))
        else:
            handler(topic, payload_str)


_manager: Optional[MQTTManager] = None


def get_mqtt_manager() -> MQTTManager:
    global _manager
    if _manager is None:
        _manager = MQTTManager()
    return _manager
