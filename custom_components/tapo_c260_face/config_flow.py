"""Config flow for Tapo C260 Face Recognition."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    TapoC260Api,
    TapoC260AuthError,
    TapoC260ConnectionError,
    TapoC260ProtocolError,
)
from .const import (
    CONF_CLOUD_PASSWORD,
    CONF_DEDUP_SECONDS,
    CONF_FACES,
    CONF_HISTORY_SECONDS,
    CONF_HOST,
    CONF_MAX_UNKNOWN_FACES,
    CONF_POLL_INTERVAL,
    CONF_RETENTION_DAYS,
    CONF_SHOW_SIDEBAR,
    CONF_SIDEBAR_TITLE,
    CONF_STRANGER_CLEAR_SECONDS,
    CONF_USERNAME,
    DEFAULT_DEDUP_SECONDS,
    DEFAULT_HISTORY_SECONDS,
    DEFAULT_MAX_UNKNOWN_FACES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_SHOW_SIDEBAR,
    DEFAULT_SIDEBAR_TITLE,
    DEFAULT_STRANGER_CLEAR_SECONDS,
    DOMAIN,
    MAX_SIDEBAR_TITLE_LEN,
    MAX_MAX_UNKNOWN_FACES,
    MAX_RETENTION_DAYS,
    MAX_STRANGER_CLEAR_SECONDS,
    MIN_MAX_UNKNOWN_FACES,
    MIN_RETENTION_DAYS,
    MIN_STRANGER_CLEAR_SECONDS,
)


class TapoC260ConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a Tapo C260 config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Set up a camera."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_CLOUD_PASSWORD]

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            api = TapoC260Api(
                session,
                host,
                username,
                password,
            )

            try:
                await api.async_login()
            except TapoC260AuthError:
                errors["base"] = "authentication_failed"
            except (TapoC260ConnectionError, TapoC260ProtocolError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Tapo C260 ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                        CONF_CLOUD_PASSWORD: password,
                    },
                    options={
                        CONF_POLL_INTERVAL: DEFAULT_POLL_INTERVAL,
                        CONF_HISTORY_SECONDS: DEFAULT_HISTORY_SECONDS,
                        CONF_DEDUP_SECONDS: DEFAULT_DEDUP_SECONDS,
                        CONF_STRANGER_CLEAR_SECONDS: DEFAULT_STRANGER_CLEAR_SECONDS,
                        CONF_RETENTION_DAYS: DEFAULT_RETENTION_DAYS,
                        CONF_MAX_UNKNOWN_FACES: DEFAULT_MAX_UNKNOWN_FACES,
                        CONF_FACES: {},
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_CLOUD_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Camera từ chối đăng nhập: xin lại username / Cloud Password."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_CLOUD_PASSWORD]
            api = TapoC260Api(
                async_get_clientsession(self.hass),
                entry.data[CONF_HOST],
                username,
                password,
            )
            try:
                await api.async_login()
            except TapoC260AuthError:
                errors["base"] = "authentication_failed"
            except (TapoC260ConnectionError, TapoC260ProtocolError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_USERNAME: username,
                        CONF_CLOUD_PASSWORD: password,
                    },
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(
                            CONF_USERNAME, entry.data.get(CONF_USERNAME, "")
                        ),
                    ): str,
                    vol.Required(CONF_CLOUD_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
            description_placeholders={"host": entry.data[CONF_HOST]},
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Return the options flow."""
        return TapoC260OptionsFlow()


class TapoC260OptionsFlow(OptionsFlow):
    """Manage known faces, discovered unknown IDs and polling options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Show management menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "faces",
                "unknown_faces",
                "add_face",
                "add_unknown",
                "edit_face",
                "delete_face",
                "polling",
                "retention",
                "sidebar",
            ],
        )

    def _faces(self) -> dict[str, str]:
        faces = self.config_entry.options.get(CONF_FACES, {})
        return {str(k): str(v) for k, v in faces.items()} if isinstance(faces, dict) else {}

    def _unknown_faces(self) -> dict[str, dict[str, Any]]:
        coordinator = getattr(self.config_entry, "runtime_data", None)
        if coordinator is None:
            return {}
        return dict(getattr(coordinator, "unknown_faces", {}))

    async def async_step_faces(self, user_input=None) -> ConfigFlowResult:
        """Show configured faces."""
        faces = self._faces()
        lines = [f"{face_id} → {name}" for face_id, name in sorted(faces.items())]
        return self.async_show_form(
            step_id="faces",
            data_schema=vol.Schema({}),
            description_placeholders={
                "faces": "\n".join(lines) if lines else "Chưa có Face ID nào.",
            },
        )

    async def async_step_unknown_faces(self, user_input=None) -> ConfigFlowResult:
        """Show Face IDs discovered but not yet named."""
        unknown = self._unknown_faces()
        lines = []
        for face_id, item in sorted(
            unknown.items(),
            key=lambda x: x[1].get("last_seen", ""),
            reverse=True,
        ):
            lines.append(
                f"{face_id} — lần cuối: {item.get('last_seen', '?')} — "
                f"{item.get('count', 0)} lần"
            )
        return self.async_show_form(
            step_id="unknown_faces",
            data_schema=vol.Schema({}),
            description_placeholders={
                "unknown_faces": "\n".join(lines) if lines else "Chưa phát hiện Face ID lạ.",
            },
        )

    async def async_step_add_face(self, user_input=None) -> ConfigFlowResult:
        """Add a Face ID/name mapping."""
        errors = {}
        faces = self._faces()
        if user_input is not None:
            face_id = str(user_input["face_id"]).strip()
            name = str(user_input["name"]).strip()
            if not face_id.isdigit():
                errors["face_id"] = "invalid_face_id"
            elif not name:
                errors["name"] = "invalid_name"
            elif face_id in faces:
                errors["face_id"] = "face_id_exists"
            else:
                faces[face_id] = name
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, CONF_FACES: faces},
                )
        return self.async_show_form(
            step_id="add_face",
            data_schema=vol.Schema({
                vol.Required("face_id"): str,
                vol.Required("name"): str,
            }),
            errors=errors,
        )

    async def async_step_add_unknown(self, user_input=None) -> ConfigFlowResult:
        """Add a discovered unknown Face ID directly to known faces."""
        unknown = self._unknown_faces()
        faces = self._faces()
        if not unknown:
            return self.async_abort(reason="no_unknown_faces")

        errors = {}
        if user_input is not None:
            face_id = str(user_input["face_id"])
            name = str(user_input["name"]).strip()
            if face_id in faces:
                errors["face_id"] = "face_id_exists"
            elif not name:
                errors["name"] = "invalid_name"
            else:
                faces[face_id] = name
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, CONF_FACES: faces},
                )

        options = [
            {"value": face_id, "label": face_id}
            for face_id in sorted(unknown)
        ]
        first_id = next(iter(sorted(unknown)))
        return self.async_show_form(
            step_id="add_unknown",
            data_schema=vol.Schema({
                vol.Required("face_id", default=first_id): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=options, mode=selector.SelectSelectorMode.DROPDOWN)
                ),
                vol.Required("name"): str,
            }),
            errors=errors,
        )

    async def async_step_edit_face(self, user_input=None) -> ConfigFlowResult:
        """Edit an existing mapping."""
        faces = self._faces()
        if not faces:
            return self.async_abort(reason="no_faces")
        errors = {}
        first_id = next(iter(faces))
        if user_input is not None:
            old_id = str(user_input["old_face_id"])
            new_id = str(user_input["new_face_id"]).strip()
            name = str(user_input["name"]).strip()
            if not new_id.isdigit():
                errors["new_face_id"] = "invalid_face_id"
            elif not name:
                errors["name"] = "invalid_name"
            elif new_id != old_id and new_id in faces:
                errors["new_face_id"] = "face_id_exists"
            else:
                if new_id != old_id:
                    # Đổi Face ID: chuyển lịch sử cũ sang ID mới.
                    coordinator = getattr(self.config_entry, "runtime_data", None)
                    if coordinator is not None:
                        await coordinator.async_merge_face_history(old_id, new_id)
                faces.pop(old_id, None)
                faces[new_id] = name
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, CONF_FACES: faces},
                )
        return self.async_show_form(
            step_id="edit_face",
            data_schema=vol.Schema({
                vol.Required("old_face_id", default=first_id): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=list(faces), mode=selector.SelectSelectorMode.DROPDOWN)
                ),
                vol.Required("new_face_id", default=first_id): str,
                vol.Required("name", default=faces[first_id]): str,
            }),
            errors=errors,
        )

    async def async_step_delete_face(self, user_input=None) -> ConfigFlowResult:
        """Delete a mapping."""
        faces = self._faces()
        if not faces:
            return self.async_abort(reason="no_faces")
        if user_input is not None:
            face_id = str(user_input["face_id"])
            faces.pop(face_id, None)
            return self.async_create_entry(
                title="",
                data={**self.config_entry.options, CONF_FACES: faces},
            )
        return self.async_show_form(
            step_id="delete_face",
            data_schema=vol.Schema({
                vol.Required("face_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=list(faces), mode=selector.SelectSelectorMode.DROPDOWN)
                )
            }),
        )

    async def async_step_sidebar(self, user_input=None) -> ConfigFlowResult:
        """Bật/tắt hiển thị Face Manager ở sidebar."""
        current = self.config_entry.options
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    **current,
                    CONF_SHOW_SIDEBAR: bool(user_input[CONF_SHOW_SIDEBAR]),
                    CONF_SIDEBAR_TITLE: str(user_input.get(CONF_SIDEBAR_TITLE, "")).strip(),
                },
            )
        return self.async_show_form(
            step_id="sidebar",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SHOW_SIDEBAR,
                    default=current.get(CONF_SHOW_SIDEBAR, DEFAULT_SHOW_SIDEBAR),
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_SIDEBAR_TITLE,
                    description={"suggested_value": current.get(CONF_SIDEBAR_TITLE, "")},
                ): vol.All(str, vol.Length(max=MAX_SIDEBAR_TITLE_LEN)),
            }),
        )

    async def async_step_retention(self, user_input=None) -> ConfigFlowResult:
        """Giới hạn số ngày lưu thống kê và số người lạ."""
        current = self.config_entry.options
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    **current,
                    CONF_RETENTION_DAYS: int(user_input[CONF_RETENTION_DAYS]),
                    CONF_MAX_UNKNOWN_FACES: int(user_input[CONF_MAX_UNKNOWN_FACES]),
                },
            )
        return self.async_show_form(
            step_id="retention",
            data_schema=vol.Schema({
                vol.Required(CONF_RETENTION_DAYS, default=current.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS)): vol.All(vol.Coerce(int), vol.Range(min=MIN_RETENTION_DAYS, max=MAX_RETENTION_DAYS)),
                vol.Required(CONF_MAX_UNKNOWN_FACES, default=current.get(CONF_MAX_UNKNOWN_FACES, DEFAULT_MAX_UNKNOWN_FACES)): vol.All(vol.Coerce(int), vol.Range(min=MIN_MAX_UNKNOWN_FACES, max=MAX_MAX_UNKNOWN_FACES)),
            }),
        )

    async def async_step_polling(self, user_input=None) -> ConfigFlowResult:
        """Configure polling."""
        current = self.config_entry.options
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    **current,
                    CONF_POLL_INTERVAL: int(user_input[CONF_POLL_INTERVAL]),
                    CONF_HISTORY_SECONDS: int(user_input[CONF_HISTORY_SECONDS]),
                    CONF_DEDUP_SECONDS: int(user_input[CONF_DEDUP_SECONDS]),
                    CONF_STRANGER_CLEAR_SECONDS: int(user_input[CONF_STRANGER_CLEAR_SECONDS]),
                },
            )
        return self.async_show_form(
            step_id="polling",
            data_schema=vol.Schema({
                vol.Required(CONF_POLL_INTERVAL, default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=2, max=300)),
                vol.Required(CONF_HISTORY_SECONDS, default=current.get(CONF_HISTORY_SECONDS, DEFAULT_HISTORY_SECONDS)): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                vol.Required(CONF_DEDUP_SECONDS, default=current.get(CONF_DEDUP_SECONDS, DEFAULT_DEDUP_SECONDS)): vol.All(vol.Coerce(int), vol.Range(min=0, max=3600)),
                vol.Required(CONF_STRANGER_CLEAR_SECONDS, default=current.get(CONF_STRANGER_CLEAR_SECONDS, DEFAULT_STRANGER_CLEAR_SECONDS)): vol.All(vol.Coerce(int), vol.Range(min=MIN_STRANGER_CLEAR_SECONDS, max=MAX_STRANGER_CLEAR_SECONDS)),
            }),
        )

