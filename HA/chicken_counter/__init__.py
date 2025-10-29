"""The Chicken Counter integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import ChickenCounterCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CAMERA, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chicken Counter from a config entry."""

    # Create coordinator
    coordinator = ChickenCounterCoordinator(hass, entry)

    # Initialize the model
    try:
        await coordinator.async_initialize()
    except Exception as err:
        _LOGGER.error("Failed to initialize chicken counter: %s", err)
        raise ConfigEntryNotReady from err

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_count_chickens(call):
        """Handle the count_chickens service call."""
        camera_entity = call.data.get("camera_entity")

        if not camera_entity:
            _LOGGER.error("No camera_entity provided")
            return

        await coordinator.count_chickens(camera_entity)

    hass.services.async_register(
        DOMAIN,
        "count_chickens",
        handle_count_chickens,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok