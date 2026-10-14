"""Event entity: mỗi lần camera thấy một khuôn mặt MỚI."""
from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.core import callback

from .const import (
    ATTR_ALARM_TYPE,
    ATTR_CAMERA,
    ATTR_EVENT_TIME,
    ATTR_FACE_ID,
    ATTR_NAME,
    ATTR_RECOGNIZED,
)
from .coordinator import TapoC260Coordinator
from .entity import TapoC260Entity

EVENT_RECOGNIZED = "face_recognized"
EVENT_UNKNOWN = "face_unknown"


class TapoC260FaceEvent(TapoC260Entity, EventEntity):
    """Dùng làm trigger trong automation UI: "Face Event" → face_recognized / face_unknown."""

    _attr_icon = "mdi:face-recognition"
    _attr_name = "Face Event"
    _attr_event_types = [EVENT_RECOGNIZED, EVENT_UNKNOWN]

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_face_event"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_face_listener(self._handle_face)
        )

    @callback
    def _handle_face(self, payload: dict[str, Any]) -> None:
        event_type = EVENT_RECOGNIZED if payload.get(ATTR_RECOGNIZED) else EVENT_UNKNOWN
        self._trigger_event(
            event_type,
            {
                key: payload.get(key)
                for key in (
                    ATTR_FACE_ID,
                    ATTR_NAME,
                    ATTR_RECOGNIZED,
                    ATTR_EVENT_TIME,
                    ATTR_ALARM_TYPE,
                    ATTR_CAMERA,
                )
            },
        )
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the face event entity."""
    async_add_entities([TapoC260FaceEvent(entry.runtime_data)])
