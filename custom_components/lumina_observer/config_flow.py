"""Config flow for Lumina Observer integration."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE

from .const import DOMAIN

API_KEY_RE = re.compile(r"^lumina_[A-Za-z0-9_-]+$")

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LATITUDE, default=-35.0): vol.Coerce(float),
        vol.Required(CONF_LONGITUDE, default=149.0): vol.Coerce(float),
        vol.Required(CONF_API_KEY): str,
    }
)


class LuminaObserverConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lumina Observer."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate latitude
            lat = user_input[CONF_LATITUDE]
            if not -90 <= lat <= 90:
                errors[CONF_LATITUDE] = "invalid_latitude"

            # Validate longitude
            lng = user_input[CONF_LONGITUDE]
            if not -180 <= lng <= 180:
                errors[CONF_LONGITUDE] = "invalid_longitude"

            # Validate API key prefix
            api_key = user_input[CONF_API_KEY].strip()
            if not API_KEY_RE.match(api_key):
                errors[CONF_API_KEY] = "invalid_api_key"

            if not errors:
                await self.async_set_unique_id(
                    f"lumina_{lat}_{lng}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Lumina ({lat:.1f}, {lng:.1f})",
                    data={
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lng,
                        CONF_API_KEY: api_key,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=SCHEMA,
            errors=errors,
            description_placeholders={
                "api_url": "https://lumina.observer",
            },
        )
