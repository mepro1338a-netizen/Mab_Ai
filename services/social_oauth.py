"""
Social platform OAuth — connect YouTube / Instagram / TikTok for publishing.
Separate from login OAuth; tokens stored encrypted in social_connections.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timezone
from urllib.parse import unquote, urlencode

from db.core import normalize_username

import requests

from config import (
    APP_BASE_URL,
    META_APP_ID,
    META_APP_SECRET,
    OAUTH_STATE_SECRET,
    TIKTOK_CLIENT_KEY,
    TIKTOK_CLIENT_SECRET,
    YOUTUBE_OAUTH_CLIENT_ID,
    YOUTUBE_OAUTH_CLIENT_SECRET,
)
from db.video_engine import save_social_connection
from oauth_service import oauth_state_ready, resolve_public_origin
from services.token_secure import encrypt_token
from services.youtube_api import parse_youtube_error

SOCIAL_PLATFORMS: dict[str, dict] = {
    "youtube_shorts": {
        "label": "YouTube Shorts",
        "connect_provider": "youtube",
        "api_ready": True,
        "review_note": "",
        "scopes": (
            "https://www.googleapis.com/auth/youtube.upload "
            "https://www.googleapis.com/auth/youtube.readonly "
            "openid email profile"
        ),
    },
    "instagram_reels": {
        "label": "Instagram Reels",
        "connect_provider": "instagram",
        "api_ready": False,
        "review_note": "Meta App Review für Publishing erforderlich.",
        "scopes": "instagram_basic,pages_show_list,instagram_content_publish",
    },
    "tiktok": {
        "label": "TikTok",
        "connect_provider": "tiktok",
        "api_ready": False,
        "review_note": "TikTok Content Posting API — Partner-Freigabe nötig.",
        "scopes": "video.publish,video.upload,user.info.basic",
    },
}

STATE_MAX_AGE = 900


def _state_key() -> bytes:
    secret = (OAUTH_STATE_SECRET or "").strip()
    if secret:
        return secret.encode("utf-8")
    base = APP_BASE_URL.lower()
    if "localhost" in base or "127.0.0.1" in base:
        return b"mabyte-social-oauth-dev"
    return b""


def social_oauth_ready() -> bool:
    return bool(_state_key())


def make_social_state(username: str, platform: str) -> str:
    if not social_oauth_ready():
        return ""
    payload = {
        "k": "social",
        "u": (username or "").strip().lower(),
        "pl": platform,
        "t": int(time.time()),
        "n": secrets.token_urlsafe(10),
    }
    raw = json.dumps(payload, separators=(",", ":"))
    sig = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:24]
    return base64.urlsafe_b64encode(f"{raw}|{sig}".encode()).decode()


def _normalize_state_param(state: str) -> str:
    """Repair state after URL/query decoding (padding, spaces)."""
    s = unquote((state or "").strip())
    if not s:
        return ""
    s = s.replace(" ", "+")
    pad = "=" * (-len(s) % 4)
    return s + pad


def verify_social_state(state: str) -> tuple[str, str, str]:
    """
    Returns (username, platform, error_code).
    error_code: '' | 'missing' | 'config' | 'invalid' | 'expired'
    """
    if not state:
        return "", "", "missing"
    if not social_oauth_ready():
        return "", "", "config"
    try:
        decoded = base64.urlsafe_b64decode(_normalize_state_param(state).encode()).decode()
        raw, sig = decoded.rsplit("|", 1)
        expected = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:24]
        if not sig or not hmac.compare_digest(sig, expected):
            return "", "", "invalid"
        payload = json.loads(raw)
        if payload.get("k") != "social":
            return "", "", "invalid"
        if int(time.time()) - int(payload["t"]) > STATE_MAX_AGE:
            return "", "", "expired"
        user = normalize_username(str(payload.get("u") or ""))
        platform = str(payload.get("pl") or "").strip()
        if not user or not platform:
            return "", "", "invalid"
        return user, platform, ""
    except Exception:
        return "", "", "invalid"


def social_state_error_message(code: str) -> str:
    messages = {
        "missing": "OAuth-Antwort unvollständig. Bitte erneut auf «Verbinden» klicken.",
        "config": "OAUTH_STATE_SECRET fehlt auf dem Server. Administrator muss Railway prüfen.",
        "invalid": "OAuth-Sitzung ungültig. Bitte erneut verbinden.",
        "expired": "OAuth-Sitzung abgelaufen (15 Min.). Bitte erneut verbinden.",
    }
    return messages.get(code, messages["invalid"])


def social_redirect_uri() -> str:
    origin = resolve_public_origin().rstrip("/")
    return f"{origin}/?page=social_oauth"


def platform_configured(platform_id: str) -> bool:
    meta = SOCIAL_PLATFORMS.get(platform_id) or {}
    prov = meta.get("connect_provider", "")
    if prov == "youtube":
        return bool(YOUTUBE_OAUTH_CLIENT_ID and YOUTUBE_OAUTH_CLIENT_SECRET and social_oauth_ready())
    if prov == "instagram":
        return bool(META_APP_ID and META_APP_SECRET and social_oauth_ready())
    if prov == "tiktok":
        return bool(TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET and social_oauth_ready())
    return False


def connect_auth_url(username: str, platform_id: str) -> str:
    state = make_social_state(username, platform_id)
    if not state:
        return ""
    meta = SOCIAL_PLATFORMS.get(platform_id) or {}
    prov = meta.get("connect_provider", "")
    redirect = social_redirect_uri()

    if prov == "youtube":
        if not YOUTUBE_OAUTH_CLIENT_ID:
            return ""
        params = {
            "client_id": YOUTUBE_OAUTH_CLIENT_ID,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": meta.get("scopes", ""),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    if prov == "instagram":
        params = {
            "client_id": META_APP_ID,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": meta.get("scopes", "email,public_profile"),
            "state": state,
        }
        return "https://www.facebook.com/v21.0/dialog/oauth?" + urlencode(params)

    if prov == "tiktok":
        params = {
            "client_key": TIKTOK_CLIENT_KEY,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": meta.get("scopes", "user.info.basic"),
            "state": state,
        }
        return "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)

    return ""


def _expires_iso(expires_in: int | None) -> str:
    if not expires_in:
        return ""
    return datetime.fromtimestamp(
        time.time() + int(expires_in), tz=timezone.utc
    ).isoformat()


def complete_social_connect(
    platform_id: str,
    code: str,
    *,
    username: str,
) -> tuple[bool, str]:
    """Exchange code and store tokens — no secrets exposed to frontend."""
    meta = SOCIAL_PLATFORMS.get(platform_id) or {}
    prov = meta.get("connect_provider", "")
    code = (code or "").strip()
    if not code:
        return False, "OAuth-Code fehlt."

    channel_id = ""
    try:
        if prov == "youtube":
            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": YOUTUBE_OAUTH_CLIENT_ID,
                    "client_secret": YOUTUBE_OAUTH_CLIENT_SECRET,
                    "redirect_uri": social_redirect_uri(),
                    "grant_type": "authorization_code",
                },
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            access = data.get("access_token", "")
            refresh = data.get("refresh_token", "")
            expires = _expires_iso(data.get("expires_in"))
            label = "YouTube"
            ch = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"part": "snippet", "mine": "true"},
                headers={"Authorization": f"Bearer {access}"},
                timeout=20,
            )
            if ch.ok:
                items = ch.json().get("items") or []
                if items:
                    label = items[0].get("snippet", {}).get("title") or label
                    channel_id = items[0].get("id") or ""
            elif ch.status_code in (401, 403):
                return False, parse_youtube_error(ch)

        elif prov == "instagram":
            resp = requests.get(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={
                    "client_id": META_APP_ID,
                    "client_secret": META_APP_SECRET,
                    "redirect_uri": social_redirect_uri(),
                    "code": code,
                },
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            access = data.get("access_token", "")
            refresh = ""
            expires = _expires_iso(data.get("expires_in"))
            label = "Instagram"

        elif prov == "tiktok":
            resp = requests.post(
                "https://open.tiktokapis.com/v2/oauth/token/",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_key": TIKTOK_CLIENT_KEY,
                    "client_secret": TIKTOK_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": social_redirect_uri(),
                },
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            access = data.get("access_token", "")
            refresh = data.get("refresh_token", "")
            expires = _expires_iso(data.get("expires_in"))
            label = "TikTok"
        else:
            return False, "Unbekannte Plattform."

        if not access:
            return False, "Kein Access-Token erhalten."

        if prov == "youtube" and not refresh:
            return False, (
                "YouTube: Kein Refresh-Token erhalten. "
                "Bitte Verbindung trennen und erneut verbinden (Google fragt Zustimmung ab)."
            )

        enc_a = encrypt_token(access)
        if not enc_a:
            return False, "OAUTH_STATE_SECRET fehlt — Token kann nicht gespeichert werden."

        save_social_connection(
            username,
            platform_id,
            access_token_enc=enc_a,
            refresh_token_enc=encrypt_token(refresh) if refresh else "",
            token_expires_at=expires,
            scopes=meta.get("scopes", ""),
            account_label=label,
            channel_id=channel_id,
        )
        detail = f" — Kanal „{label}“" if label and prov == "youtube" else ""
        return True, f"{meta.get('label', platform_id)} verbunden{detail}."

    except requests.HTTPError as exc:
        resp = getattr(exc, "response", None)
        if resp is not None:
            return False, parse_youtube_error(resp)
        return False, "OAuth-Verbindung fehlgeschlagen. Bitte erneut versuchen."
    except requests.Timeout:
        return False, "Zeitüberschreitung bei der OAuth-Verbindung."
    except requests.RequestException:
        return False, "Netzwerkfehler bei der OAuth-Verbindung."
    except Exception:
        return False, "Verbindung fehlgeschlagen. Bitte erneut versuchen."
