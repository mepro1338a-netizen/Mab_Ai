"""OAuth token obfuscation — uses OAUTH_STATE_SECRET from ENV (no hardcoded secrets)."""
from __future__ import annotations

import base64
import hashlib
import os


def _secret() -> bytes:
    raw = (
        os.getenv("VIDEO_TOKEN_ENCRYPT_KEY", "").strip()
        or os.getenv("OAUTH_STATE_SECRET", "").strip()
    )
    if not raw:
        return b""
    return hashlib.sha256(raw.encode("utf-8")).digest()


def encrypt_token(plain: str) -> str:
    if not plain:
        return ""
    key = _secret()
    if not key:
        return ""
    data = plain.encode("utf-8")
    xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.urlsafe_b64encode(xored).decode("ascii")


def decrypt_token(enc: str) -> str:
    if not enc:
        return ""
    key = _secret()
    if not key:
        return ""
    try:
        data = base64.urlsafe_b64decode(enc.encode("ascii"))
        plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return plain.decode("utf-8")
    except Exception:
        return ""
