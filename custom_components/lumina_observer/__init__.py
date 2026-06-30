"""Lumina Observer integration for Home Assistant.

Provides real-time aurora prediction data via WebSocket streaming from
lumina.observer for Australian and New Zealand aurora hunters.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .websocket import LuminaWebSocketClient

# Pre-import platforms to avoid blocking import_module in the event loop
from . import sensor, binary_sensor  # noqa: F401

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


class LuminaData:
    """Holds the latest prediction data and manages the WebSocket client."""

    def __init__(
        self,
        hass: HomeAssistant,
        latitude: float,
        longitude: float,
        api_key: str,
    ) -> None:
        """Initialize the data container."""
        self.hass = hass
        self.latitude = latitude
        self.longitude = longitude
        self.api_key = api_key
        self._raw: dict | None = None
        self._listeners: list[Callable[[], None]] = []

        self.client = LuminaWebSocketClient(
            latitude=latitude,
            longitude=longitude,
            api_key=api_key,
            on_prediction=self._handle_prediction,
        )

    @property
    def prediction(self) -> dict | None:
        """Return the nested prediction dict."""
        if self._raw:
            return self._raw.get("prediction")
        return None

    @property
    def conditions(self) -> dict | None:
        """Return the conditions dict."""
        if self._raw:
            return self._raw.get("conditions")
        return None

    @property
    def sqm(self) -> float | None:
        """Return the SQM value."""
        if self._raw:
            return self._raw.get("sqm")
        return None

    @property
    def last_ts(self) -> datetime | None:
        """Return the timestamp as a datetime object."""
        ts = self._raw.get("ts") if self._raw else None
        if ts:
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        return None

    def _handle_prediction(self, msg: dict) -> None:
        """Handle an incoming prediction message from the WebSocket."""
        self._raw = msg
        # Schedule entity updates on the HA event loop
        for listener in self._listeners:
            listener()

    def register_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a listener that is called on new data.

        Returns a callable that unregisters the listener.
        """
        self._listeners.append(listener)

        def remove() -> None:
            self._listeners.remove(listener)

        return remove

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the device registry."""
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self.latitude}_{self.longitude}")},
            name=f"Lumina Observer ({self.latitude:.1f}, {self.longitude:.1f})",
            manufacturer="Lumina Observer",
            model="Aurora Prediction Stream",
            configuration_url="https://lumina.observer",
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lumina Observer from a config entry."""
    data = LuminaData(
        hass=hass,
        latitude=entry.data["latitude"],
        longitude=entry.data["longitude"],
        api_key=entry.data["api_key"],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await data.client.connect()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data: LuminaData = hass.data[DOMAIN].pop(entry.entry_id)
    await data.client.disconnect()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
