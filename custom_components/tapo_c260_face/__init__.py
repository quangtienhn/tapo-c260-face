"""Tapo C260 Face Recognition integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .panel import async_sync_panel, async_unregister_panel, has_active_entries
from .websocket import async_setup as async_setup_websocket

from .api import TapoC260Api
from .const import (
    CONF_CLOUD_PASSWORD,
    CONF_HOST,
    CONF_USERNAME,
    DOMAIN,
)
from .coordinator import TapoC260Coordinator

type TapoC260ConfigEntry = ConfigEntry[TapoC260Coordinator]

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.EVENT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TapoC260ConfigEntry,
) -> bool:
    """Set up Tapo C260 from a config entry."""
    api = TapoC260Api(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data[CONF_USERNAME],
        entry.data[CONF_CLOUD_PASSWORD],
        hass=hass,
    )
    if not hass.data.get(DOMAIN, {}).get("websocket_registered"):
        async_setup_websocket(hass)
        hass.data.setdefault(DOMAIN, {})["websocket_registered"] = True

    await async_sync_panel(hass)

    coordinator = TapoC260Coordinator(hass, entry, api)

    # Make the coordinator available to the Face Manager even if the initial
    # refresh fails. The panel can then still show/manage saved Face IDs.
    entry.runtime_data = coordinator
    # Đăng ký listener TRƯỚC first refresh: nếu camera chưa sẵn sàng (setup retry)
    # thì tắt/bật và đổi tên sidebar vẫn có tác dụng. Listener tự gỡ khi setup lỗi.
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )
    return True


async def async_update_options(
    hass: HomeAssistant,
    entry: TapoC260ConfigEntry,
) -> None:
    """Apply changed options without reloading the integration."""
    # Hiện/ẩn sidebar trước, để toggle luôn có tác dụng dù bước sau có lỗi.
    await async_sync_panel(hass)
    # Đang reload/unload (vd. sau reauth) thì để lần setup mới đọc options.
    if entry.state is not ConfigEntryState.LOADED:
        return
    coordinator = entry.runtime_data
    await coordinator.async_apply_options()


async def async_unload_entry(
    hass: HomeAssistant,
    entry: TapoC260ConfigEntry,
) -> bool:
    """Unload the integration."""
    # Ghi nốt lịch sử/người lạ đang chờ trước khi gỡ.
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is not None:
        coordinator.async_cancel_timers()
        await coordinator.async_flush()
    unloaded = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
    if unloaded:
        if has_active_entries(hass, exclude_entry_id=entry.entry_id):
            # Entry còn lại có thể có cấu hình sidebar khác entry vừa gỡ.
            await async_sync_panel(hass, exclude_entry_id=entry.entry_id)
        else:
            async_unregister_panel(hass)
    return unloaded
