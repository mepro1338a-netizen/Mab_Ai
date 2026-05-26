"""
Social publishing — OAuth prep, queue, scheduled posts, platform uploads (stubs).
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import (
    DATA_DIR,
    META_APP_ID,
    TIKTOK_CLIENT_KEY,
    YOUTUBE_OAUTH_CLIENT_ID,
    normalize_app_base_url,
)
from db.video_engine import (
    get_social_connection,
    get_video_job,
    list_scheduled_posts,
    save_social_connection,
    update_scheduled_post,
    update_video_job,
)
from services.token_secure import decrypt_token, encrypt_token

PUBLISH_QUEUE_DIR = DATA_DIR / "reels" / "publish_queue"


PLATFORMS = (
    {
        "id": "youtube_shorts",
        "label": "YouTube Shorts",
        "oauth_env": "YOUTUBE_OAUTH_CLIENT_ID",
        "api_ready": False,
    },
    {
        "id": "instagram_reels",
        "label": "Instagram Reels",
        "oauth_env": "META_APP_ID",
        "api_ready": False,
    },
    {
        "id": "tiktok",
        "label": "TikTok",
        "oauth_env": "TIKTOK_CLIENT_KEY",
        "api_ready": False,
    },
)


@dataclass
class PublishDraft:
    id: str
    platform: str
    title: str
    caption: str
    hashtags: str
    video_path: str = ""
    job_id: str = ""
    scheduled_at: str = ""
    status: str = "draft"
    created_at: str = field(default_factory=lambda: _now_iso())
    error: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _queue_file(username: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (username or "anon"))
    PUBLISH_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    return PUBLISH_QUEUE_DIR / f"{safe}.json"


def load_queue(username: str) -> list[dict[str, Any]]:
    path = _queue_file(username)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_queue(username: str, items: list[dict[str, Any]]) -> None:
    path = _queue_file(username)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


class SocialPublishService:
    def __init__(self, username: str, base_url: str | None = None):
        self.username = username
        self.base_url = (base_url or normalize_app_base_url()).rstrip("/")

    def oauth_configured(self, platform_id: str) -> bool:
        env_map = {
            "youtube_shorts": YOUTUBE_OAUTH_CLIENT_ID,
            "instagram_reels": META_APP_ID,
            "tiktok": TIKTOK_CLIENT_KEY,
        }
        return bool((env_map.get(platform_id) or os.getenv(
            next((p["oauth_env"] for p in PLATFORMS if p["id"] == platform_id), ""), ""
        ) or "").strip())

    def is_connected(self, platform_id: str) -> bool:
        row = get_social_connection(self.username, platform_id)
        return bool(row and row.get("access_token_enc"))

    def connect_url(self, platform_id: str) -> str:
        return f"{self.base_url}/?page=video_oauth&platform={platform_id}"

    def list_platforms(self) -> list[dict[str, Any]]:
        out = []
        for p in PLATFORMS:
            api_env_ok = self.oauth_configured(p["id"])
            connected = self.is_connected(p["id"])
            out.append({
                **p,
                "api_configured": api_env_ok,
                "connected": connected,
                "connect_url": self.connect_url(p["id"]),
                "can_post": connected and p.get("api_ready"),
            })
        return out

    def connect_account(
        self,
        platform_id: str,
        *,
        access_token: str,
        refresh_token: str = "",
        expires_at: str = "",
        scopes: str = "",
        label: str = "",
    ) -> tuple[bool, str]:
        if not access_token:
            return False, "Kein Token."
        if not encrypt_token(access_token):
            return False, (
                "OAUTH_STATE_SECRET oder VIDEO_TOKEN_ENCRYPT_KEY fehlt — "
                "Tokens können nicht gespeichert werden."
            )
        save_social_connection(
            self.username,
            platform_id,
            access_token_enc=encrypt_token(access_token),
            refresh_token_enc=encrypt_token(refresh_token),
            token_expires_at=expires_at,
            scopes=scopes,
            account_label=label or platform_id,
        )
        return True, f"{platform_id} verbunden."

    def disconnect(self, platform_id: str) -> None:
        from db.video_engine import delete_social_connection

        delete_social_connection(self.username, platform_id)

    def add_draft(
        self,
        *,
        platform: str,
        title: str,
        caption: str,
        hashtags: str = "",
        video_path: str = "",
        job_id: str = "",
        scheduled_at: str = "",
    ) -> PublishDraft:
        draft = PublishDraft(
            id=uuid.uuid4().hex[:12],
            platform=platform,
            title=title,
            caption=caption,
            hashtags=hashtags,
            video_path=video_path,
            job_id=job_id,
            scheduled_at=scheduled_at,
            status="scheduled" if scheduled_at else "draft",
        )
        items = load_queue(self.username)
        items.insert(0, asdict(draft))
        save_queue(self.username, items[:50])
        return draft

    def queue_for_posting(self, draft_id: str) -> tuple[bool, str]:
        items = load_queue(self.username)
        for item in items:
            if item.get("id") == draft_id:
                item["status"] = "queued"
        save_queue(self.username, items)
        return True, "In Warteschlange"

    def publish_job(
        self,
        job_id: str,
        *,
        dry_run: bool = True,
        user_consent: bool = False,
    ) -> tuple[bool, str]:
        job = get_video_job(job_id)
        if not job:
            return False, "Job nicht gefunden."
        if job.get("username") != self.username:
            return False, "Kein Zugriff."
        if job.get("status") != "ready":
            return False, f"Job Status: {job.get('status')}"

        platform = job.get("platform") or "tiktok"
        plat = next((p for p in PLATFORMS if p["id"] == platform), None)
        label = plat["label"] if plat else platform

        if not user_consent:
            update_video_job(job_id, status="ready_to_publish")
            return True, f"Bereit zum manuellen Export für {label}."

        if not self.is_connected(platform):
            update_video_job(job_id, status="ready_to_publish")
            return True, f"OAuth nicht verbunden — Video bereit für {label} (manuell)."

        if dry_run or not plat or not plat.get("api_ready"):
            update_video_job(job_id, status="ready_to_publish")
            return True, f"[Vorbereitet] Upload für {label} — API-Freigabe ausstehend."

        ok, msg = self._provider_upload(platform, job)
        if ok:
            update_video_job(job_id, status="posted", error_message="")
            return True, msg
        update_video_job(job_id, status="failed", error_message=msg)
        return False, msg

    def _provider_upload(self, platform_id: str, job: dict) -> tuple[bool, str]:
        conn = get_social_connection(self.username, platform_id)
        if not conn:
            return False, "Nicht verbunden."
        token = decrypt_token(conn.get("access_token_enc") or "")
        if not token:
            return False, "Token nicht lesbar."
        if platform_id == "youtube_shorts":
            return self._upload_youtube_shorts(job, token)
        if platform_id == "instagram_reels":
            return self._upload_instagram_reels(job, token)
        if platform_id == "tiktok":
            return self._upload_tiktok(job, token)
        return False, "Unbekannte Plattform"

    def _upload_youtube_shorts(self, job: dict, token: str) -> tuple[bool, str]:
        return False, "YouTube Shorts Upload API — Integration vorbereitet, noch nicht live."

    def _upload_instagram_reels(self, job: dict, token: str) -> tuple[bool, str]:
        return False, "Instagram Reels Publish API — App Review erforderlich."

    def _upload_tiktok(self, job: dict, token: str) -> tuple[bool, str]:
        return False, "TikTok Content Posting API — Partner-Freigabe erforderlich."

    def simulate_post(self, draft_id: str, *, dry_run: bool = True) -> tuple[bool, str]:
        items = load_queue(self.username)
        for item in items:
            if item.get("id") == draft_id:
                plat = item.get("platform", "")
                if dry_run:
                    item["status"] = "ready_to_publish"
                    save_queue(self.username, items)
                    return True, "[Dry-Run] ready_to_publish"
                item["status"] = "posted"
                save_queue(self.username, items)
                return True, "Simuliert gepostet"
        return False, "Draft nicht gefunden"

    def list_drafts(self, *, status: str | None = None) -> list[dict[str, Any]]:
        items = load_queue(self.username)
        if status:
            return [i for i in items if i.get("status") == status]
        return items

    def list_db_queue(self) -> list[dict[str, Any]]:
        return list_scheduled_posts(self.username)

    def delete_draft(self, draft_id: str) -> bool:
        items = [i for i in load_queue(self.username) if i.get("id") != draft_id]
        save_queue(self.username, items)
        return True
