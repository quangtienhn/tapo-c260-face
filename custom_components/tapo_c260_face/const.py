"""Constants for the Tapo C260 Face Recognition integration."""
from __future__ import annotations

DOMAIN = "tapo_c260_face"
MANUFACTURER = "TP-Link"
MODEL = "Tapo C260"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_CLOUD_PASSWORD = "cloud_password"

CONF_POLL_INTERVAL = "poll_interval"
CONF_HISTORY_SECONDS = "history_seconds"
CONF_DEDUP_SECONDS = "dedup_seconds"
CONF_FACES = "faces"
CONF_SHOW_SIDEBAR = "show_sidebar"
CONF_SIDEBAR_TITLE = "sidebar_title"
CONF_RETENTION_DAYS = "retention_days"
CONF_STRANGER_CLEAR_SECONDS = "stranger_clear_seconds"
CONF_MAX_UNKNOWN_FACES = "max_unknown_faces"

DEFAULT_POLL_INTERVAL = 10
DEFAULT_HISTORY_SECONDS = 120
DEFAULT_DEDUP_SECONDS = 60
DEFAULT_FACE_NAME = "Stranger"
DEFAULT_SHOW_SIDEBAR = True
DEFAULT_SIDEBAR_TITLE = "Tapo C260 Face Manager"
MAX_SIDEBAR_TITLE_LEN = 40
# Lưu trữ: lịch sử xuất hiện giữ tối đa N ngày; danh sách người lạ giữ tối đa M
# người (bỏ người lạ lâu không thấy nhất trước).
DEFAULT_RETENTION_DAYS = 90
DEFAULT_MAX_UNKNOWN_FACES = 100
# Binary sensor "Stranger Detected" tự tắt sau ngần này giây kể từ lần thấy người lạ cuối.
DEFAULT_STRANGER_CLEAR_SECONDS = 30
MIN_STRANGER_CLEAR_SECONDS = 5
MAX_STRANGER_CLEAR_SECONDS = 600
MIN_RETENTION_DAYS = 1
MAX_RETENTION_DAYS = 365
MIN_MAX_UNKNOWN_FACES = 10
MAX_MAX_UNKNOWN_FACES = 1000

EVENT_FACE_DETECTED = f"{DOMAIN}_detected"

ATTR_FACE_ID = "face_id"
ATTR_NAME = "name"
ATTR_RECOGNIZED = "recognized"
ATTR_EVENT_TIME = "event_time"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_ALARM_TYPE = "alarm_type"
ATTR_EVENTS_1 = "events_1"
ATTR_CAMERA = "camera"
ATTR_EVENT_FACE_IDS = "event_face_ids"

PLATFORMS = ["sensor", "binary_sensor", "event"]
