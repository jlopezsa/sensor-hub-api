from __future__ import annotations

import asyncio
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger("sensors.websocket")


class SensorWebSocketManager:
    """Manage WebSocket subscribers for sensor readings."""

    def __init__(self) -> None:
        self._all: Set[WebSocket] = set()
        self._by_sensor: Dict[int, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, sensor_id: int | None) -> None:
        async with self._lock:
            if sensor_id is None:
                self._all.add(websocket)
            else:
                self._by_sensor.setdefault(sensor_id, set()).add(websocket)

    async def disconnect(self, websocket: WebSocket, sensor_id: int | None) -> None:
        async with self._lock:
            self._all.discard(websocket)
            for bucket in self._by_sensor.values():
                bucket.discard(websocket)
            # clean empty buckets
            self._by_sensor = {k: v for k, v in self._by_sensor.items() if v}

    async def broadcast_reading(self, sensor_id: int, payload: dict) -> None:
        """Send a reading to sensor-specific and global subscribers."""
        targets: Set[WebSocket] = set()
        async with self._lock:
            targets.update(self._all)
            targets.update(self._by_sensor.get(sensor_id, set()))

        stale: Set[WebSocket] = set()
        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception as exc:  # noqa: BLE001
                logger.debug("Failed to send ws message: %s", exc)
                stale.add(ws)

        if stale:
            async with self._lock:
                for ws in stale:
                    self._all.discard(ws)
                for bucket in self._by_sensor.values():
                    bucket.difference_update(stale)
                self._by_sensor = {k: v for k, v in self._by_sensor.items() if v}


_manager: SensorWebSocketManager | None = None


def get_sensor_ws_manager() -> SensorWebSocketManager:
    global _manager
    if _manager is None:
        _manager = SensorWebSocketManager()
    return _manager
