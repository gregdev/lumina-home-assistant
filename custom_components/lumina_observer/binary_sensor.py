"""Binary sensor entities for Lumina Observer."""

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

_SUBSTORM_ACTIVE_LEVELS = {"likely", "imminent", "active"}


class LuminaBinarySensor(BinarySensorEntity):
    """Base binary sensor for Lumina Observer."""

    _attr_has_entity_name = True

    def __init__(
        self,
        data: LuminaData,
        description: BinarySensorEntityDescription,
        is_on_fn: callable[[LuminaData], bool | None],
    ) -> None:
        """Initialize the binary sensor."""
        self._data = data
        self.entity_description = description
        self._is_on_fn = is_on_fn
        self._attr_unique_id = f"{data.latitude}_{data.longitude}_{description.key}"
        self._attr_device_info = data.device_info
        self._remove_listener = data.register_listener(self._on_update)

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        return self._is_on_fn(self._data)

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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lumina Observer binary sensors from a config entry."""
    data: LuminaData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        LuminaBinarySensor(
            data,
            BinarySensorEntityDescription(
                key="worth_driving",
                translation_key="worth_driving",
                icon="mdi:car-side",
            ),
            lambda d: d.prediction.get("worthDriving") if d.prediction else None,
        ),
        LuminaBinarySensor(
            data,
            BinarySensorEntityDescription(
                key="substorm_active",
                translation_key="substorm_active",
                icon="mdi:lightning-bolt-circle",
            ),
            lambda d: (
                d.prediction.get("substormAssessment", {}).get("alertLevel")
                in _SUBSTORM_ACTIVE_LEVELS
                if d.prediction
                else None
            ),
        ),
        LuminaBinarySensor(
            data,
            BinarySensorEntityDescription(
                key="cme_incoming",
                translation_key="cme_incoming",
                icon="mdi:meteor",
            ),
            lambda d: (
                len(d.prediction.get("upcomingCmeImpacts", [])) > 0
                if d.prediction
                else None
            ),
        ),
        LuminaBinarySensor(
            data,
            BinarySensorEntityDescription(
                key="bz_southward",
                translation_key="bz_southward",
                icon="mdi:magnet-on",
            ),
            lambda d: (
                d.conditions.get("imf", {}).get("bz", 0) < -3
                if d.conditions
                else None
            ),
        ),
    ]
    async_add_entities(entities)
