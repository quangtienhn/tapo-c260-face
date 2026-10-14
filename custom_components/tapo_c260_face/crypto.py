"""Cryptographic helpers for the verified Tapo C260 secure channel."""
from __future__ import annotations

import base64
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def sha256(text: str) -> str:
    """Return uppercase SHA-256 hex digest."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def sha256_buffer(text: str) -> bytes:
    """Return raw SHA-256 digest."""
    return hashlib.sha256(text.encode("utf-8")).digest()


def _pkcs7_pad(data: bytes) -> bytes:
    pad = 16 - (len(data) % 16)
    return data + bytes([pad]) * pad


def _pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        raise ValueError("Empty AES plaintext")
    pad = data[-1]
    if pad < 1 or pad > 16 or data[-pad:] != bytes([pad]) * pad:
        raise ValueError("Invalid AES padding")
    return data[:-pad]


def aes_encrypt(text: str, key: bytes, iv: bytes) -> str:
    """Encrypt UTF-8 text with AES-128-CBC and return base64."""
    encryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
    ).encryptor()
    encrypted = encryptor.update(_pkcs7_pad(text.encode("utf-8")))
    encrypted += encryptor.finalize()
    return base64.b64encode(encrypted).decode("ascii")


def aes_decrypt(data: str, key: bytes, iv: bytes) -> str:
    """Decrypt base64 AES-128-CBC data."""
    decryptor = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
    ).decryptor()
    plaintext = decryptor.update(base64.b64decode(data))
    plaintext += decryptor.finalize()
    return _pkcs7_unpad(plaintext).decode("utf-8")
