"""Coordinator for Tapo C260 face recognition."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta, timezone
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    TapoC260Api,
    TapoC260AuthError,
    TapoC260ConnectionError,
    TapoC260ProtocolError,
)
from .const import (
    ATTR_ALARM_TYPE,
    ATTR_CAMERA,
    ATTR_END_TIME,
    ATTR_EVENT_TIME,
    ATTR_EVENT_FACE_IDS,
    ATTR_EVENTS_1,
    ATTR_FACE_ID,
    ATTR_NAME,
    ATTR_RECOGNIZED,
    ATTR_START_TIME,
    CONF_DEDUP_SECONDS,
    CONF_FACES,
    CONF_HISTORY_SECONDS,
    CONF_MAX_UNKNOWN_FACES,
    CONF_POLL_INTERVAL,
    CONF_RETENTION_DAYS,
    CONF_STRANGER_CLEAR_SECONDS,
    DEFAULT_DEDUP_SECONDS,
    DEFAULT_FACE_NAME,
    DEFAULT_HISTORY_SECONDS,
    DEFAULT_MAX_UNKNOWN_FACES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_STRANGER_CLEAR_SECONDS,
    DOMAIN,
    EVENT_FACE_DETECTED,
    MAX_MAX_UNKNOWN_FACES,
    MAX_RETENTION_DAYS,
    MAX_STRANGER_CLEAR_SECONDS,
    MIN_MAX_UNKNOWN_FACES,
    MIN_RETENTION_DAYS,
    MIN_STRANGER_CLEAR_SECONDS,
)
from .history import FaceHistory

_LOGGER = logging.getLogger(__name__)

# Ghi lịch sử xuống đĩa trễ tối đa ngần này giây (gộp nhiều event, đỡ mòn flash).
HISTORY_SAVE_DELAY = 30


def _clamp(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def history_store(hass: HomeAssistant, entry_id: str) -> Store:
    return Store(hass, 1, f"{DOMAIN}.history.{entry_id}")


async def async_load_history(hass: HomeAssistant, entry_id: str) -> FaceHistory:
    """Đọc lịch sử đã lưu (dùng cả khi entry chưa được load)."""
    return FaceHistory.from_dict(await history_store(hass, entry_id).async_load())

# Số lần poll liên tiếp được phép chờ Tapo-Control trước khi báo lỗi (entity unavailable).
WAIT_GRACE_POLLS = 6


class TapoC260Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate C260 polling and publish HA events."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: TapoC260Api,
    ) -> None:
        self.entry = entry
        self.api = api
        # Mỗi event camera (face_id + start_time) chỉ được xử lý MỘT lần, dù
        # camera trả lại nó ở nhiều lần poll liên tiếp (cửa sổ history trượt).
        self._seen_events: dict[str, float] = {}
        # Known faces: thêm cooldown theo Face ID cho các event MỚI.
        # Unknown faces: không cooldown, mỗi event mới được báo ngay.
        self._last_face_event: dict[str, float] = {}
        # Lần poll đầu sau khi khởi động/reload: history có sẵn chỉ để làm mốc,
        # không báo lại và không tăng count.
        self._baseline_done = False
        self._wait_polls = 0
        self._logged_modes: set[str] = set()
        self._unknown_faces: dict[str, dict[str, Any]] = {}
        self._unknown_store = Store(
            hass, 1, f"{DOMAIN}.unknown_faces.{entry.entry_id}"
        )
        self.history = FaceHistory()
        self._history_store = history_store(hass, entry.entry_id)
        # Các Face ID đang là người quen ở lần xử lý thay đổi gần nhất; dùng để
        # biết ID nào vừa bị xoá khỏi người quen.
        self._known_snapshot: set[str] = set(self.faces)
        self._last_prune_day: date | None = None
        # Sức khoẻ (chỉ trong RAM, reset khi restart/reload).
        self._mode = "starting"
        self._last_success: datetime | None = None
        self._last_attempt: datetime | None = None
        self._last_response_ms: int | None = None
        self._consecutive_failures = 0
        self._total_failures = 0
        self._last_error: str | None = None
        self._last_error_time: datetime | None = None
        self._dedup_skipped = 0
        self._events_processed = 0
        # Binary sensor "Stranger Detected" + event entity.
        self.stranger_active = False
        self._stranger_unsub: Callable[[], None] | None = None
        self._face_listeners: list[Callable[[dict[str, Any]], None]] = []

        options = entry.options
        self.stranger_clear_seconds = _clamp(
            options.get(CONF_STRANGER_CLEAR_SECONDS),
            DEFAULT_STRANGER_CLEAR_SECONDS,
            MIN_STRANGER_CLEAR_SECONDS,
            MAX_STRANGER_CLEAR_SECONDS,
        )
        self.retention_days = _clamp(
            options.get(CONF_RETENTION_DAYS),
            DEFAULT_RETENTION_DAYS,
            MIN_RETENTION_DAYS,
            MAX_RETENTION_DAYS,
        )
        self.max_unknown_faces = _clamp(
            options.get(CONF_MAX_UNKNOWN_FACES),
            DEFAULT_MAX_UNKNOWN_FACES,
            MIN_MAX_UNKNOWN_FACES,
            MAX_MAX_UNKNOWN_FACES,
        )
        self.poll_interval = int(
            options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
        )
        self.history_seconds = int(
            options.get(CONF_HISTORY_SECONDS, DEFAULT_HISTORY_SECONDS)
        )
        self.dedup_seconds = int(
            options.get(CONF_DEDUP_SECONDS, DEFAULT_DEDUP_SECONDS)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=self.poll_interval),
            always_update=True,
        )

    @property
    def unknown_faces(self) -> dict[str, dict[str, Any]]:
        """Return discovered Face IDs not currently mapped."""
        return dict(self._unknown_faces)

    @property
    def known_face_count(self) -> int:
        """Return number of configured known faces."""
        return len(self.faces)

    @property
    def unknown_face_count(self) -> int:
        """Return number of discovered unknown faces."""
        return len(self._unknown_faces)

    @property
    def faces(self) -> dict[str, str]:
        """Return configured Face ID/name mappings."""
        faces = self.entry.options.get(CONF_FACES, {})
        if not isinstance(faces, Mapping):
            return {}
        return {str(k): str(v) for k, v in faces.items()}

    @property
    def current(self) -> dict[str, Any]:
        """Return current face state."""
        return self.data or {
            ATTR_FACE_ID: None,
            ATTR_NAME: DEFAULT_FACE_NAME,
            ATTR_RECOGNIZED: False,
        }

    @callback
    def lookup_face(self, face_id: str) -> tuple[str, bool]:
        """Map Face ID to configured name."""
        name = self.faces.get(str(face_id))
        if name:
            return name, True
        return DEFAULT_FACE_NAME, False

    def _find_tapo_control_controller(self) -> tuple[str, Any | None]:
        """Return (mode, controller): shared, wait, or standalone.

        Chờ (không login riêng) CHỈ khi entry Tapo-Control khớp đang setup/retry.
        Nếu nó bị tắt/lỗi, hoặc đã load mà không thấy controller (cấu trúc nội bộ
        đổi), dùng session riêng thay vì đứng im vô thời hạn.
        """
        host = str(self.entry.data.get("host", "")).strip().lower()
        tapo_entries = self.hass.config_entries.async_entries("tapo_control")
        matching_entry = None
        for tapo_entry in tapo_entries:
            values = [tapo_entry.title]
            for source in (tapo_entry.data, tapo_entry.options):
                for key in ("ip_address", "host", "ip", "address", "device_ip"):
                    value = source.get(key) if isinstance(source, Mapping) else None
                    if value:
                        values.append(str(value))
            if any(str(value).strip().lower() == host for value in values if value):
                matching_entry = tapo_entry
                break

        if matching_entry is None:
            return "standalone", None

        entry_data = self.hass.data.get("tapo_control", {}).get(matching_entry.entry_id)
        controller = entry_data.get("controller") if isinstance(entry_data, Mapping) else None
        if controller is not None and callable(getattr(controller, "executeFunction", None)):
            return "shared", controller

        if matching_entry.state in (
            ConfigEntryState.SETUP_IN_PROGRESS,
            ConfigEntryState.SETUP_RETRY,
        ):
            return "wait", None

        reason = f"standalone:{matching_entry.state.value}"
        if reason not in self._logged_modes:
            self._logged_modes.add(reason)
            _LOGGER.warning(
                "Tapo-Control entry for %s is %s and has no usable controller; "
                "using a separate camera session",
                self.entry.title,
                matching_entry.state.value,
            )
        return "standalone", None

    async def _async_setup(self) -> None:
        """Load persistent unknown faces and validate the selected API mode."""
        stored = await self._unknown_store.async_load()
        if isinstance(stored, Mapping):
            self._unknown_faces = {
                str(face_id): dict(value)
                for face_id, value in stored.items()
                if isinstance(value, Mapping)
            }

        # Remove IDs that are already configured as known.
        known_ids = set(self.faces)
        self._unknown_faces = {
            face_id: value
            for face_id, value in self._unknown_faces.items()
            if face_id not in known_ids
        }

        self.history = FaceHistory.from_dict(await self._history_store.async_load())
        self._known_snapshot = set(self.faces)
        self._prune_all()

        await self._unknown_store.async_save(self._unknown_faces)
        self._schedule_history_save()

        mode, controller = self._find_tapo_control_controller()
        self.api.shared_controller = controller if mode == "shared" else None
        if mode == "wait":
            _LOGGER.debug("Waiting for Tapo-Control controller for %s", self.entry.title)
            return
        if mode == "shared":
            _LOGGER.info("Using existing Tapo-Control controller for %s", self.entry.title)
            return

        try:
            await self.api.async_login()
        except TapoC260AuthError as exc:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from exc
        except (TapoC260ConnectionError, TapoC260ProtocolError) as exc:
            raise UpdateFailed(str(exc)) from exc

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll camera, đồng thời ghi lại sức khoẻ kết nối."""
        self._last_attempt = dt_util.utcnow()
        try:
            data = await self._async_poll()
        except Exception as exc:  # noqa: BLE001 - ghi nhận rồi ném lại nguyên vẹn
            self._record_poll_failure(exc)
            raise
        return data

    def _record_poll_failure(self, exc: Exception) -> None:
        self._consecutive_failures += 1
        self._total_failures += 1
        self._last_error = f"{type(exc).__name__}: {exc}"[:300]
        self._last_error_time = dt_util.utcnow()
        # Khi lỗi lặp lại, HA không tự báo listeners: tự báo để sensor sức khoẻ cập nhật.
        self.async_update_listeners()

    @callback
    def health(self) -> dict[str, Any]:
        """Sức khoẻ integration: để biết camera mất kết nối chứ không phải "không có ai"."""
        stale_after = max(self.poll_interval * 3, 60)
        now = dt_util.utcnow()
        if self._consecutive_failures:
            status = "error"
        elif self._mode == "wait":
            status = "waiting"
        elif self._last_success is None:
            status = "starting"
        elif (now - self._last_success).total_seconds() > stale_after:
            status = "stale"
        else:
            status = "ok"
        return {
            "status": status,
            "connected": status in ("ok", "waiting"),
            "mode": self._mode,
            "last_success": self._last_success.isoformat() if self._last_success else None,
            "last_attempt": self._last_attempt.isoformat() if self._last_attempt else None,
            "response_ms": self._last_response_ms,
            "consecutive_failures": self._consecutive_failures,
            "total_failures": self._total_failures,
            "last_error": self._last_error,
            "last_error_time": self._last_error_time.isoformat() if self._last_error_time else None,
            "dedup_skipped": self._dedup_skipped,
            "events_processed": self._events_processed,
        }

    async def _async_poll(self) -> dict[str, Any]:
        """Fetch and process recent detection events."""
        mode, controller = self._find_tapo_control_controller()
        self.api.shared_controller = controller if mode == "shared" else None
        self._mode = mode

        if mode == "wait":
            # Crucially, don't fall back to our own login while a matching
            # Tapo-Control entry exists but its controller isn't ready. Return
            # a harmless initial state so HA can finish setup and retry on the
            # next scheduled poll instead of entering setup-retry loops.
            self._wait_polls += 1
            if self._wait_polls > WAIT_GRACE_POLLS:
                raise UpdateFailed("Tapo-Control controller is not ready")
            return self.data or {
                ATTR_FACE_ID: None,
                ATTR_NAME: DEFAULT_FACE_NAME,
                ATTR_RECOGNIZED: False,
            }
        self._wait_polls = 0

        fetch_started = time.monotonic()
        if mode == "shared":
            try:
                events = await self.api.async_search_detection_list(self.history_seconds)
            except (TapoC260AuthError, TapoC260ConnectionError, TapoC260ProtocolError) as exc:
                # Shared-controller failures are transient from this
                # integration's perspective; never initiate a second login.
                raise UpdateFailed(f"Shared Tapo-Control request failed: {exc}") from exc
        else:
            try:
                if self.api._secure is None:
                    await self.api.async_login()
                events = await self.api.async_search_detection_list(self.history_seconds)
            except TapoC260AuthError:
                try:
                    await self.api.async_login()
                    events = await self.api.async_search_detection_list(self.history_seconds)
                except TapoC260AuthError as exc:
                    raise ConfigEntryAuthFailed(
                        translation_domain=DOMAIN,
                        translation_key="authentication_failed",
                    ) from exc
                except (TapoC260ConnectionError, TapoC260ProtocolError) as exc:
                    raise UpdateFailed(str(exc)) from exc
            except (TapoC260ConnectionError, TapoC260ProtocolError) as exc:
                raise UpdateFailed(str(exc)) from exc

        # Poll thật sự thành công (đã lấy được danh sách event từ camera).
        self._last_response_ms = round((time.monotonic() - fetch_started) * 1000)
        self._last_success = dt_util.utcnow()
        self._consecutive_failures = 0

        latest: dict[str, Any] | None = None
        latest_key: tuple[float, float, int] | None = None
        now = time.monotonic()
        baseline = not self._baseline_done

        for event_index, event in enumerate(events):
            event_info = event.get("event_info")
            if not isinstance(event_info, list):
                continue

            # Một event có thể chứa NHIỀU khuôn mặt (vd. người quen + người lạ).
            # Xử lý từng Face ID riêng, không để ID này ghi đè ID kia. Cùng một
            # Face ID lặp lại trong event thì chỉ tính một lần.
            candidates: list[tuple[str, str, bool, int]] = []
            seen_ids: set[str] = set()
            for info_index, info in enumerate(event_info):
                if not isinstance(info, Mapping):
                    continue
                face_value = info.get("face_id")
                if face_value is None:
                    continue
                candidate_id = str(face_value)
                if candidate_id in seen_ids:
                    continue
                seen_ids.add(candidate_id)
                candidate_name, candidate_recognized = self.lookup_face(candidate_id)
                candidates.append(
                    (candidate_id, candidate_name, candidate_recognized, info_index)
                )
            if not candidates:
                continue

            event_time = self._event_timestamp_iso(
                event.get("start_time"), event.get("end_time")
            )
            event_face_ids = [c[0] for c in candidates]

            def build_payload(candidate: tuple[str, str, bool, int]) -> dict[str, Any]:
                return {
                    ATTR_FACE_ID: candidate[0],
                    ATTR_NAME: candidate[1],
                    ATTR_RECOGNIZED: candidate[2],
                    # Giờ của camera, không phải giờ HA poll.
                    ATTR_EVENT_TIME: event_time,
                    ATTR_START_TIME: event.get("start_time"),
                    ATTR_END_TIME: event.get("end_time"),
                    ATTR_ALARM_TYPE: event.get("alarm_type"),
                    ATTR_EVENTS_1: event.get("events_1"),
                    ATTR_CAMERA: self.entry.title,
                    ATTR_EVENT_FACE_IDS: event_face_ids,
                }

            # Trạng thái "hiện tại" (sensor): trong event ưu tiên Face ID đã nhận
            # diện. Giữa các event, event mới nhất theo thời gian thắng.
            best = max(candidates, key=lambda item: (item[2], item[3]))
            order_key = (
                self._event_timestamp_seconds(event.get("start_time")),
                self._event_timestamp_seconds(event.get("end_time")),
                event_index,
            )
            if latest_key is None or order_key > latest_key:
                latest = build_payload(best)
                latest_key = order_key

            # Mỗi (event, Face ID) chỉ xử lý một lần (cả known lẫn unknown).
            event_marker = event.get("start_time")
            if event_marker is None:
                event_marker = event.get("end_time")
            if event_marker is None:
                event_marker = (
                    event.get("alarm_type"),
                    event.get("events_1"),
                    repr(event_info),
                )

            for candidate in sorted(candidates, key=lambda item: item[3]):
                face_id, _name, recognized, _idx = candidate
                seen_key = f"{face_id}|{event_marker}"
                if seen_key in self._seen_events:
                    continue
                self._seen_events[seen_key] = now

                if baseline:
                    # History có sẵn lúc khởi động: chỉ làm mốc.
                    continue

                if recognized:
                    # Cooldown theo Face ID cho các event MỚI của người quen.
                    last = self._last_face_event.get(face_id)
                    if last is not None and now - last < self.dedup_seconds:
                        self._dedup_skipped += 1
                        continue
                    self._last_face_event[face_id] = now
                else:
                    await self._record_unknown_face(face_id)

                payload = build_payload(candidate)
                self._events_processed += 1
                self._record_history(face_id, payload[ATTR_EVENT_TIME])
                self.hass.bus.async_fire(EVENT_FACE_DETECTED, payload)
                self._notify_face(payload)
                if not recognized:
                    self._mark_stranger()

        self._baseline_done = True
        await self._async_daily_prune()

        # Giữ bộ nhớ dedup có giới hạn (dài hơn cửa sổ history).
        expiry = now - max(self.history_seconds * 2, 300)
        self._seen_events = {
            key: seen_at
            for key, seen_at in self._seen_events.items()
            if seen_at >= expiry
        }

        if latest is None:
            return self.data or {
                ATTR_FACE_ID: None,
                ATTR_NAME: DEFAULT_FACE_NAME,
                ATTR_RECOGNIZED: False,
            }

        return latest

    @staticmethod
    def _event_timestamp_seconds(value: Any) -> float:
        """Normalize a C260 event timestamp to Unix seconds."""
        try:
            timestamp = float(value)
        except (TypeError, ValueError):
            return 0.0
        if timestamp > 10_000_000_000:
            timestamp /= 1000.0
        return timestamp

    @classmethod
    def _event_timestamp_iso(cls, start_time: Any, end_time: Any) -> str:
        """Return the camera event time as an ISO-8601 UTC timestamp."""
        timestamp = cls._event_timestamp_seconds(start_time)
        if timestamp <= 0:
            timestamp = cls._event_timestamp_seconds(end_time)
        if timestamp <= 0:
            return datetime.now(timezone.utc).isoformat()
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    async def _record_unknown_face(self, face_id: str) -> None:
        """Persist an unknown Face ID for later classification."""
        now = datetime.now(timezone.utc).isoformat()
        item = self._unknown_faces.get(face_id)
        if item is None:
            self._unknown_faces[face_id] = {
                "first_seen": now,
                "last_seen": now,
                "count": 1,
            }
            self._cap_unknown()
            await self._unknown_store.async_save(self._unknown_faces)
            return

        item["last_seen"] = now
        item["count"] = int(item.get("count", 0)) + 1

        # Avoid writing storage on every polling cycle.
        last_saved = item.get("last_saved")
        try:
            should_save = (
                last_saved is None
                or datetime.fromisoformat(last_saved)
                < datetime.now(timezone.utc) - timedelta(seconds=60)
            )
        except (TypeError, ValueError):
            should_save = True

        if should_save:
            item["last_saved"] = now
            await self._unknown_store.async_save(self._unknown_faces)

    # ------------------------------------------------ stranger / events
    @callback
    def async_add_face_listener(
        self, listener: Callable[[dict[str, Any]], None]
    ) -> Callable[[], None]:
        """Nhận payload của mỗi event khuôn mặt MỚI (cho entity `event`)."""
        self._face_listeners.append(listener)

        @callback
        def _remove() -> None:
            if listener in self._face_listeners:
                self._face_listeners.remove(listener)

        return _remove

    def _notify_face(self, payload: dict[str, Any]) -> None:
        for listener in list(self._face_listeners):
            try:
                listener(payload)
            except Exception:  # noqa: BLE001 - một listener lỗi không được chặn polling
                _LOGGER.exception("Face event listener failed")

    def _mark_stranger(self) -> None:
        """Bật "Stranger Detected" và hẹn giờ tự tắt (mỗi lần thấy lại thì gia hạn)."""
        self.stranger_active = True
        self._cancel_stranger_timer()
        self._stranger_unsub = async_call_later(
            self.hass, self.stranger_clear_seconds, self._clear_stranger
        )

    @callback
    def _clear_stranger(self, _now: datetime | None = None) -> None:
        self._stranger_unsub = None
        self.stranger_active = False
        self.async_update_listeners()

    def _cancel_stranger_timer(self) -> None:
        if self._stranger_unsub is not None:
            self._stranger_unsub()
            self._stranger_unsub = None

    @callback
    def async_cancel_timers(self) -> None:
        self._cancel_stranger_timer()
        self.stranger_active = False

    @property
    def unknown_today(self) -> int:
        """Số lần người lạ xuất hiện hôm nay (giờ địa phương)."""
        known = set(self.faces)
        bucket = self.history.days.get(dt_util.now().date().isoformat(), {})
        return sum(n for fid, n in bucket.items() if fid not in known)

    @property
    def last_unknown_seen(self) -> datetime | None:
        known = set(self.faces)
        latest = max(
            (v for fid, v in self.history.last_seen.items() if fid not in known),
            default=None,
        )
        if not latest:
            return None
        try:
            parsed = datetime.fromisoformat(latest)
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    # ------------------------------------------------------------ history
    def _schedule_history_save(self) -> None:
        self._history_store.async_delay_save(
            self.history.to_dict, HISTORY_SAVE_DELAY
        )

    def _record_history(self, face_id: str, event_iso: str) -> None:
        """Ghi một lần xuất hiện vào ngày (giờ địa phương) của event."""
        try:
            moment = datetime.fromisoformat(event_iso)
            if moment.tzinfo is None:
                moment = moment.replace(tzinfo=timezone.utc)
            day = dt_util.as_local(moment).date()
        except (TypeError, ValueError):
            moment = dt_util.utcnow()
            day = dt_util.now().date()
        self.history.record(
            face_id, day, moment.astimezone(timezone.utc).isoformat(), at=moment
        )
        self._schedule_history_save()

    def _prune_unknown(self) -> bool:
        """Bỏ người lạ lâu không thấy hơn `retention_days`."""
        cutoff = dt_util.utcnow() - timedelta(days=self.retention_days)
        stale: list[str] = []
        for face_id, item in self._unknown_faces.items():
            try:
                seen = datetime.fromisoformat(str(item.get("last_seen")))
            except (TypeError, ValueError):
                continue
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=timezone.utc)
            if seen < cutoff:
                stale.append(face_id)
        for face_id in stale:
            self._unknown_faces.pop(face_id, None)
        return bool(stale)

    def _cap_unknown(self) -> bool:
        """Giữ tối đa `max_unknown_faces` người lạ (bỏ người lâu không thấy nhất)."""
        excess = len(self._unknown_faces) - self.max_unknown_faces
        if excess <= 0:
            return False
        oldest = sorted(
            self._unknown_faces,
            key=lambda fid: str(self._unknown_faces[fid].get("last_seen", "")),
        )[:excess]
        for face_id in oldest:
            self._unknown_faces.pop(face_id, None)
        return True

    def _prune_all(self) -> bool:
        """Áp dụng giới hạn ngày / số lượng. True nếu có thay đổi."""
        changed = self.history.prune(self.retention_days, dt_util.now().date())
        changed |= self._prune_unknown()
        changed |= self._cap_unknown()
        return changed

    async def _async_daily_prune(self) -> None:
        today = dt_util.now().date()
        if self._last_prune_day == today:
            return
        self._last_prune_day = today
        if self._prune_all():
            await self._unknown_store.async_save(self._unknown_faces)
            self._schedule_history_save()
            if self.data is not None:
                self.async_update_listeners()

    async def async_flush(self) -> None:
        """Ghi ngay mọi dữ liệu đang chờ (gọi khi unload)."""
        await self._unknown_store.async_save(self._unknown_faces)
        await self._history_store.async_save(self.history.to_dict())

    async def async_merge_face_history(self, old_id: str, new_id: str) -> None:
        """Gộp lịch sử khi người dùng đổi Face ID của một người."""
        if self.history.merge(old_id, new_id):
            self._schedule_history_save()

    async def async_forget_unknown(self, face_id: str) -> bool:
        """Bỏ một người lạ khỏi danh sách và xoá thống kê của ID đó."""
        face_id = str(face_id)
        if face_id not in self._unknown_faces:
            return False
        self._unknown_faces.pop(face_id)
        self.history.purge(face_id)
        await self._unknown_store.async_save(self._unknown_faces)
        self._schedule_history_save()
        self.async_update_listeners()
        return True

    async def async_clear_unknown(self) -> int:
        """Xoá toàn bộ người lạ (danh sách + thống kê). Trả về số ID đã xoá."""
        known = set(self.faces)
        removed = len(self._unknown_faces)
        self._unknown_faces = {}
        self.history.purge_where(lambda face_id: face_id not in known)
        await self._unknown_store.async_save(self._unknown_faces)
        self._schedule_history_save()
        self.async_update_listeners()
        return removed

    def get_day(self, day: date) -> dict[str, Any]:
        """Ai xuất hiện lúc nào trong `day` (giờ địa phương của HA)."""
        return self.history.day_view(
            self.faces, day, dt_util.get_default_time_zone()
        )

    def get_stats(self, range_days: int) -> dict[str, Any]:
        """Thống kê; tên và phân loại người quen/lạ tính theo danh sách hiện tại."""
        return self.history.stats(self.faces, dt_util.now().date(), range_days)

    async def async_face_map_changed(self) -> None:
        """Đồng bộ danh sách người lạ với danh sách người quen và refresh state.

        - ID mới được đặt tên: bỏ khỏi danh sách người lạ.
        - Người quen bị xoá: ID quay lại danh sách người lạ cùng số liệu cũ.
        """
        known_ids = set(self.faces)
        removed = self._known_snapshot - known_ids
        self._known_snapshot = known_ids
        changed = False
        for face_id in list(self._unknown_faces):
            if face_id in known_ids:
                self._unknown_faces.pop(face_id, None)
                changed = True
        for face_id in removed:
            if face_id in self._unknown_faces:
                continue
            summary = self.history.summary(face_id)
            if summary is None:
                continue
            try:
                first_seen = dt_util.start_of_local_day(
                    date.fromisoformat(summary["first_day"])
                ).isoformat()
            except (TypeError, ValueError):
                first_seen = dt_util.utcnow().isoformat()
            self._unknown_faces[face_id] = {
                "first_seen": first_seen,
                "last_seen": summary["last_seen"] or first_seen,
                "count": summary["count"],
            }
            changed = True
        if changed:
            self._cap_unknown()
            await self._unknown_store.async_save(self._unknown_faces)
        self.async_face_map_updated()

    async def async_apply_options(self) -> None:
        """Apply updated Face mappings, polling and retention options immediately."""
        options = self.entry.options

        self.poll_interval = int(
            options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
        )
        self.history_seconds = int(
            options.get(CONF_HISTORY_SECONDS, DEFAULT_HISTORY_SECONDS)
        )
        self.dedup_seconds = int(
            options.get(CONF_DEDUP_SECONDS, DEFAULT_DEDUP_SECONDS)
        )
        self.update_interval = timedelta(seconds=self.poll_interval)
        self.stranger_clear_seconds = _clamp(
            options.get(CONF_STRANGER_CLEAR_SECONDS),
            DEFAULT_STRANGER_CLEAR_SECONDS,
            MIN_STRANGER_CLEAR_SECONDS,
            MAX_STRANGER_CLEAR_SECONDS,
        )
        self.retention_days = _clamp(
            options.get(CONF_RETENTION_DAYS),
            DEFAULT_RETENTION_DAYS,
            MIN_RETENTION_DAYS,
            MAX_RETENTION_DAYS,
        )
        self.max_unknown_faces = _clamp(
            options.get(CONF_MAX_UNKNOWN_FACES),
            DEFAULT_MAX_UNKNOWN_FACES,
            MIN_MAX_UNKNOWN_FACES,
            MAX_MAX_UNKNOWN_FACES,
        )

        # Áp dụng giới hạn mới ngay, không cần chờ qua ngày.
        if self._prune_all():
            await self._unknown_store.async_save(self._unknown_faces)
            self._schedule_history_save()

        # Re-evaluate the currently displayed Face ID immediately.
        await self.async_face_map_changed()

        # Refresh so the new polling/history settings take effect without
        # requiring an integration reload or HA restart.
        await self.async_request_refresh()

    @callback
    def async_face_map_updated(self) -> None:
        """Update current state after mapping changes."""
        if not self.data or not self.data.get(ATTR_FACE_ID):
            return

        face_id = str(self.data[ATTR_FACE_ID])
        name, recognized = self.lookup_face(face_id)
        self.async_set_updated_data(
            {
                **self.data,
                ATTR_NAME: name,
                ATTR_RECOGNIZED: recognized,
            }
        )
