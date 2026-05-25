"""
Social publishing layer — OAuth prep, queue, drafts, scheduled posts (API stubs).
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DATA_DIR, normalize_app_base_url


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
    scheduled_at: str = ""
    status: str = "draft"  # draft | queued | scheduled | posted | failed
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
        import os

        for p in PLATFORMS:
            if p["id"] == platform_id:
                return bool(os.getenv(p["oauth_env"], "").strip())
        return False

    def connect_url(self, platform_id: str) -> str:
        """Placeholder OAuth start — replace with real provider URLs."""
        return f"{self.base_url}/?page=reels&oauth={platform_id}&state=pending"

    def list_platforms(self) -> list[dict[str, Any]]:
        out = []
        for p in PLATFORMS:
            out.append({
                **p,
                "connected": self.oauth_configured(p["id"]),
                "connect_url": self.connect_url(p["id"]),
            })
        return out

    def add_draft(
        self,
        *,
        platform: str,
        title: str,
        caption: str,
        hashtags: str = "",
        video_path: str = "",
        scheduled_at: str = "",
    ) -> PublishDraft:
        draft = PublishDraft(
            id=uuid.uuid4().hex[:12],
            platform=platform,
            title=title,
            caption=caption,
            hashtags=hashtags,
            video_path=video_path,
            scheduled_at=scheduled_at,
            status="scheduled" if scheduled_at else "draft",
        )
        items = load_queue(self.username)
        items.insert(0, asdict(draft))
        save_queue(self.username, items[:50])
        return draft

    def queue_for_posting(self, draft_id: str) -> tuple[bool, str]:
        items = load_queue(self.username)
        found = False
        for item in items:
            if item.get("id") == draft_id:
                item["status"] = "queued"
                found = True
        if not found:
            return False, "Draft nicht gefunden"
        save_queue(self.username, items)
        return True, "In Warteschlange (API-Anbindung folgt)"

    def simulate_post(self, draft_id: str, *, dry_run: bool = True) -> tuple[bool, str]:
        """Dry-run post — no external API call when dry_run=True."""
        items = load_queue(self.username)
        for item in items:
            if item.get("id") == draft_id:
                plat = item.get("platform", "")
                plat_meta = next((p for p in PLATFORMS if p["id"] == plat), None)
                label = plat_meta["label"] if plat_meta else plat
                if dry_run:
                    item["status"] = "posted"
                    item["error"] = ""
                    save_queue(self.username, items)
                    return True, f"[Dry-Run] Bereit für {label} — OAuth/API folgt"
                if plat_meta and not plat_meta.get("api_ready"):
                    item["status"] = "failed"
                    item["error"] = f"{label}: API noch nicht verbunden"
                    save_queue(self.username, items)
                    return False, item["error"]
                item["status"] = "posted"
                item["error"] = ""
                save_queue(self.username, items)
                return True, f"Gepostet auf {label}"
        return False, "Draft nicht gefunden"

    def list_drafts(self, *, status: str | None = None) -> list[dict[str, Any]]:
        items = load_queue(self.username)
        if status:
            return [i for i in items if i.get("status") == status]
        return items

    def delete_draft(self, draft_id: str) -> bool:
        items = [i for i in load_queue(self.username) if i.get("id") != draft_id]
        save_queue(self.username, items)
        return True
