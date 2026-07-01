"""Sensor entities for Lumina Observer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LuminaData
from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class LuminaSensorDescription(SensorEntityDescription):
    """Description for a Lumina sensor entity."""

    value_fn: callable[[LuminaData], Any]


SENSORS: tuple[LuminaSensorDescription, ...] = (
    LuminaSensorDescription(
        key="score",
        translation_key="score",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-lightning",
        value_fn=lambda d: d.prediction.get("score") if d.prediction else None,
    ),
    LuminaSensorDescription(
        key="aurora_probability_field",
        translation_key="aurora_probability_field",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:weather-aurora",
        value_fn=lambda d: (
            round(d.prediction["auroraProbabilityField"] * 100, 1)
            if d.prediction and "auroraProbabilityField" in d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="aurora_probability_plan",
        translation_key="aurora_probability_plan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:road-variant",
        value_fn=lambda d: (
            round(d.prediction["auroraProbabilityPlan"] * 100, 1)
            if d.prediction and "auroraProbabilityPlan" in d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="solar_wind_speed",
        translation_key="solar_wind_speed",
        native_unit_of_measurement="km/s",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda d: (
            d.conditions.get("solarWind", {}).get("speed")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="solar_wind_density",
        translation_key="solar_wind_density",
        native_unit_of_measurement="p/cm³",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:blur",
        value_fn=lambda d: (
            d.conditions.get("solarWind", {}).get("density")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="imf_bz",
        translation_key="imf_bz",
        native_unit_of_measurement="nT",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:magnet",
        value_fn=lambda d: (
            d.conditions.get("imf", {}).get("bz")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="imf_bt",
        translation_key="imf_bt",
        native_unit_of_measurement="nT",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:magnet-on",
        value_fn=lambda d: (
            d.conditions.get("imf", {}).get("bt")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="hemispheric_power",
        translation_key="hemispheric_power",
        native_unit_of_measurement="GW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        value_fn=lambda d: (
            d.conditions.get("hemisphericPower", {}).get("value")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="sqm",
        translation_key="sqm",
        native_unit_of_measurement="mag/arcsec²",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:weather-night",
        value_fn=lambda d: d.sqm,
    ),
    LuminaSensorDescription(
        key="confidence",
        translation_key="confidence",
        icon="mdi:sigma",
        value_fn=lambda d: (
            d.prediction.get("confidence") if d.prediction else None
        ),
    ),
    LuminaSensorDescription(
        key="magnetotail_energy_state",
        translation_key="magnetotail_energy_state",
        icon="mdi:atom-variant",
        value_fn=lambda d: (
            d.prediction.get("magnetotailEnergyState", {}).get("state")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="magnetotail_energy_ratio",
        translation_key="magnetotail_energy_ratio",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        icon="mdi:chart-bell-curve",
        value_fn=lambda d: (
            d.prediction.get("magnetotailEnergyState", {}).get("energyRatio")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="upcoming_cme_count",
        translation_key="upcoming_cme_count",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meteor",
        value_fn=lambda d: (
            len(d.prediction.get("upcomingCmeImpacts", []))
            if d.prediction
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lumina Observer sensors from a config entry."""
    data: LuminaData = hass.data[DOMAIN][entry.entry_id]

    entities = [LuminaSensor(data, desc) for desc in SENSORS]
    async_add_entities(entities)


class LuminaSensor(SensorEntity):
    """Representation of a Lumina Observer sensor."""

    _attr_has_entity_name = True
    entity_description: LuminaSensorDescription

    def __init__(
        self, data: LuminaData, description: LuminaSensorDescription
    ) -> None:
        """Initialize the sensor."""
        self._data = data
        self.entity_description = description
        self._attr_unique_id = f"{data.latitude}_{data.longitude}_{description.key}"
        self._attr_device_info = data.device_info
        self._remove_listener = data.register_listener(self._on_update)

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self._data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for the score sensor."""
        if self.entity_description.key != "score":
            return None
        prediction = self._data.prediction
        if not prediction:
            return None
        return {
            "confidence": prediction.get("confidence"),
            "worth_driving": prediction.get("worthDriving"),
            "magnetotail_state": prediction.get("magnetotailEnergyState", {}).get("state"),
            "magnetotail_energy_ratio": prediction.get("magnetotailEnergyState", {}).get("energyRatio"),
            "upcoming_cme_count": len(prediction.get("upcomingCmeImpacts", [])),
            "field_probability_pct": (
                round(prediction["auroraProbabilityField"] * 100, 1)
                if "auroraProbabilityField" in prediction
                else None
            ),
            "plan_probability_pct": (
                round(prediction["auroraProbabilityPlan"] * 100, 1)
                if "auroraProbabilityPlan" in prediction
                else None
            ),
        }

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
