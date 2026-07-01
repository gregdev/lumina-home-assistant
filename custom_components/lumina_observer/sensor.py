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
    # -- Probability & Colour --
    LuminaSensorDescription(
        key="aurora_probability_field",
        translation_key="aurora_probability_field",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:forest",
        value_fn=lambda d: (
            round(d.prediction["auroraProbabilityField"] * 100)
            if d.prediction and "auroraProbabilityField" in d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="aurora_probability_plan",
        translation_key="aurora_probability_plan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:sofa-single",
        value_fn=lambda d: (
            round(d.prediction["auroraProbabilityFinal"] * 100)
            if d.prediction and "auroraProbabilityFinal" in d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="aurora_score",
        translation_key="aurora_score",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-lightning",
        value_fn=lambda d: d.prediction.get("score") if d.prediction else None,
    ),
    LuminaSensorDescription(
        key="aurora_confidence",
        translation_key="aurora_confidence",
        icon="mdi:sigma",
        value_fn=lambda d: (
            d.prediction.get("confidence") if d.prediction else None
        ),
    ),
    # -- Solar Wind & IMF --
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
        key="dynamic_pressure",
        translation_key="dynamic_pressure",
        native_unit_of_measurement="nPa",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:gauge",
        value_fn=lambda d: (
            d.conditions.get("pressure", {}).get("pressure")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="kp_index",
        translation_key="kp_index",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:earth",
        value_fn=lambda d: (
            d.conditions.get("kp", {}).get("kp")
            if d.conditions
            else None
        ),
    ),
    # -- Geospace & Magnetotail --
    LuminaSensorDescription(
        key="hemispheric_power",
        translation_key="hemispheric_power",
        native_unit_of_measurement="GW",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        value_fn=lambda d: (
            d.conditions.get("hemisphericPower", {}).get("south")
            if d.conditions
            else None
        ),
    ),
    LuminaSensorDescription(
        key="magnetotail_energy",
        translation_key="magnetotail_energy",
        icon="mdi:atom-variant",
        value_fn=lambda d: (
            d.prediction.get("magnetotailEnergyState", {}).get("state")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="field_outlook",
        translation_key="field_outlook",
        icon="mdi:compass-outline",
        value_fn=lambda d: (
            d.prediction.get("fieldOutlook", {}).get("state")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="estimated_storm_level",
        translation_key="estimated_storm_level",
        icon="mdi:weather-hurricane",
        value_fn=lambda d: (
            d.prediction.get("estimatedStormLevel", {}).get("gScale")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="substorm_probability",
        translation_key="substorm_probability",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:lightning-bolt",
        value_fn=lambda d: (
            round(d.prediction["substormAssessment"]["probability"] * 100)
            if d.prediction and "substormAssessment" in d.prediction
            else None
        ),
    ),
    # -- Visibility & Geometry --
    LuminaSensorDescription(
        key="sky_quality",
        translation_key="sky_quality",
        native_unit_of_measurement="mag/arcsec²",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        icon="mdi:weather-night",
        value_fn=lambda d: d.sqm,
    ),
    LuminaSensorDescription(
        key="oval_distance",
        translation_key="oval_distance",
        native_unit_of_measurement="km",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:map-marker-distance",
        value_fn=lambda d: (
            d.prediction.get("ovalDistanceKm") if d.prediction else None
        ),
    ),
    LuminaSensorDescription(
        key="visibility_factor",
        translation_key="visibility_factor",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon="mdi:eye",
        value_fn=lambda d: (
            round(d.prediction["visibilityFactor"] * 100)
            if d.prediction and "visibilityFactor" in d.prediction
            else None
        ),
    ),
    # -- Events & Warnings --
    LuminaSensorDescription(
        key="incoming_cme_count",
        translation_key="incoming_cme_count",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meteor",
        value_fn=lambda d: (
            len(d.prediction.get("upcomingCmeImpacts", []))
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="coronal_hole_hss",
        translation_key="coronal_hole_hss",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:white-balance-sunny",
        value_fn=lambda d: (
            d.prediction.get("upcomingCoronalHoleHss", {}).get("daysToArrival")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="cme_shock_detected",
        translation_key="cme_shock_detected",
        icon="mdi:alert-decagram",
        value_fn=lambda d: (
            d.prediction.get("cmeShockArrival", {}).get("detected")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="proton_precursor",
        translation_key="proton_precursor",
        icon="mdi:atom",
        value_fn=lambda d: (
            d.prediction.get("energeticProtonPrecursor", {}).get("detected")
            if d.prediction
            else None
        ),
    ),
    LuminaSensorDescription(
        key="pressure_pulse_active",
        translation_key="pressure_pulse_active",
        icon="mdi:pulse",
        value_fn=lambda d: (
            d.prediction.get("pressurePulseActive") if d.prediction else None
        ),
    ),
    LuminaSensorDescription(
        key="hss_arrival",
        translation_key="hss_arrival",
        icon="mdi:arrow-decision",
        value_fn=lambda d: (
            d.prediction.get("hssArrival", {}).get("detected")
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
        """Return additional attributes for sensors that have them."""
        prediction = self._data.prediction
        conditions = self._data.conditions
        key = self.entity_description.key

        # -- Probability & Colour --
        if key == "aurora_probability_field":
            return {
                "intensity_colour": prediction.get("intensityColourField") if prediction else None,
            }
        if key == "aurora_probability_plan":
            return {
                "intensity_colour": prediction.get("intensityColourPlan") if prediction else None,
            }
        if key == "aurora_score":
            if not prediction:
                return None
            return {
                "confidence": prediction.get("confidence"),
                "worth_driving": prediction.get("worthDriving"),
                "data_confidence": prediction.get("dataConfidence"),
            }
        if key == "aurora_confidence":
            if not prediction:
                return None
            return {
                "data_confidence": prediction.get("dataConfidence"),
            }

        # -- Solar Wind & IMF --
        if key == "solar_wind_speed":
            wind = conditions.get("solarWind", {}) if conditions else {}
            return {
                "density": wind.get("density"),
                "temperature": wind.get("temperature"),
            }
        if key == "imf_bz":
            imf = conditions.get("imf", {}) if conditions else {}
            return {
                "bt": imf.get("bt"),
                "bx": imf.get("bx"),
                "by": imf.get("by"),
                "field_bz": prediction.get("fieldCurrentBz") if prediction else None,
            }
        if key == "dynamic_pressure":
            return {
                "high_pdyn_active": prediction.get("highPdynActive") if prediction else None,
            }
        if key == "kp_index":
            kp = conditions.get("kp", {}) if conditions else {}
            return {
                "estimated": kp.get("estimated"),
                "estimated_storm_g_scale": kp.get("estimatedStormGScale"),
            }

        # -- Geospace & Magnetotail --
        if key == "hemispheric_power":
            hp = conditions.get("hemisphericPower", {}) if conditions else {}
            return {
                "north": hp.get("north"),
            }
        if key == "magnetotail_energy":
            mes = prediction.get("magnetotailEnergyState", {}) if prediction else {}
            return {
                "score": mes.get("score"),
                "balance": mes.get("balance"),
                "input_score": mes.get("inputScore"),
                "release_score": mes.get("releaseScore"),
                "trend": mes.get("trend"),
            }
        if key == "field_outlook":
            fo = prediction.get("fieldOutlook", {}) if prediction else {}
            return {
                "narrative": fo.get("narrative"),
                "ground_data_available": fo.get("groundDataAvailable"),
            }
        if key == "estimated_storm_level":
            esl = prediction.get("estimatedStormLevel", {}) if prediction else {}
            return {
                "estimated_kp": esl.get("estimatedKp"),
                "confidence": esl.get("confidence"),
                "sources": esl.get("sources"),
            }
        if key == "substorm_probability":
            sa = prediction.get("substormAssessment", {}) if prediction else {}
            return {
                "alert_level": sa.get("alertLevel"),
                "label": sa.get("label"),
                "expansion_low_min": sa.get("expansionLowMin"),
                "expansion_high_min": sa.get("expansionHighMin"),
                "has_mag_signal": sa.get("hasMagSignal"),
            }

        # -- Visibility & Geometry --
        if key == "oval_distance":
            if not prediction:
                return None
            return {
                "elevation_deg": prediction.get("ovalElevationDeg"),
                "geomagnetic_lat": prediction.get("geomagneticLat"),
            }
        if key == "visibility_factor":
            if not prediction:
                return None
            return {
                "geometric_factor": prediction.get("geometricFactor"),
                "ovation_flux": prediction.get("ovationFlux"),
            }

        # -- Events & Warnings --
        if key == "incoming_cme_count":
            if not prediction:
                return None
            return {
                "impacts": prediction.get("upcomingCmeImpacts"),
            }
        if key == "coronal_hole_hss":
            ch = prediction.get("upcomingCoronalHoleHss", {}) if prediction else {}
            return {
                "estimated_arrival": ch.get("estimatedArrival"),
                "hemisphere": ch.get("hemisphere"),
                "area_km2": ch.get("areaKm2"),
            }
        if key == "cme_shock_detected":
            cs = prediction.get("cmeShockArrival", {}) if prediction else {}
            return {
                "confidence_level": cs.get("confidenceLevel"),
                "speed_jump_kms": cs.get("speedJumpKms"),
                "pressure_jump_npa": cs.get("pressureJumpNpa"),
            }
        if key == "proton_precursor":
            ep = prediction.get("energeticProtonPrecursor", {}) if prediction else {}
            return {
                "confidence": ep.get("confidence"),
                "flux_ratio": ep.get("fluxRatio"),
                "detail": ep.get("detail"),
            }
        if key == "pressure_pulse_active":
            return {
                "high_pdyn_active": prediction.get("highPdynActive") if prediction else None,
            }
        if key == "hss_arrival":
            ha = prediction.get("hssArrival", {}) if prediction else {}
            return {
                "current_speed_kms": ha.get("currentSpeedKms"),
                "delta_kms": ha.get("deltaKms"),
            }

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
