"""Config flow for Chicken Counter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MODEL_PATH,
    CONF_CONFIDENCE,
    CONF_DEVICE,
    DEFAULT_CONFIDENCE,
    DEFAULT_DEVICE,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODEL_PATH): str,
        vol.Optional(CONF_CONFIDENCE, default=DEFAULT_CONFIDENCE): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=1.0)
        ),
        vol.Optional(CONF_DEVICE, default=DEFAULT_DEVICE): vol.In(["cpu", "cuda"]),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chicken Counter."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate model path exists
            model_path = user_input[CONF_MODEL_PATH]

            # You could add validation here to check if model file exists
            # For now, we'll just accept it

            return self.async_create_entry(
                title="Chicken Counter",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )