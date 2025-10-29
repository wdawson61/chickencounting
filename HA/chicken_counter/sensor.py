"""Sensor platform for Chicken Counter."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChickenCounterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: ChickenCounterCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([ChickenCountSensor(coordinator, entry)])


class ChickenCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for chicken count."""

    def __init__(
            self,
            coordinator: ChickenCounterCoordinator,
            entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Chicken Count"
        self._attr_unique_id = f"{entry.entry_id}_chicken_count"
        self._attr_native_unit_of_measurement = "chickens"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:chicken"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.last_count

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        attrs = {}

        if self.coordinator.last_detection_time:
            attrs["last_detection"] = self.coordinator.last_detection_time.isoformat()

        if self.coordinator.data:
            attrs["detection_count"] = len(self.coordinator.data.get("detections", []))

        return attrs