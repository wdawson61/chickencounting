"""Coordinator for Chicken Counter integration."""
from __future__ import annotations

import io
import logging
from datetime import datetime

from PIL import Image
from ultralytics import YOLO

from homeassistant.components.camera import async_get_image
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_MODEL_PATH,
    CONF_CONFIDENCE,
    CONF_DEVICE,
)

_LOGGER = logging.getLogger(__name__)


class ChickenCounterCoordinator(DataUpdateCoordinator):
    """Coordinator to manage chicken counting."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self.entry = entry
        self.model = None
        self._last_count = 0
        self._last_image = None
        self._last_detection_time = None

    async def async_initialize(self) -> None:
        """Initialize the YOLO model."""
        model_path = self.entry.data[CONF_MODEL_PATH]
        device = self.entry.data.get(CONF_DEVICE, "cpu")

        _LOGGER.info("Loading YOLO model from %s", model_path)

        # Load model in executor since it's CPU intensive
        self.model = await self.hass.async_add_executor_job(
            self._load_model, model_path, device
        )

        _LOGGER.info("YOLO model loaded successfully")

    def _load_model(self, model_path: str, device: str) -> YOLO:
        """Load YOLO model (runs in executor)."""
        model = YOLO(model_path)
        model.to(device)
        return model

    async def count_chickens(self, camera_entity: str) -> dict:
        """Count chickens from camera image."""
        try:
            # Get camera image
            _LOGGER.debug("Fetching image from %s", camera_entity)
            image_data = await async_get_image(self.hass, camera_entity)

            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data.content))

            # Run inference
            _LOGGER.debug("Running YOLO inference")
            results = await self.hass.async_add_executor_job(
                self._run_inference, image
            )

            # Process results
            count = len(results["detections"])
            annotated_image = results["annotated_image"]

            # Update state
            self._last_count = count
            self._last_image = annotated_image
            self._last_detection_time = datetime.now()

            # Notify listeners
            self.async_set_updated_data({
                "count": count,
                "detections": results["detections"],
                "timestamp": self._last_detection_time,
            })

            _LOGGER.info("Detected %d chickens", count)

            # Fire event for automations
            self.hass.bus.async_fire(
                f"{DOMAIN}_detection_complete",
                {
                    "count": count,
                    "camera_entity": camera_entity,
                    "timestamp": self._last_detection_time.isoformat(),
                },
            )

            return {
                "count": count,
                "detections": results["detections"],
            }

        except Exception as err:
            _LOGGER.error("Error counting chickens: %s", err)
            raise

    def _run_inference(self, image: Image.Image) -> dict:
        """Run YOLO inference (runs in executor)."""
        confidence = self.entry.data.get(CONF_CONFIDENCE, 0.5)

        # Run prediction
        results = self.model.predict(
            image,
            conf=confidence,
            verbose=False,
        )

        # Get annotated image
        annotated = results[0].plot()

        # Convert BGR to RGB
        annotated_rgb = Image.fromarray(annotated[..., ::-1])

        # Extract detections
        detections = []
        for box in results[0].boxes:
            detections.append({
                "confidence": float(box.conf[0]),
                "class": int(box.cls[0]),
                "bbox": box.xyxy[0].tolist(),
            })

        return {
            "detections": detections,
            "annotated_image": annotated_rgb,
        }

    @property
    def last_count(self) -> int:
        """Return last chicken count."""
        return self._last_count

    @property
    def last_image(self) -> Image.Image | None:
        """Return last annotated image."""
        return self._last_image

    @property
    def last_detection_time(self) -> datetime | None:
        """Return last detection time."""
        return self._last_detection_time