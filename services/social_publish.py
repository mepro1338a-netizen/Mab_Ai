"""
Social publishing — queue, OAuth-gated auto-post, YouTube Shorts upload.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
from services.social_oauth import decrypt_token, encrypt_token
from services.youtube_api import (
    ensure_access_token,
    fetch_channel_info,
    upload_short_video,
)


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
            has_refresh = bool(row and row.get("refresh_token_enc"))
            out.append({
                "id": pid,
                "label": meta.get("label", pid),
                "status": status,
                "account_label": (row or {}).get("account_label", ""),
                "channel_id": (row or {}).get("channel_id", ""),
                "token_expires_at": (row or {}).get("token_expires_at", ""),
                "has_refresh_token": has_refresh,
                "api_ready": meta.get("api_ready", False),
                "connected": status == "connected",
            })
        return out

    def youtube_channel_status(
        self, platform_id: str = "youtube_shorts"
    ) -> tuple[dict[str, Any] | None, str]:
        """Live channel stats — only when connected."""
        conn = get_social_connection(self.username, platform_id)
        if not conn or not conn.get("access_token_enc"):
            return None, "YouTube ist nicht verbunden."
        token, err = ensure_access_token(self.username, conn, platform_id)
        if err or not token:
            return None, err or "YouTube-Token ungültig."
        info, err = fetch_channel_info(token)
        if err or not info:
            return None, err or "Kanalstatus konnte nicht geladen werden."
        if info.get("id"):
            try:
                save_social_connection(
                    self.username,
                    platform_id,
                    access_token_enc=conn.get("access_token_enc", ""),
                    refresh_token_enc=conn.get("refresh_token_enc", ""),
                    token_expires_at=conn.get("token_expires_at", ""),
                    scopes=conn.get("scopes", ""),
                    account_label=info.get("title") or conn.get("account_label", ""),
                    channel_id=info.get("id", ""),
                )
            except Exception:
                pass
        return info, ""

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
        channel_id: str = "",
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
            channel_id=channel_id,
        )
        return True, "Verbunden."

    def disconnect(self, platform_id: str) -> None:
        delete_social_connection(self.username, platform_id)

    def list_queue_jobs(self) -> list[dict[str, Any]]:
        return list_video_jobs(self.username, studio_type="reel", limit=30)

    def list_publishable_jobs(self) -> list[dict[str, Any]]:
        jobs = self.list_queue_jobs()
        return [
            j for j in jobs
            if j.get("status") in ("ready", "ready_to_publish")
        ]

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
            return False, (
                f"Dieses Reel ist noch nicht bereit (Status: {job.get('status')}). "
                "Warte auf Rendering oder Queue-Abarbeitung."
            )

        platform = job.get("platform") or "tiktok"
        meta = SOCIAL_PLATFORMS.get(platform) or {}
        label = meta.get("label", platform)

        if not user_consent:
            return False, "Bitte bestätige die Veröffentlichung (Zustimmung erforderlich)."

        if not self.is_connected(platform):
            return False, (
                f"{label} ist nicht verbunden. "
                "Verbinde deinen Account unter „Accounts“."
            )

        if dry_run or not meta.get("api_ready"):
            update_video_job(job_id, status="ready_to_publish")
            return True, f"{label}: Upload vorbereitet (API-Freigabe ausstehend)."

        ok, msg = self._upload(platform, job)
        if ok:
            update_video_job(job_id, status="posted", error_message="")
            return True, msg
        update_video_job(job_id, status="failed", error_message=msg[:500])
        return False, msg

    def _upload(self, platform_id: str, job: dict) -> tuple[bool, str]:
        conn = get_social_connection(self.username, platform_id)
        if not conn:
            return False, "Account nicht verbunden."
        if platform_id == "youtube_shorts":
            return self._youtube_upload(job, conn, platform_id)
        if platform_id == "instagram_reels":
            return False, "Instagram Reels: Publishing nach Meta App Review."
        if platform_id == "tiktok":
            return False, "TikTok: Publishing nach Partner-API-Freigabe."
        return False, "Unbekannte Plattform."

    def _youtube_upload(
        self,
        job: dict,
        conn: dict[str, Any],
        platform_id: str,
    ) -> tuple[bool, str]:
        out = get_latest_output(job["id"])
        path = (out or {}).get("file_path") or ""
        if not path or not Path(path).exists():
            return False, "Video-Datei fehlt. Bitte Reel erneut rendern."

        token, err = ensure_access_token(self.username, conn, platform_id)
        if err or not token:
            return False, err or "YouTube-Anmeldung ungültig."

        title = (job.get("title") or "MaByte Short").strip()
        caption = (job.get("caption") or "").strip()
        tags_raw = (job.get("hashtags") or "").strip()
        tags = [t.strip().lstrip("#") for t in tags_raw.replace(",", " ").split() if t.strip()]

        desc = caption
        if tags_raw:
            desc = f"{caption}\n\n{tags_raw}".strip()

        video_id, err = upload_short_video(
            token,
            path,
            title=title,
            description=desc,
            tags=tags,
        )
        if err or not video_id:
            return False, err or "YouTube-Upload fehlgeschlagen."

        update_video_job(job["id"], posted_video_id=video_id)
        return True, (
            f"Short veröffentlicht: https://www.youtube.com/shorts/{video_id}"
        )

    def list_scheduled(self) -> list[dict]:
        return list_scheduled_posts(self.username)
