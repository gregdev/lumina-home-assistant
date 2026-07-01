"""Binary sensor entity for Lumina Observer."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LuminaData
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lumina Observer binary sensors from a config entry."""
    data: LuminaData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuminaWorthDrivingBinarySensor(data)])


class LuminaWorthDrivingBinarySensor(BinarySensorEntity):
    """Binary sensor for the worth_driving recommendation."""

    _attr_has_entity_name = True
    entity_description = BinarySensorEntityDescription(
        key="worth_driving",
        translation_key="worth_driving",
        icon="mdi:car-side",
    )

    def __init__(self, data: LuminaData) -> None:
        """Initialize the binary sensor."""
        self._data = data
        self._attr_unique_id = f"{data.latitude}_{data.longitude}_worth_driving"
        self._attr_device_info = data.device_info
        self._remove_listener = data.register_listener(self._on_update)

    @property
    def is_on(self) -> bool | None:
        """Return True if it's worth driving."""
        if self._data.prediction:
            return self._data.prediction.get("worthDriving")
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._data.prediction is not None

    def _on_update(self) -> None:
        """Handle updated data from the WebSocket."""
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        self._remove_listener()
