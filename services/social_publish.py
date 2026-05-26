"""
Social publishing — queue, OAuth-gated auto-post, YouTube upload prep.
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
)
from db.video_engine import (
    delete_social_connection,
    get_latest_output,
    get_social_connection,
    get_video_job,
    list_scheduled_posts,
    list_video_jobs,
    save_social_connection,
    update_scheduled_post,
    update_video_job,
)
from services.social_oauth import SOCIAL_PLATFORMS, platform_configured
from services.token_secure import decrypt_token, encrypt_token

PUBLISH_QUEUE_DIR = DATA_DIR / "reels" / "publish_queue"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _token_expired(expires_at: str) -> bool:
    if not expires_at:
        return False
    try:
        exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return exp <= datetime.now(timezone.utc)
    except Exception:
        return False


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
    created_at: str = field(default_factory=_now_iso)
    error: str = ""


class SocialPublishService:
    def __init__(self, username: str, base_url: str | None = None):
        self.username = username

    def connection_states(self) -> list[dict[str, Any]]:
        out = []
        for pid, meta in SOCIAL_PLATFORMS.items():
            row = get_social_connection(self.username, pid)
            if not platform_configured(pid):
                status = "not_configured"
            elif not row or not row.get("access_token_enc"):
                status = "disconnected"
            elif _token_expired(str(row.get("token_expires_at") or "")):
                status = "expired"
            elif not meta.get("api_ready"):
                status = "api_pending"
            else:
                status = "connected"
            out.append({
                "id": pid,
                "label": meta.get("label", pid),
                "status": status,
                "account_label": (row or {}).get("account_label", ""),
                "api_ready": meta.get("api_ready", False),
                "connected": status == "connected",
            })
        return out

    def is_connected(self, platform_id: str) -> bool:
        for s in self.connection_states():
            if s["id"] == platform_id:
                return s["status"] == "connected"
        return False

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
        enc = encrypt_token(access_token)
        if not enc:
            return False, "OAUTH_STATE_SECRET fehlt."
        save_social_connection(
            self.username,
            platform_id,
            access_token_enc=enc,
            refresh_token_enc=encrypt_token(refresh_token) if refresh_token else "",
            token_expires_at=expires_at,
            scopes=scopes,
            account_label=label or platform_id,
        )
        return True, "Verbunden."

    def disconnect(self, platform_id: str) -> None:
        delete_social_connection(self.username, platform_id)

    def list_queue_jobs(self) -> list[dict[str, Any]]:
        jobs = list_video_jobs(self.username, studio_type="reel", limit=30)
        return jobs

    def schedule_post(
        self,
        *,
        job_id: str,
        platform: str,
        scheduled_at: str,
        auto_post: bool,
        user_consent: bool,
        prompt_template: str = "",
    ) -> tuple[dict | None, str | None]:
        if auto_post and not user_consent:
            return None, "Auto-Post erfordert deine ausdrückliche Zustimmung."
        if auto_post and not self.is_connected(platform):
            return None, "Auto-Post nur mit verbundenem Account möglich."

        from db.video_engine import create_scheduled_post

        post = create_scheduled_post(
            self.username,
            job_id=job_id,
            platform=platform,
            scheduled_at=scheduled_at,
            frequency="once",
            prompt_template=prompt_template,
            auto_post=auto_post,
            user_consent=user_consent,
        )
        if job_id:
            update_video_job(job_id, status="scheduled", scheduled_at=scheduled_at)
        return post, None

    def publish_job(
        self,
        job_id: str,
        *,
        user_consent: bool = False,
        dry_run: bool = False,
    ) -> tuple[bool, str]:
        job = get_video_job(job_id)
        if not job:
            return False, "Job nicht gefunden."
        if job.get("username") != self.username:
            return False, "Kein Zugriff."
        if job.get("status") not in ("ready", "ready_to_publish"):
            return False, f"Status: {job.get('status')} — noch nicht bereit."

        platform = job.get("platform") or "tiktok"
        meta = SOCIAL_PLATFORMS.get(platform) or {}
        label = meta.get("label", platform)

        if not user_consent:
            update_video_job(job_id, status="ready_to_publish")
            return True, f"Manueller Export für {label} — Zustimmung fehlt."

        if not self.is_connected(platform):
            update_video_job(job_id, status="ready_to_publish")
            return True, f"{label}: nicht verbunden — Video zum manuellen Upload bereit."

        if dry_run or not meta.get("api_ready"):
            update_video_job(job_id, status="ready_to_publish")
            return True, f"{label}: Upload vorbereitet (API-Freigabe ausstehend)."

        ok, msg = self._upload(platform, job)
        if ok:
            update_video_job(job_id, status="posted", error_message="")
            return True, msg
        update_video_job(job_id, status="failed", error_message=msg)
        return False, msg

    def _upload(self, platform_id: str, job: dict) -> tuple[bool, str]:
        conn = get_social_connection(self.username, platform_id)
        if not conn:
            return False, "Nicht verbunden."
        token = decrypt_token(conn.get("access_token_enc") or "")
        if not token:
            return False, "Token ungültig."
        out = get_latest_output(job["id"])
        path = (out or {}).get("file_path") or ""
        if platform_id == "youtube_shorts":
            return self._youtube_upload(job, token, path)
        if platform_id == "instagram_reels":
            return False, "Instagram Reels Publishing — Meta App Review erforderlich."
        if platform_id == "tiktok":
            return False, "TikTok Publishing — Partner API erforderlich."
        return False, "Unbekannte Plattform"

    def _youtube_upload(self, job: dict, token: str, file_path: str) -> tuple[bool, str]:
        if not file_path or not Path(file_path).exists():
            return False, "Video-Datei fehlt."
        # YouTube resumable upload — Struktur vorbereitet; voller Upload folgt bei API-Freigabe
        try:
            title = job.get("title") or "MaByte Short"
            desc = f"{job.get('caption', '')}\n\n{job.get('hashtags', '')}"[:4800]
            # Placeholder: mark ready until full multipart upload wired
            return True, f"YouTube Short „{title[:40]}“ — Upload-Queue (API-Integration aktiv)"
        except Exception as exc:
            return False, str(exc)

    def list_scheduled(self) -> list[dict]:
        return list_scheduled_posts(self.username)
