"""Base entity for Tapo C260 Face Recognition."""
from __future__ import annotations

from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TapoC260Coordinator


class TapoC260Entity(CoordinatorEntity[TapoC260Coordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TapoC260Coordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": coordinator.entry.title,
            "manufacturer": "TP-Link",
            "model": "Tapo C260",
            "configuration_url": f"http://{coordinator.entry.data['host']}",
        }


class TapoC260HealthEntity(TapoC260Entity):
    """Entity sức khoẻ: luôn available, kể cả khi poll lỗi (đó chính là thông tin cần xem)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self) -> bool:
        return True
