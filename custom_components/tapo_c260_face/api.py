"""Async client for the Tapo C260 local secure API."""
from __future__ import annotations

import asyncio
import json
import logging
import secrets
from dataclasses import dataclass
from typing import Any

import aiohttp

from .crypto import aes_decrypt, aes_encrypt, sha256, sha256_buffer

_LOGGER = logging.getLogger(__name__)


class TapoC260Error(Exception):
    """Base API error."""


class TapoC260AuthError(TapoC260Error):
    """Authentication or secure-session error."""


class TapoC260ConnectionError(TapoC260Error):
    """Connection or transport error."""


class TapoC260ProtocolError(TapoC260Error):
    """Unexpected camera response."""


@dataclass
class TapoSession:
    """Verified C260 secure-channel session."""

    stok: str
    seq: int
    lsk: bytes
    ivb: bytes
    tag_prefix: str


class TapoC260Api:
    """Implement the verified C260 login and securePassthrough flow."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        username: str,
        cloud_password: str,
        hass: Any | None = None,
    ) -> None:
        self._session = session
        self._hass = hass
        self.host = host
        self.username = username
        self.cloud_password = cloud_password
        self._secure: TapoSession | None = None
        self._lock = asyncio.Lock()
        # When Tapo-Control owns this camera, use its existing pytapo.Tapo
        # instance instead of creating a second camera session.
        self.shared_controller: Any | None = None

    async def async_login(self) -> TapoSession:
        """Perform the C260 challenge/login handshake."""
        cnonce = secrets.token_hex(8).upper()

        challenge = await self._post(
            "/",
            {
                "method": "login",
                "params": {
                    "encrypt_type": "3",
                    "username": self.username,
                    "cnonce": cnonce,
                },
            },
        )

        data = challenge.get("result", {}).get("data", {})
        nonce = data.get("nonce")
        device_confirm = data.get("device_confirm")

        # The C260 can return a non-zero outer challenge code while still
        # providing usable nonce/device_confirm data.
        if not nonce or not device_confirm:
            raise TapoC260AuthError(
                f"Challenge failed: {challenge!r}"
            )

        hashed_password = sha256(self.cloud_password)

        expected_confirm = (
            sha256(cnonce + hashed_password + nonce)
            + nonce
            + cnonce
        )

        if expected_confirm.upper() != device_confirm.upper():
            raise TapoC260AuthError("device_confirm mismatch")

        digest = sha256(hashed_password + cnonce + nonce)
        digest_password = digest + cnonce + nonce

        login_response = await self._post(
            "/",
            {
                "method": "login",
                "params": {
                    "cnonce": cnonce,
                    "encrypt_type": "3",
                    "digest_passwd": digest_password,
                    "username": self.username,
                },
            },
        )

        if login_response.get("error_code") != 0:
            raise TapoC260AuthError(
                f"Login failed: {login_response!r}"
            )

        result = login_response.get("result") or {}
        stok = result.get("stok")
        if not stok:
            raise TapoC260ProtocolError(
                f"Login response has no stok: {login_response!r}"
            )

        try:
            start_seq = int(result["start_seq"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TapoC260ProtocolError(
                f"Login response has invalid start_seq: {login_response!r}"
            ) from exc

        hashed_key = sha256(cnonce + hashed_password + nonce)
        lsk_full = sha256_buffer(
            "lsk" + cnonce + nonce + hashed_key
        )
        ivb_full = sha256_buffer(
            "ivb" + cnonce + nonce + hashed_key
        )

        self._secure = TapoSession(
            stok=stok,
            seq=start_seq,
            lsk=lsk_full[:16],
            ivb=ivb_full[:16],
            tag_prefix=sha256(hashed_password + cnonce),
        )
        return self._secure

    async def _post(
        self,
        path: str,
        body: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """POST JSON to the camera."""
        url = f"https://{self.host}{path}"
        request_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Tapo CameraClient Android",
            "requestByApp": "true",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)

        try:
            async with self._session.post(
                url,
                json=body,
                headers=request_headers,
                ssl=False,
            ) as response:
                raw = await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise TapoC260ConnectionError(
                f"Unable to connect to Tapo C260 at {self.host}: {exc}"
            ) from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TapoC260ProtocolError(
                f"Camera returned invalid JSON: {raw[:300]}"
            ) from exc

    async def async_secure_request(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send one encrypted securePassthrough request."""
        async with self._lock:
            if self._secure is None:
                await self.async_login()

            assert self._secure is not None
            session = self._secure

            inner_json = json.dumps(
                payload,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            encrypted = aes_encrypt(
                inner_json,
                session.lsk,
                session.ivb,
            )

            outer = {
                "method": "securePassthrough",
                "params": {"request": encrypted},
            }
            outer_json = json.dumps(
                outer,
                separators=(",", ":"),
                ensure_ascii=False,
            )

            seq = session.seq
            tapo_tag = sha256(
                session.tag_prefix + outer_json + str(seq)
            )

            response = await self._post(
                f"/stok={session.stok}/ds",
                outer,
                headers={
                    "Seq": str(seq),
                    "Tapo_tag": tapo_tag,
                },
            )
            session.seq += 1

            if response.get("error_code") != 0:
                self._secure = None
                raise TapoC260AuthError(
                    f"securePassthrough failed: {response!r}"
                )

            encrypted_response = (
                response.get("result", {}).get("response")
            )
            if not encrypted_response:
                raise TapoC260ProtocolError(
                    f"No encrypted response: {response!r}"
                )

            try:
                plaintext = aes_decrypt(
                    encrypted_response,
                    session.lsk,
                    session.ivb,
                )
                return json.loads(plaintext)
            except (ValueError, json.JSONDecodeError) as exc:
                self._secure = None
                raise TapoC260ProtocolError(
                    "Unable to decrypt/parse secure response"
                ) from exc

    async def _async_search_with_shared_controller(
        self,
        history_seconds: int,
    ) -> list[dict[str, Any]]:
        """Query detections using Tapo-Control's already-authenticated controller.

        Errors here deliberately remain connection/protocol errors. The Face
        integration must not trigger its own login flow while borrowing a
        controller owned by Tapo-Control.
        """
        import time

        controller = self.shared_controller
        if controller is None:
            raise TapoC260ConnectionError("Shared Tapo-Control controller unavailable")

        now = int(time.time())
        params = {
            "playback": {
                "search_detection_list": {
                    "start_index": 0,
                    "end_index": 999,
                    "channel": 0,
                    "start_time": now - history_seconds,
                    "end_time": now + 5,
                }
            }
        }

        try:
            if self._hass is None:
                raise RuntimeError("Home Assistant instance is not configured")
            async with asyncio.timeout(30):
                response = await self._hass.async_add_executor_job(
                    controller.executeFunction,
                    "searchDetectionList",
                    params,
                )
        except Exception as exc:
            raise TapoC260ConnectionError(
                f"Shared Tapo-Control request failed: {exc}"
            ) from exc

        # pytapo versions may return the method result directly or wrap it in
        # the full response. Accept both known response shapes.
        candidates = [response]
        if isinstance(response, dict):
            result = response.get("result")
            if isinstance(result, dict):
                candidates.append(result)
                playback = result.get("playback")
                if isinstance(playback, dict):
                    candidates.append(playback)
            playback = response.get("playback")
            if isinstance(playback, dict):
                candidates.append(playback)

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            events = candidate.get("search_detection_list")
            if isinstance(events, list):
                return events
            events = candidate.get("events")
            if isinstance(events, list):
                return events

        raise TapoC260ProtocolError(
            f"Unexpected shared searchDetectionList response: {response!r}"
        )

    async def async_search_detection_list(
        self,
        history_seconds: int,
    ) -> list[dict[str, Any]]:
        """Fetch recent detection events, preferring Tapo-Control's controller."""
        import time

        if self.shared_controller is not None:
            return await self._async_search_with_shared_controller(history_seconds)

        now = int(time.time())
        payload = {
            "method": "multipleRequest",
            "params": {
                "requests": [
                    {
                        "method": "searchDetectionList",
                        "params": {
                            "playback": {
                                "search_detection_list": {
                                    "start_index": 0,
                                    "end_index": 999,
                                    "channel": 0,
                                    "start_time": now - history_seconds,
                                    "end_time": now + 5,
                                }
                            }
                        },
                    }
                ]
            },
        }

        response = await self.async_secure_request(payload)
        events = (
            response.get("result", {})
            .get("responses", [{}])[0]
            .get("result", {})
            .get("playback", {})
            .get("search_detection_list")
        )

        if not isinstance(events, list):
            raise TapoC260ProtocolError(
                f"Invalid detection response: {response!r}"
            )

        return events
