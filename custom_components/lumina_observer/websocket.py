"""WebSocket client for Lumina Observer streaming API.

Handles connection, reconnection with exponential backoff, heartbeat
detection, and message parsing.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable
from urllib.parse import urlencode

import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed, WebSocketException

from .const import (
    BACKOFF_MULTIPLIER,
    HEARTBEAT_TIMEOUT,
    INITIAL_BACKOFF,
    MAX_BACKOFF,
    WS_URL,
)

_LOGGER = logging.getLogger(__name__)

MessageCallback = Callable[[dict[str, Any]], None]
StatusCallback = Callable[[bool], None]


class LuminaWebSocketClient:
    """Manages a WebSocket connection to Lumina Observer with reconnection."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        api_key: str,
        on_prediction: MessageCallback,
        on_status_change: StatusCallback | None = None,
    ) -> None:
        """Initialize the WebSocket client.

        Args:
            latitude: Observer's latitude.
            longitude: Observer's longitude.
            api_key: Lumina API key (prefixed with lumina_).
            on_prediction: Callback invoked with parsed prediction dicts.
            on_status_change: Optional callback invoked with True (connected)
                or False (disconnected).
        """
        self._latitude = latitude
        self._longitude = longitude
        self._api_key = api_key
        self._on_prediction = on_prediction
        self._on_status_change = on_status_change

        self._ws: ClientConnection | None = None
        self._task: asyncio.Task[None] | None = None
        self._shutdown = False
        self._backoff = INITIAL_BACKOFF
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._last_message_time = 0.0

    @property
    def connected(self) -> bool:
        """Return whether the WebSocket is currently connected."""
        return self._ws is not None and self._ws.state.name == "OPEN"

    def _build_url(self) -> str:
        params = urlencode(
            {
                "lat": self._latitude,
                "lng": self._longitude,
                "x-api-key": self._api_key,
            }
        )
        return f"{WS_URL}?{params}"

    async def connect(self) -> None:
        """Start the WebSocket connection loop."""
        self._shutdown = False
        self._task = asyncio.create_task(self._run())

    async def disconnect(self) -> None:
        """Shut down the WebSocket connection and cancel all tasks."""
        self._shutdown = True
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        """Main connection loop with exponential backoff reconnection."""
        while not self._shutdown:
            try:
                await self._connect_and_listen()
            except asyncio.CancelledError:
                break
            except Exception:
                _LOGGER.exception("Unexpected error in WebSocket loop")

            if self._shutdown:
                break

            # Exponential backoff before reconnect
            _LOGGER.debug("Reconnecting in %ds...", self._backoff)
            await asyncio.sleep(self._backoff)
            self._backoff = min(
                self._backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF
            )

    async def _connect_and_listen(self) -> None:
        """Establish connection and process incoming messages."""
        url = self._build_url()
        _LOGGER.debug("Connecting to %s", url)

        try:
            async with websockets.connect(url) as ws:
                self._ws = ws
                self._backoff = INITIAL_BACKOFF  # reset on success
                self._last_message_time = asyncio.get_running_loop().time()

                if self._on_status_change:
                    self._on_status_change(True)

                # Start heartbeat monitor
                self._heartbeat_task = asyncio.create_task(
                    self._heartbeat_monitor()
                )

                _LOGGER.info("Connected to Lumina Observer")

                async for raw in ws:
                    self._last_message_time = asyncio.get_running_loop().time()
                    try:
                        # websockets may yield str or bytes depending on version
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        msg = json.loads(raw)
                    except Exception:
                        _LOGGER.warning("Failed to parse message: %s", raw)
                        continue

                    if msg.get("type") == "heartbeat":
                        _LOGGER.debug("Heartbeat received")
                    elif msg.get("type") == "prediction":
                        _LOGGER.debug("Prediction received: score=%s", msg.get("prediction", {}).get("score"))
                        self._on_prediction(msg)
                    else:
                        _LOGGER.debug("Unknown message type: %s", msg.get("type"))

        except ConnectionClosed as exc:
            _LOGGER.warning("WebSocket connection closed: %s", exc)
        except WebSocketException as exc:
            _LOGGER.error("WebSocket error: %s", exc)
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOGGER.exception("Unexpected connection error")
        finally:
            self._ws = None
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                self._heartbeat_task = None
            if self._on_status_change:
                self._on_status_change(False)

    async def _heartbeat_monitor(self) -> None:
        """Monitor heartbeat and force reconnect if no message received."""
        try:
            while not self._shutdown:
                await asyncio.sleep(HEARTBEAT_TIMEOUT)
                elapsed = asyncio.get_running_loop().time() - self._last_message_time
                if elapsed > HEARTBEAT_TIMEOUT and self._ws:
                    _LOGGER.warning(
                        "No message received for %ds, reconnecting...", int(elapsed)
                    )
                    await self._ws.close()
                    return
        except asyncio.CancelledError:
            pass
