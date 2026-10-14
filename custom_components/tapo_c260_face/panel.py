"""Sidebar panel registration for the Tapo C260 Face Manager."""
from __future__ import annotations

import asyncio
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const import (
    CONF_SHOW_SIDEBAR,
    CONF_SIDEBAR_TITLE,
    DEFAULT_SHOW_SIDEBAR,
    DEFAULT_SIDEBAR_TITLE,
    DOMAIN,
)

PANEL_PATH = f"/{DOMAIN}_manager"
PANEL_URL = DOMAIN
PANEL_NAME = "tapo-c260-face-manager"
PANEL_TITLE = DEFAULT_SIDEBAR_TITLE
PANEL_ICON = "mdi:face-recognition"


def _asset_version(path: Path) -> str:
    """Cache-bust token: đổi mỗi khi file JS đổi (mtime), khỏi phải sửa tay."""
    try:
        return str(int(path.stat().st_mtime))
    except OSError:
        return "0"


_ACTIVE_STATES = (
    ConfigEntryState.LOADED,
    ConfigEntryState.SETUP_IN_PROGRESS,
    ConfigEntryState.SETUP_RETRY,
)


def has_active_entries(hass: HomeAssistant, exclude_entry_id: str | None = None) -> bool:
    """Còn camera nào đang chạy (ngoài exclude_entry_id) cần panel không."""
    return any(
        entry.entry_id != exclude_entry_id and entry.state in _ACTIVE_STATES
        for entry in hass.config_entries.async_entries(DOMAIN)
    )


def _sidebar_wanted(hass: HomeAssistant, exclude_entry_id: str | None = None) -> bool:
    """Panel là dùng chung cho mọi camera: hiện ở sidebar nếu BẤT KỲ camera nào bật."""
    return any(
        entry.options.get(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR)
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id != exclude_entry_id and entry.state in _ACTIVE_STATES
    )


def _sidebar_title(hass: HomeAssistant, exclude_entry_id: str | None = None) -> str:
    """Tên ở sidebar: lấy của camera đầu tiên (theo tên) đang bật sidebar và có đặt tên."""
    entries = sorted(
        (
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.entry_id != exclude_entry_id and entry.state in _ACTIVE_STATES
        ),
        key=lambda entry: (entry.title, entry.entry_id),
    )
    for entry in entries:
        if not entry.options.get(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR):
            continue
        title = str(entry.options.get(CONF_SIDEBAR_TITLE) or "").strip()
        if title:
            return title
    return PANEL_TITLE


async def async_sync_panel(
    hass: HomeAssistant, exclude_entry_id: str | None = None
) -> None:
    """Đồng bộ panel, tuần tự hoá để nhiều camera setup cùng lúc không đăng ký trùng."""
    data = hass.data.setdefault(DOMAIN, {})
    lock = data.setdefault("panel_lock", asyncio.Lock())
    async with lock:
        await _async_sync_panel_locked(hass, exclude_entry_id)


async def _async_sync_panel_locked(
    hass: HomeAssistant, exclude_entry_id: str | None = None
) -> None:
    """Đăng ký panel và đồng bộ việc hiện/ẩn ở sidebar theo option.

    Idempotent: gọi nhiều lần không sao. Khi tắt, panel vẫn truy cập được bằng
    URL /tapo_c260_face nhưng không hiện trong sidebar.
    """
    data = hass.data.setdefault(DOMAIN, {})
    show = _sidebar_wanted(hass, exclude_entry_id)
    title = _sidebar_title(hass, exclude_entry_id)

    if (
        data.get("panel_registered")
        and data.get("panel_sidebar") == show
        and data.get("panel_title") == title
    ):
        return

    www_path = Path(__file__).parent / "frontend"
    if not data.get("static_registered"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_PATH, str(www_path), cache_headers=False)]
        )
        data["static_registered"] = True

    js_version = await hass.async_add_executor_job(
        _asset_version, www_path / "face-manager.js"
    )

    # panel_custom không hỗ trợ update tại chỗ: gỡ rồi đăng ký lại. Hai bước này
    # liền nhau, không await xen giữa, để frontend không bắt gặp lúc panel biến mất.
    if data.get("panel_registered"):
        frontend.async_remove_panel(hass, PANEL_URL)
        data["panel_registered"] = False

    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=PANEL_URL,
        module_url=f"{PANEL_PATH}/face-manager.js?v={js_version}",
        sidebar_title=title if show else None,
        sidebar_icon=PANEL_ICON if show else None,
        require_admin=True,
        embed_iframe=False,
        config={},
        # KHÔNG đặt config_panel_domain: nếu đặt, nút ⚙ ở trang integration sẽ
        # mở thẳng panel và options flow (Polling, Sidebar) không còn đường vào.
    )
    data["panel_registered"] = True
    data["panel_sidebar"] = show
    data["panel_title"] = title


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the Face Manager sidebar panel."""
    data = hass.data.get(DOMAIN, {})
    if data.get("panel_registered"):
        frontend.async_remove_panel(hass, PANEL_URL)
        data["panel_registered"] = False
        data["panel_sidebar"] = None
