"""Sensors for Tapo C260 Face Recognition."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime

from .const import (
    ATTR_ALARM_TYPE,
    ATTR_CAMERA,
    ATTR_END_TIME,
    ATTR_EVENT_TIME,
    ATTR_EVENTS_1,
    ATTR_FACE_ID,
    ATTR_NAME,
    ATTR_RECOGNIZED,
    ATTR_START_TIME,
    DEFAULT_FACE_NAME,
)
from .coordinator import TapoC260Coordinator
from .entity import TapoC260Entity, TapoC260HealthEntity


class TapoC260FaceNameSensor(TapoC260Entity, SensorEntity):
    """Current detected face name."""

    _attr_icon = "mdi:face-recognition"
    _attr_name = "Face Name"

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_face_name"

    @property
    def native_value(self) -> str:
        return str(self.coordinator.current.get(ATTR_NAME, DEFAULT_FACE_NAME))

    @property
    def extra_state_attributes(self) -> dict:
        return dict(self.coordinator.current)


class TapoC260FaceIdSensor(TapoC260Entity, SensorEntity):
    """Current detected Face ID."""

    _attr_icon = "mdi:identifier"
    _attr_name = "Face ID"

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_face_id"

    @property
    def native_value(self) -> str | None:
        value = self.coordinator.current.get(ATTR_FACE_ID)
        return None if value is None else str(value)

    @property
    def extra_state_attributes(self) -> dict:
        return dict(self.coordinator.current)


class TapoC260LastSeenSensor(TapoC260Entity, SensorEntity):
    """ISO timestamp of the last processed face event."""

    _attr_icon = "mdi:clock-outline"
    _attr_name = "Last Seen"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_last_seen"

    @property
    def native_value(self) -> datetime | None:
        value = self.coordinator.current.get(ATTR_EVENT_TIME)
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "face_id": self.coordinator.current.get(ATTR_FACE_ID),
            "name": self.coordinator.current.get(ATTR_NAME),
            "recognized": self.coordinator.current.get(ATTR_RECOGNIZED),
            "start_time": self.coordinator.current.get(ATTR_START_TIME),
            "end_time": self.coordinator.current.get(ATTR_END_TIME),
            "alarm_type": self.coordinator.current.get(ATTR_ALARM_TYPE),
            "events_1": self.coordinator.current.get(ATTR_EVENTS_1),
            "camera": self.coordinator.current.get(ATTR_CAMERA),
        }


class TapoC260KnownFacesSensor(TapoC260Entity, SensorEntity):
    """Number of configured known faces."""

    _attr_icon = "mdi:account-check"
    _attr_name = "Known Faces"

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_known_faces"

    @property
    def native_value(self) -> int:
        return self.coordinator.known_face_count

    @property
    def extra_state_attributes(self) -> dict:
        return {"faces": dict(self.coordinator.faces)}


class TapoC260UnknownFacesSensor(TapoC260Entity, SensorEntity):
    """Number of discovered unknown faces."""

    _attr_icon = "mdi:account-question"
    _attr_name = "Unknown Faces"

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_unknown_faces"

    @property
    def native_value(self) -> int:
        return coordinator.unknown_face_count if (coordinator := self.coordinator) else 0

    @property
    def extra_state_attributes(self) -> dict:
        return {"faces": dict(self.coordinator.unknown_faces)}


class TapoC260UnknownTodaySensor(TapoC260Entity, SensorEntity):
    """Số lần người lạ xuất hiện hôm nay (reset lúc 0h giờ địa phương)."""

    _attr_icon = "mdi:account-clock"
    _attr_name = "Unknown Today"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_unknown_today"

    @property
    def native_value(self) -> int:
        return self.coordinator.unknown_today


class TapoC260LastUnknownSeenSensor(TapoC260Entity, SensorEntity):
    """Lần cuối camera thấy người lạ (từ lúc có lịch sử)."""

    _attr_icon = "mdi:clock-alert-outline"
    _attr_name = "Last Unknown Seen"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_last_unknown_seen"

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_unknown_seen


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class TapoC260LastPollSensor(TapoC260HealthEntity, SensorEntity):
    """Lần poll thành công gần nhất."""

    _attr_icon = "mdi:check-network-outline"
    _attr_name = "Last Successful Poll"
    # Đổi mỗi lần poll → mặc định tắt để khỏi spam recorder; xem trong Face Manager.
    _attr_entity_registry_enabled_default = False
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_last_poll"

    @property
    def native_value(self) -> datetime | None:
        return _parse(self.coordinator.health()["last_success"])

    @property
    def extra_state_attributes(self) -> dict:
        return {"last_attempt": self.coordinator.health()["last_attempt"]}


class TapoC260ResponseTimeSensor(TapoC260HealthEntity, SensorEntity):
    """Thời gian camera (hoặc controller dùng chung) trả lời lần poll gần nhất."""

    _attr_icon = "mdi:timer-outline"
    _attr_name = "Response Time"
    _attr_entity_registry_enabled_default = False
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MILLISECONDS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_response_time"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.health()["response_ms"]


class TapoC260PollErrorsSensor(TapoC260HealthEntity, SensorEntity):
    """Số lần poll lỗi LIÊN TIẾP (0 = bình thường)."""

    _attr_icon = "mdi:alert-circle-outline"
    _attr_name = "Polling Errors"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_poll_errors"

    @property
    def native_value(self) -> int:
        return self.coordinator.health()["consecutive_failures"]

    @property
    def extra_state_attributes(self) -> dict:
        health = self.coordinator.health()
        return {
            "total_failures": health["total_failures"],
            "last_error": health["last_error"],
            "last_error_time": health["last_error_time"],
        }


class TapoC260ModeSensor(TapoC260HealthEntity, SensorEntity):
    """Đang dùng controller chung của Tapo-Control hay session riêng."""

    _attr_icon = "mdi:link-variant"
    _attr_name = "Connection Mode"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["shared", "standalone", "wait", "starting"]

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode"

    @property
    def native_value(self) -> str:
        mode = self.coordinator.health()["mode"]
        return mode if mode in self._attr_options else "starting"


class TapoC260DedupSkippedSensor(TapoC260HealthEntity, SensorEntity):
    """Số event người quen đã bỏ qua do dedup (từ lúc integration khởi động)."""

    _attr_icon = "mdi:filter-remove-outline"
    _attr_name = "Dedup Skipped"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_dedup_skipped"

    @property
    def native_value(self) -> int:
        return self.coordinator.health()["dedup_skipped"]

    @property
    def extra_state_attributes(self) -> dict:
        return {"events_processed": self.coordinator.health()["events_processed"]}


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up C260 sensors."""
    coordinator: TapoC260Coordinator = entry.runtime_data
    async_add_entities(
        [
            TapoC260FaceNameSensor(coordinator),
            TapoC260FaceIdSensor(coordinator),
            TapoC260LastSeenSensor(coordinator),
            TapoC260KnownFacesSensor(coordinator),
            TapoC260UnknownFacesSensor(coordinator),
            TapoC260UnknownTodaySensor(coordinator),
            TapoC260LastUnknownSeenSensor(coordinator),
            TapoC260LastPollSensor(coordinator),
            TapoC260ResponseTimeSensor(coordinator),
            TapoC260PollErrorsSensor(coordinator),
            TapoC260ModeSensor(coordinator),
            TapoC260DedupSkippedSensor(coordinator),
        ]
    )
