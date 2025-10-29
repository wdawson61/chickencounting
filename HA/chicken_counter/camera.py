"""Camera platform for Chicken Counter."""
from __future__ import annotations

import io
import logging

from homeassistant.components.camera import Camera
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
    """Set up the camera platform."""
    coordinator: ChickenCounterCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([ChickenCounterCamera(coordinator, entry)])


class ChickenCounterCamera(CoordinatorEntity, Camera):
    """Camera entity showing annotated chicken detections."""

    def __init__(
            self,
            coordinator: ChickenCounterCoordinator,
            entry: ConfigEntry,
    ) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        Camera.__init__(self)

        self._attr_name = "Chicken Detection Camera"
        self._attr_unique_id = f"{entry.entry_id}_detection_camera"
        self._attr_brand = "Chicken Counter"
        self._attr_model = "YOLOv12 Detection"

    async def async_camera_image(
            self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return image with chicken detections."""
        if self.coordinator.last_image is None:
            return None

        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        self.coordinator.last_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        attrs = {
            "chicken_count": self.coordinator.last_count,
        }

        if self.coordinator.last_detection_time:
            attrs["last_detection"] = self.coordinator.last_detection_time.isoformat()

        return attrs