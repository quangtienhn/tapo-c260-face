"""WebSocket API for the Tapo C260 Face Manager."""
from __future__ import annotations

from datetime import date
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_FACE_ID,
    ATTR_NAME,
    ATTR_RECOGNIZED,
    CONF_DEDUP_SECONDS,
    CONF_FACES,
    CONF_HISTORY_SECONDS,
    CONF_MAX_UNKNOWN_FACES,
    CONF_POLL_INTERVAL,
    CONF_RETENTION_DAYS,
    CONF_SHOW_SIDEBAR,
    CONF_SIDEBAR_TITLE,
    CONF_STRANGER_CLEAR_SECONDS,
    DEFAULT_DEDUP_SECONDS,
    DEFAULT_FACE_NAME,
    DEFAULT_HISTORY_SECONDS,
    DEFAULT_MAX_UNKNOWN_FACES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_SHOW_SIDEBAR,
    DEFAULT_STRANGER_CLEAR_SECONDS,
    DOMAIN,
    MAX_MAX_UNKNOWN_FACES,
    MAX_SIDEBAR_TITLE_LEN,
    MAX_RETENTION_DAYS,
    MAX_STRANGER_CLEAR_SECONDS,
    MIN_MAX_UNKNOWN_FACES,
    MIN_RETENTION_DAYS,
    MIN_STRANGER_CLEAR_SECONDS,
)
from .coordinator import async_load_history, history_store
from .panel import async_sync_panel

WS_GET_DATA = f"{DOMAIN}/get_data"
WS_SAVE_FACE = f"{DOMAIN}/save_face"
WS_DELETE_FACE = f"{DOMAIN}/delete_face"
WS_FORGET_UNKNOWN = f"{DOMAIN}/forget_unknown"
WS_CLEAR_UNKNOWN = f"{DOMAIN}/clear_unknown"
WS_GET_STATS = f"{DOMAIN}/get_stats"
WS_GET_DAY = f"{DOMAIN}/get_day"
WS_SAVE_SETTINGS = f"{DOMAIN}/save_settings"


_LOGGER = logging.getLogger(__name__)

_SETTING_KEYS = (
    CONF_POLL_INTERVAL,
    CONF_HISTORY_SECONDS,
    CONF_DEDUP_SECONDS,
    CONF_STRANGER_CLEAR_SECONDS,
    CONF_RETENTION_DAYS,
    CONF_MAX_UNKNOWN_FACES,
    CONF_SHOW_SIDEBAR,
    CONF_SIDEBAR_TITLE,
)


def _entry(hass: HomeAssistant, entry_id: str) -> ConfigEntry:
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ValueError("Invalid Tapo C260 config entry")
    return entry


def _get_coordinator(entry: ConfigEntry):
    """Return coordinator when the config entry is currently set up."""
    return getattr(entry, "runtime_data", None)


def _faces_from_options(entry: ConfigEntry) -> dict[str, str]:
    faces = entry.options.get(CONF_FACES, {})
    if not isinstance(faces, dict):
        return {}
    return {str(k): str(v) for k, v in faces.items()}


def _serialize_entry(entry: ConfigEntry) -> dict[str, Any]:
    """Serialize even when the entry is configured but not fully loaded.

    This is important for the Face Manager: a temporary setup/auth error must
    not make the whole sidebar panel disappear.
    """
    coordinator = _get_coordinator(entry)
    faces = coordinator.faces if coordinator is not None else _faces_from_options(entry)

    if coordinator is not None:
        unknown_faces = coordinator.unknown_faces
        current = dict(coordinator.current)
        poll_interval = coordinator.poll_interval
        history_seconds = coordinator.history_seconds
        dedup_seconds = coordinator.dedup_seconds
        retention_days = coordinator.retention_days
        max_unknown_faces = coordinator.max_unknown_faces
        stranger_clear_seconds = coordinator.stranger_clear_seconds
        health = coordinator.health()
    else:
        health = None
        stranger_clear_seconds = int(
            entry.options.get(CONF_STRANGER_CLEAR_SECONDS, DEFAULT_STRANGER_CLEAR_SECONDS)
        )
        unknown_faces = {}
        current = {
            ATTR_FACE_ID: None,
            ATTR_NAME: DEFAULT_FACE_NAME,
            ATTR_RECOGNIZED: False,
        }
        poll_interval = int(entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        history_seconds = int(entry.options.get(CONF_HISTORY_SECONDS, DEFAULT_HISTORY_SECONDS))
        dedup_seconds = int(entry.options.get(CONF_DEDUP_SECONDS, DEFAULT_DEDUP_SECONDS))
        retention_days = int(entry.options.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS))
        max_unknown_faces = int(
            entry.options.get(CONF_MAX_UNKNOWN_FACES, DEFAULT_MAX_UNKNOWN_FACES)
        )

    # Cài đặt luôn lấy từ options (nguồn chính thức): coordinator áp dụng chúng
    # bất đồng bộ qua update listener nên có thể chậm hơn một nhịp.
    opts = entry.options
    poll_interval = int(opts.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
    history_seconds = int(opts.get(CONF_HISTORY_SECONDS, DEFAULT_HISTORY_SECONDS))
    dedup_seconds = int(opts.get(CONF_DEDUP_SECONDS, DEFAULT_DEDUP_SECONDS))
    retention_days = int(opts.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS))
    max_unknown_faces = int(opts.get(CONF_MAX_UNKNOWN_FACES, DEFAULT_MAX_UNKNOWN_FACES))
    stranger_clear_seconds = int(
        opts.get(CONF_STRANGER_CLEAR_SECONDS, DEFAULT_STRANGER_CLEAR_SECONDS)
    )

    return {
        "entry_id": entry.entry_id,
        "title": entry.title,
        "host": entry.data.get("host"),
        "faces": [
            {"face_id": str(face_id), "name": str(name)}
            for face_id, name in sorted(faces.items())
        ],
        "unknown_faces": [
            {
                "face_id": str(face_id),
                "first_seen": item.get("first_seen"),
                "last_seen": item.get("last_seen"),
                "count": int(item.get("count", 0)),
            }
            for face_id, item in sorted(
                unknown_faces.items(),
                key=lambda pair: pair[1].get("last_seen", ""),
                reverse=True,
            )
        ],
        "current": current,
        "poll_interval": poll_interval,
        "history_seconds": history_seconds,
        "dedup_seconds": dedup_seconds,
        "retention_days": retention_days,
        "max_unknown_faces": max_unknown_faces,
        "stranger_clear_seconds": stranger_clear_seconds,
        "show_sidebar": bool(entry.options.get(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR)),
        "sidebar_title": str(entry.options.get(CONF_SIDEBAR_TITLE) or ""),
        "health": health,
    }


async def _save_options(
    hass: HomeAssistant, entry: ConfigEntry, faces: dict[str, str]
) -> None:
    """Persist face mappings and update live state when available."""
    options = dict(entry.options)
    options[CONF_FACES] = faces
    hass.config_entries.async_update_entry(entry, options=options)

    coordinator = _get_coordinator(entry)
    if coordinator is not None:
        await coordinator.async_face_map_changed()


async def _merge_history(
    hass: HomeAssistant, entry: ConfigEntry, old_id: str, new_id: str
) -> None:
    coordinator = _get_coordinator(entry)
    if coordinator is not None:
        await coordinator.async_merge_face_history(old_id, new_id)
        return
    # Entry chưa load: sửa thẳng file lưu trữ.
    history = await async_load_history(hass, entry.entry_id)
    if history.merge(old_id, new_id):
        await history_store(hass, entry.entry_id).async_save(history.to_dict())


@websocket_api.websocket_command({vol.Required("type"): WS_GET_DATA})
@websocket_api.async_response
async def websocket_get_data(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return all configured C260 Face Manager data."""
    entries = hass.config_entries.async_entries(DOMAIN)
    connection.send_result(
        msg["id"],
        {"entries": [_serialize_entry(entry) for entry in entries]},
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SAVE_FACE,
        vol.Required("entry_id"): str,
        vol.Required("face_id"): str,
        vol.Required("name"): str,
        vol.Optional("old_face_id"): str,
    }
)
@websocket_api.async_response
async def websocket_save_face(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create or update a known Face ID."""
    try:
        entry = _entry(hass, msg["entry_id"])
        face_id = msg["face_id"].strip()
        name = msg["name"].strip()
        old_face_id = msg.get("old_face_id", "").strip() or face_id

        if not face_id.isdigit():
            raise ValueError("Face ID must contain digits only")
        if not name:
            raise ValueError("Name cannot be empty")

        coordinator = _get_coordinator(entry)
        faces = dict(coordinator.faces) if coordinator is not None else _faces_from_options(entry)

        if old_face_id != face_id:
            if old_face_id not in faces:
                raise ValueError("Original Face ID does not exist")
            if face_id in faces:
                raise ValueError("New Face ID already exists")
            faces.pop(old_face_id)
            # Đổi Face ID: chuyển lịch sử cũ sang ID mới để thống kê không mất.
            await _merge_history(hass, entry, old_face_id, face_id)

        faces[face_id] = name
        await _save_options(hass, entry, faces)
        connection.send_result(msg["id"], {"entry": _serialize_entry(entry)})
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_face", str(exc))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DELETE_FACE,
        vol.Required("entry_id"): str,
        vol.Required("face_id"): str,
    }
)
@websocket_api.async_response
async def websocket_delete_face(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a known Face ID."""
    try:
        entry = _entry(hass, msg["entry_id"])
        coordinator = _get_coordinator(entry)
        faces = dict(coordinator.faces) if coordinator is not None else _faces_from_options(entry)
        face_id = msg["face_id"].strip()
        if face_id not in faces:
            raise ValueError("Face ID does not exist")
        faces.pop(face_id)
        await _save_options(hass, entry, faces)
        connection.send_result(msg["id"], {"entry": _serialize_entry(entry)})
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_face", str(exc))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_FORGET_UNKNOWN,
        vol.Required("entry_id"): str,
        vol.Required("face_id"): str,
    }
)
@websocket_api.async_response
async def websocket_forget_unknown(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove an unknown Face ID from the local discovery list."""
    try:
        entry = _entry(hass, msg["entry_id"])
        coordinator = _get_coordinator(entry)
        if coordinator is None:
            raise ValueError("Tapo C260 is not currently loaded")
        face_id = msg["face_id"].strip()
        if not await coordinator.async_forget_unknown(face_id):
            raise ValueError("Unknown Face ID does not exist")
        connection.send_result(msg["id"], {"entry": _serialize_entry(entry)})
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_face", str(exc))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_CLEAR_UNKNOWN,
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def websocket_clear_unknown(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove every unknown Face ID (list + statistics)."""
    try:
        entry = _entry(hass, msg["entry_id"])
        coordinator = _get_coordinator(entry)
        if coordinator is None:
            raise ValueError("Tapo C260 is not currently loaded")
        removed = await coordinator.async_clear_unknown()
        connection.send_result(
            msg["id"], {"removed": removed, "entry": _serialize_entry(entry)}
        )
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_face", str(exc))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_GET_STATS,
        vol.Required("entry_id"): str,
        vol.Optional("range_days", default=30): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=365)
        ),
    }
)
@websocket_api.async_response
async def websocket_get_stats(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return per-day / all-time statistics (works even if entry isn't loaded)."""
    try:
        entry = _entry(hass, msg["entry_id"])
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_face", str(exc))
        return
    coordinator = _get_coordinator(entry)
    if coordinator is not None:
        stats = coordinator.get_stats(msg["range_days"])
    else:
        history = await async_load_history(hass, entry.entry_id)
        stats = history.stats(
            _faces_from_options(entry), dt_util.now().date(), msg["range_days"]
        )
    connection.send_result(msg["id"], {"entry_id": entry.entry_id, "stats": stats})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_GET_DAY,
        vol.Required("entry_id"): str,
        vol.Optional("date"): str,
    }
)
@websocket_api.async_response
async def websocket_get_day(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Ai xuất hiện lúc nào trong một ngày (mặc định hôm nay)."""
    try:
        entry = _entry(hass, msg["entry_id"])
        day = date.fromisoformat(msg["date"]) if msg.get("date") else dt_util.now().date()
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_date", str(exc))
        return
    coordinator = _get_coordinator(entry)
    if coordinator is not None:
        view = coordinator.get_day(day)
    else:
        history = await async_load_history(hass, entry.entry_id)
        view = history.day_view(
            _faces_from_options(entry), day, dt_util.get_default_time_zone()
        )
    connection.send_result(msg["id"], {"entry_id": entry.entry_id, "day": view})


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SAVE_SETTINGS,
        vol.Required("entry_id"): str,
        vol.Required(CONF_POLL_INTERVAL): vol.All(int, vol.Range(min=2, max=300)),
        vol.Required(CONF_HISTORY_SECONDS): vol.All(int, vol.Range(min=30, max=3600)),
        vol.Required(CONF_DEDUP_SECONDS): vol.All(int, vol.Range(min=0, max=3600)),
        vol.Required(CONF_STRANGER_CLEAR_SECONDS): vol.All(
            int, vol.Range(min=MIN_STRANGER_CLEAR_SECONDS, max=MAX_STRANGER_CLEAR_SECONDS)
        ),
        vol.Required(CONF_RETENTION_DAYS): vol.All(
            int, vol.Range(min=MIN_RETENTION_DAYS, max=MAX_RETENTION_DAYS)
        ),
        vol.Required(CONF_MAX_UNKNOWN_FACES): vol.All(
            int, vol.Range(min=MIN_MAX_UNKNOWN_FACES, max=MAX_MAX_UNKNOWN_FACES)
        ),
        vol.Required(CONF_SHOW_SIDEBAR): bool,
        vol.Optional(CONF_SIDEBAR_TITLE, default=""): vol.All(
            str, vol.Length(max=MAX_SIDEBAR_TITLE_LEN)
        ),
    }
)
@websocket_api.async_response
async def websocket_save_settings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Lưu Polling / Dedup / Storage limits / Sidebar (cùng options với menu ⚙)."""
    try:
        entry = _entry(hass, msg["entry_id"])
    except ValueError as exc:
        connection.send_error(msg["id"], "invalid_entry", str(exc))
        return
    options = dict(entry.options)
    for key in _SETTING_KEYS:
        options[key] = msg[key].strip() if key == CONF_SIDEBAR_TITLE else msg[key]
    # Listener của entry (async_update_options) sẽ áp dụng ngay vào coordinator.
    hass.config_entries.async_update_entry(entry, options=options)
    # Đồng bộ sidebar NGAY tại đây (không phụ thuộc update listener, vốn chỉ chạy
    # khi entry đã load xong). Idempotent nên chạy thêm lần nữa ở listener cũng không sao.
    try:
        await async_sync_panel(hass)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.exception("Cannot update Face Manager sidebar")
        connection.send_error(msg["id"], "panel_sync_failed", str(exc))
        return
    data = hass.data.get(DOMAIN, {})
    connection.send_result(
        msg["id"],
        {
            "entry": _serialize_entry(entry),
            "panel": {
                "in_sidebar": bool(data.get("panel_sidebar")),
                "title": data.get("panel_title"),
            },
        },
    )


@callback
def async_setup(hass: HomeAssistant) -> None:
    """Register Face Manager WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_data)
    websocket_api.async_register_command(hass, websocket_save_face)
    websocket_api.async_register_command(hass, websocket_delete_face)
    websocket_api.async_register_command(hass, websocket_forget_unknown)
    websocket_api.async_register_command(hass, websocket_clear_unknown)
    websocket_api.async_register_command(hass, websocket_get_stats)
    websocket_api.async_register_command(hass, websocket_get_day)
    websocket_api.async_register_command(hass, websocket_save_settings)
