"""OAuth 2.0 — Google (primary), Instagram/Meta, TikTok."""
from __future__ import annotations

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
    GOOGLE_OAUTH_REDIRECT_PATH,
    GOOGLE_OAUTH_REDIRECT_URI,
    META_APP_ID,
    META_APP_SECRET,
    OAUTH_STATE_SECRET,
    TIKTOK_CLIENT_KEY,
    TIKTOK_CLIENT_SECRET,
)
from database import oauth_login_or_register


PROVIDERS = ("google", "instagram", "tiktok")
STATE_MAX_AGE = 900


def _is_local_base() -> bool:
    base = APP_BASE_URL.lower()
    return "localhost" in base or "127.0.0.1" in base


def _state_key() -> bytes:
    secret = (OAUTH_STATE_SECRET or "").strip()
    if secret:
        return secret.encode("utf-8")
    if _is_local_base():
        return b"mabyte-oauth-dev-local-only"
    return b""


def oauth_state_ready() -> bool:
    return bool(_state_key())


def make_state(provider: str) -> str:
    if not oauth_state_ready():
        return ""
    payload = {
        "p": provider.lower(),
        "t": int(time.time()),
        "n": secrets.token_urlsafe(12),
    }
    raw = json.dumps(payload, separators=(",", ":"))
    sig = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:24]
    return base64.urlsafe_b64encode(f"{raw}|{sig}".encode()).decode()


def verify_state(state: str, max_age: int = STATE_MAX_AGE) -> str:
    if not state or not oauth_state_ready():
        return ""
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        raw, sig = decoded.rsplit("|", 1)
        expected = hmac.new(_state_key(), raw.encode(), hashlib.sha256).hexdigest()[:24]
        if not sig or not hmac.compare_digest(sig, expected):
            return ""
        payload = json.loads(raw)
        if payload.get("p") not in PROVIDERS:
            return ""
        if int(time.time()) - int(payload["t"]) > max_age:
            return ""
        return str(payload["p"])
    except Exception:
        return ""


def resolve_public_origin() -> str:
    """
    Öffentliche App-URL — bevorzugt Request-Host (mabyte.de),
    falls APP_BASE_URL noch auf Railway zeigt.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        headers = getattr(ctx, "request_headers", None) or {}
        host = (headers.get("X-Forwarded-Host") or headers.get("Host") or "").strip()
        if isinstance(host, str) and "," in host:
            host = host.split(",")[0].strip()
        proto = (headers.get("X-Forwarded-Proto") or "https").strip().split(",")[0]
        if host and "localhost" not in host.lower() and "127.0.0.1" not in host:
            return f"{proto}://{host}".rstrip("/")
    except Exception:
        pass
    return APP_BASE_URL.rstrip("/")


def google_redirect_uri() -> str:
    if GOOGLE_OAUTH_REDIRECT_URI:
        return GOOGLE_OAUTH_REDIRECT_URI.strip()

    origin = resolve_public_origin()
    path = GOOGLE_OAUTH_REDIRECT_PATH.strip() or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path == "/":
        return f"{origin}/"
    return f"{origin}{path.rstrip('/')}"


def google_oauth_diagnostics() -> dict[str, str]:
    """Hilfe für Admin/Debug — keine Secrets."""
    redirect = google_redirect_uri()
    issues = []
    if not GOOGLE_CLIENT_ID:
        issues.append("GOOGLE_CLIENT_ID fehlt")
    if not GOOGLE_CLIENT_SECRET:
        issues.append("GOOGLE_CLIENT_SECRET fehlt")
    if not oauth_state_ready():
        issues.append("OAUTH_STATE_SECRET fehlt (Pflicht in Production)")
    if GOOGLE_CLIENT_ID and ".apps.googleusercontent.com" not in GOOGLE_CLIENT_ID:
        issues.append("Client-ID Format prüfen (Web-Application)")
    return {
        "public_origin": resolve_public_origin(),
        "redirect_uri": redirect,
        "app_base_url_env": APP_BASE_URL,
        "issues": "; ".join(issues) if issues else "OK",
    }


def redirect_uri(provider: str = "") -> str:
    """Provider-specific OAuth redirect URI (must match Google Console)."""
    if provider.lower() == "google":
        return google_redirect_uri()
    return f"{APP_BASE_URL}/"


def provider_configured(provider: str) -> bool:
    provider = provider.lower()
    if provider == "google":
        return bool(
            GOOGLE_CLIENT_ID
            and GOOGLE_CLIENT_SECRET
            and oauth_state_ready()
        )
    if provider == "instagram":
        return bool(META_APP_ID and META_APP_SECRET and oauth_state_ready())
    if provider == "tiktok":
        return bool(TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET and oauth_state_ready())
    return False


def auth_url(provider: str, state: str) -> str:
    if not state:
        return ""
    provider = provider.lower()
    redirect = redirect_uri(provider)

    if provider == "google":
        if not GOOGLE_CLIENT_ID or not redirect:
            return ""
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
            "redirect_uri": google_redirect_uri(),
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
            "redirect_uri": redirect_uri("instagram"),
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
            "redirect_uri": redirect_uri("tiktok"),
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


def _google_profile_ok(profile: dict) -> tuple[bool, str]:
    email = (profile.get("email") or "").strip().lower()
    if not email:
        return False, "Google hat keine E-Mail-Adresse freigegeben. Bitte Konto-Berechtigungen prüfen."
    verified = profile.get("email_verified")
    if verified is False:
        return False, "Bitte nutze ein bei Google verifiziertes E-Mail-Konto."
    sub = profile.get("sub") or profile.get("id") or ""
    if not sub:
        return False, "Google-Profil unvollständig. Bitte erneut versuchen."
    return True, ""


def complete_oauth(provider: str, code: str) -> tuple[bool, str, dict | None]:
    provider = provider.lower()
    code = (code or "").strip()
    if not code:
        return False, "OAuth-Code fehlt.", None

    try:
        if provider == "google":
            token_data = _exchange_google(code)
            profile = _profile_google(token_data["access_token"])
            ok, err = _google_profile_ok(profile)
            if not ok:
                return False, err, None
            email = profile["email"].strip().lower()
            name = profile.get("name") or email.split("@")[0]
            sub = str(profile.get("sub") or "")

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
            return False, "Unbekannter OAuth-Anbieter.", None

        if not sub:
            return False, "OAuth-Profil unvollständig.", None

        return oauth_login_or_register(
            email=email,
            display_name=name,
            provider=provider,
            provider_sub=sub,
        )

    except requests.HTTPError as exc:
        try:
            from logger import log_oauth
            log_oauth("oauth_http_error", provider=provider, success=False)
        except Exception:
            pass
        detail = ""
        try:
            detail = exc.response.json()
        except Exception:
            detail = exc.response.text if exc.response is not None else str(exc)
        if provider == "google" and "redirect_uri" in str(detail).lower():
            return (
                False,
                "Redirect-URI stimmt nicht mit Google Console überein. "
                f"Erwartet: {google_redirect_uri()}",
                None,
            )
        return False, f"Anmeldung fehlgeschlagen ({provider}). Bitte erneut versuchen.", None

    except Exception as exc:
        try:
            from logger import log_oauth
            log_oauth("oauth_exception", provider=provider, success=False)
        except Exception:
            pass
        return False, "Anmeldung fehlgeschlagen. Bitte später erneut versuchen.", None


def friendly_oauth_error(error_code: str, description: str = "") -> str:
    code = (error_code or "").strip().lower()
    desc = (description or "").strip()
    messages = {
        "access_denied": "Google-Anmeldung abgebrochen.",
        "invalid_scope": "Die Google-Anmeldung ist derzeit nicht möglich. Bitte Support kontaktieren.",
        "server_error": "Google ist vorübergehend nicht erreichbar. Bitte später erneut versuchen.",
        "temporarily_unavailable": "Google ist vorübergehend nicht erreichbar. Bitte später erneut versuchen.",
    }
    msg = messages.get(code, "Die Anmeldung mit Google ist fehlgeschlagen. Bitte erneut versuchen.")
    if desc and code not in messages:
        return msg
    return msg
