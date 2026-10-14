"""Binary sensors for Tapo C260 Face Recognition."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .const import ATTR_RECOGNIZED
from .coordinator import TapoC260Coordinator
from .entity import TapoC260Entity, TapoC260HealthEntity


class TapoC260RecognizedBinarySensor(
    TapoC260Entity, BinarySensorEntity
):
    """Whether the current Face ID is configured/recognized."""

    _attr_icon = "mdi:face-recognition"
    _attr_name = "Face Recognized"

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.entry.entry_id}_face_recognized"
        )

    @property
    def is_on(self) -> bool:
        return bool(
            self.coordinator.current.get(ATTR_RECOGNIZED, False)
        )


class TapoC260StrangerBinarySensor(TapoC260Entity, BinarySensorEntity):
    """On khi vừa thấy người lạ; tự tắt sau `stranger_clear_seconds`."""

    _attr_icon = "mdi:account-alert"
    _attr_name = "Stranger Detected"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_stranger_detected"

    @property
    def is_on(self) -> bool:
        return self.coordinator.stranger_active

    @property
    def extra_state_attributes(self) -> dict:
        return {"clear_after_seconds": self.coordinator.stranger_clear_seconds}


class TapoC260ConnectionBinarySensor(TapoC260HealthEntity, BinarySensorEntity):
    """On = poll gần đây thành công (hoặc đang chờ Tapo-Control); Off = mất kết nối."""

    _attr_name = "Camera Connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_connection"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.health()["connected"])

    @property
    def extra_state_attributes(self) -> dict:
        health = self.coordinator.health()
        return {
            "status": health["status"],
            "last_error": health["last_error"],
            "consecutive_failures": health["consecutive_failures"],
        }


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up recognized binary sensor."""
    coordinator: TapoC260Coordinator = entry.runtime_data
    async_add_entities(
        [
            TapoC260RecognizedBinarySensor(coordinator),
            TapoC260StrangerBinarySensor(coordinator),
            TapoC260ConnectionBinarySensor(coordinator),
        ]
    )
