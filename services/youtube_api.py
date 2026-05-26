"""
YouTube Data API — token refresh, channel status, Shorts upload.
Never log access/refresh tokens or client secrets.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from config import YOUTUBE_OAUTH_CLIENT_ID, YOUTUBE_OAUTH_CLIENT_SECRET
from db.video_engine import save_social_connection
from services.token_secure import decrypt_token, encrypt_token

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_API = "https://www.googleapis.com/youtube/v3"
YOUTUBE_UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"


def _expires_iso(expires_in: int | None) -> str:
    if not expires_in:
        return ""
    return datetime.fromtimestamp(
        time.time() + int(expires_in), tz=timezone.utc
    ).isoformat()


def _token_expired(expires_at: str, *, skew_sec: int = 120) -> bool:
    if not expires_at:
        return False
    try:
        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return exp <= datetime.now(timezone.utc) + timedelta(seconds=skew_sec)
    except Exception:
        return True


def parse_youtube_error(resp: requests.Response) -> str:
    """User-facing message — no token or secret content."""
    code = resp.status_code
    if code == 401:
        return "YouTube-Zugriff abgelaufen. Bitte unter „Accounts“ erneut verbinden."
    if code == 403:
        return (
            "Keine Upload-Berechtigung für diesen Kanal. "
            "Prüfe YouTube-Kanal und OAuth-Scopes (youtube.upload)."
        )
    if code == 404:
        return "YouTube-Ressource nicht gefunden."
    if code == 429:
        return "YouTube API-Limit erreicht. Bitte später erneut versuchen."
    if code >= 500:
        return "YouTube-Server vorübergehend nicht erreichbar. Bitte später erneut."
    try:
        data = resp.json()
        err = data.get("error", {})
        if isinstance(err, dict):
            msg = str(err.get("message") or "").strip()
            if msg and len(msg) < 200:
                return f"YouTube: {msg}"
    except Exception:
        pass
    return f"YouTube-Fehler (HTTP {code})."


def refresh_access_token(refresh_token: str) -> tuple[dict[str, Any] | None, str]:
    if not refresh_token:
        return None, "Refresh-Token fehlt. Bitte YouTube erneut verbinden."
    if not YOUTUBE_OAUTH_CLIENT_ID or not YOUTUBE_OAUTH_CLIENT_SECRET:
        return None, "YouTube OAuth ist auf dem Server nicht konfiguriert."

    try:
        resp = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": YOUTUBE_OAUTH_CLIENT_ID,
                "client_secret": YOUTUBE_OAUTH_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=25,
        )
        if not resp.ok:
            return None, parse_youtube_error(resp)
        data = resp.json()
        if not data.get("access_token"):
            return None, "YouTube hat keinen neuen Access-Token geliefert."
        return data, ""
    except requests.Timeout:
        return None, "Zeitüberschreitung bei der YouTube-Anmeldung."
    except requests.RequestException:
        return None, "Netzwerkfehler bei der YouTube-Anmeldung."


def persist_refreshed_tokens(
    username: str,
    platform: str,
    conn: dict[str, Any],
    token_data: dict[str, Any],
) -> None:
    access = token_data.get("access_token", "")
    enc_a = encrypt_token(access)
    if not enc_a:
        return
    refresh = decrypt_token(conn.get("refresh_token_enc") or "")
    new_refresh = token_data.get("refresh_token") or refresh
    save_social_connection(
        username,
        platform,
        access_token_enc=enc_a,
        refresh_token_enc=encrypt_token(new_refresh) if new_refresh else conn.get("refresh_token_enc", ""),
        token_expires_at=_expires_iso(token_data.get("expires_in")),
        scopes=conn.get("scopes") or "",
        account_label=conn.get("account_label") or "",
        channel_id=conn.get("channel_id") or "",
    )


def ensure_access_token(username: str, conn: dict[str, Any], platform: str) -> tuple[str | None, str]:
    access = decrypt_token(conn.get("access_token_enc") or "")
    expires_at = str(conn.get("token_expires_at") or "")

    if access and not _token_expired(expires_at):
        return access, ""

    refresh = decrypt_token(conn.get("refresh_token_enc") or "")
    if not refresh:
        return None, "YouTube-Token abgelaufen. Bitte erneut verbinden."

    data, err = refresh_access_token(refresh)
    if err or not data:
        return None, err or "Token-Refresh fehlgeschlagen."

    persist_refreshed_tokens(username, platform, conn, data)
    return str(data.get("access_token") or ""), ""


def fetch_channel_info(access_token: str) -> tuple[dict[str, Any] | None, str]:
    try:
        resp = requests.get(
            f"{YOUTUBE_API}/channels",
            params={"part": "snippet,statistics,status", "mine": "true"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=20,
        )
        if not resp.ok:
            return None, parse_youtube_error(resp)
        items = resp.json().get("items") or []
        if not items:
            return None, "Kein YouTube-Kanal mit diesem Account verknüpft."
        ch = items[0]
        snippet = ch.get("snippet") or {}
        stats = ch.get("statistics") or {}
        status = ch.get("status") or {}
        return {
            "id": ch.get("id", ""),
            "title": snippet.get("title", ""),
            "description": (snippet.get("description") or "")[:120],
            "thumbnail": (snippet.get("thumbnails") or {}).get("default", {}).get("url", ""),
            "subscriber_count": stats.get("subscriberCount", "—"),
            "video_count": stats.get("videoCount", "—"),
            "view_count": stats.get("viewCount", "—"),
            "privacy_status": status.get("privacyStatus", ""),
            "made_for_kids": status.get("madeForKids"),
        }, ""
    except requests.Timeout:
        return None, "Zeitüberschreitung beim Laden des Kanalstatus."
    except requests.RequestException:
        return None, "Netzwerkfehler beim Kanalstatus."


def upload_short_video(
    access_token: str,
    file_path: str,
    *,
    title: str,
    description: str,
    tags: list[str] | None = None,
) -> tuple[str | None, str]:
    path = Path(file_path)
    if not path.exists():
        return None, "Video-Datei wurde nicht gefunden."
    size = path.stat().st_size
    if size < 1024:
        return None, "Video-Datei ist zu klein oder beschädigt."
    if size > 256 * 1024 * 1024:
        return None, "Video ist zu groß (max. 256 MB für Shorts-Upload)."

    desc = (description or "").strip()
    if "#shorts" not in desc.lower() and "#shorts" not in (title or "").lower():
        desc = (desc + "\n\n#Shorts").strip()

    tag_list = list(tags or [])[:30]
    if "Shorts" not in tag_list:
        tag_list.insert(0, "Shorts")

    metadata = {
        "snippet": {
            "title": (title or "MaByte Short")[:100],
            "description": desc[:5000],
            "tags": tag_list,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    try:
        init = requests.post(
            f"{YOUTUBE_UPLOAD}?uploadType=resumable&part=snippet,status",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/mp4",
                "X-Upload-Content-Length": str(size),
            },
            json=metadata,
            timeout=45,
        )
        if not init.ok:
            return None, parse_youtube_error(init)

        upload_url = init.headers.get("Location")
        if not upload_url:
            return None, "YouTube hat keine Upload-Adresse zurückgegeben."

        with open(path, "rb") as fh:
            body = fh.read()

        put = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "video/mp4",
                "Content-Length": str(size),
            },
            data=body,
            timeout=600,
        )
        if put.status_code not in (200, 201):
            return None, parse_youtube_error(put)

        vid = (put.json() or {}).get("id") or ""
        if not vid:
            return None, "Upload abgeschlossen, aber keine Video-ID erhalten."
        return vid, ""
    except requests.Timeout:
        return None, "Upload-Zeitüberschreitung. Bitte erneut versuchen."
    except requests.RequestException:
        return None, "Netzwerkfehler beim Video-Upload."
    except OSError:
        return None, "Video-Datei konnte nicht gelesen werden."
