import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode

import requests

from config import (
    APP_BASE_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    META_APP_ID,
    META_APP_SECRET,
    OAUTH_STATE_SECRET,
    TIKTOK_CLIENT_KEY,
    TIKTOK_CLIENT_SECRET,
)
from database import oauth_login_or_register


PROVIDERS = ("google", "instagram", "tiktok")


def _state_key() -> bytes:
    secret = OAUTH_STATE_SECRET or GOOGLE_CLIENT_SECRET or "mabyte-oauth-dev"
    return secret.encode("utf-8")


def make_state(provider: str) -> str:
    payload = {
        "p": provider.lower(),
        "t": int(time.time()),
        "n": secrets.token_urlsafe(8),
    }
    raw = json.dumps(payload, separators=(",", ":"))
    sig = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:20]
    return base64.urlsafe_b64encode(f"{raw}|{sig}".encode()).decode()


def verify_state(state: str, max_age: int = 900) -> str:
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        raw, sig = decoded.rsplit("|", 1)
        expected = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:20]
        if not hmac.compare_digest(sig, expected):
            return ""
        payload = json.loads(raw)
        if int(time.time()) - int(payload["t"]) > max_age:
            return ""
        return str(payload.get("p") or "")
    except Exception:
        return ""


def redirect_uri() -> str:
    return APP_BASE_URL.rstrip("/") + "/"


def provider_configured(provider: str) -> bool:
    provider = provider.lower()
    if provider == "google":
        return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    if provider == "instagram":
        return bool(META_APP_ID and META_APP_SECRET)
    if provider == "tiktok":
        return bool(TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET)
    return False


def auth_url(provider: str, state: str) -> str:
    provider = provider.lower()
    redirect = redirect_uri()

    if provider == "google":
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
            "state": state,
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    if provider == "instagram":
        params = {
            "client_id": META_APP_ID,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "email,public_profile,instagram_basic",
            "state": state,
        }
        return "https://www.facebook.com/v21.0/dialog/oauth?" + urlencode(params)

    if provider == "tiktok":
        params = {
            "client_key": TIKTOK_CLIENT_KEY,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": "user.info.basic",
            "state": state,
        }
        return "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)

    return ""


def _exchange_google(code: str) -> dict:
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri(),
            "grant_type": "authorization_code",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _profile_google(access_token: str) -> dict:
    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _exchange_meta(code: str) -> dict:
    response = requests.get(
        "https://graph.facebook.com/v21.0/oauth/access_token",
        params={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "redirect_uri": redirect_uri(),
            "code": code,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _profile_meta(access_token: str) -> dict:
    response = requests.get(
        "https://graph.facebook.com/me",
        params={"fields": "id,name,email", "access_token": access_token},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _exchange_tiktok(code: str) -> dict:
    response = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri(),
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def _profile_tiktok(access_token: str) -> dict:
    response = requests.get(
        "https://open.tiktokapis.com/v2/user/info/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"fields": "open_id,union_id,avatar_url,display_name"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    data = (payload.get("data") or {}).get("user") or {}
    return {
        "sub": data.get("open_id") or data.get("union_id") or "",
        "name": data.get("display_name") or "TikTok User",
        "email": f"{data.get('open_id', 'tiktok')}@tiktok.oauth.local",
    }


def complete_oauth(provider: str, code: str) -> tuple[bool, str, dict | None]:
    provider = provider.lower()

    try:
        if provider == "google":
            token_data = _exchange_google(code)
            profile = _profile_google(token_data["access_token"])
            email = profile.get("email", "")
            name = profile.get("name") or email.split("@")[0]
            sub = profile.get("sub") or profile.get("id") or ""

        elif provider == "instagram":
            token_data = _exchange_meta(code)
            profile = _profile_meta(token_data["access_token"])
            email = profile.get("email") or f"{profile.get('id')}@meta.oauth.local"
            name = profile.get("name") or "Instagram User"
            sub = str(profile.get("id") or "")

        elif provider == "tiktok":
            token_data = _exchange_tiktok(code)
            profile = _profile_tiktok(token_data["access_token"])
            email = profile.get("email") or ""
            name = profile.get("name") or "TikTok User"
            sub = str(profile.get("sub") or "")

        else:
            return False, "Unbekannter OAuth Provider.", None

        if not sub:
            return False, "OAuth Profil unvollständig.", None

        return oauth_login_or_register(
            email=email,
            display_name=name,
            provider=provider,
            provider_sub=sub,
        )

    except requests.HTTPError as exc:
        detail = ""
        try:
            detail = exc.response.json()
        except Exception:
            detail = exc.response.text if exc.response is not None else str(exc)
        return False, f"OAuth Fehler ({provider}): {detail}", None

    except Exception as exc:
        return False, f"OAuth Fehler ({provider}): {exc}", None
