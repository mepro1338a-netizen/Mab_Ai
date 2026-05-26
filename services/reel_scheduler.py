"""
Scheduler — due scheduled_posts → reel jobs; auto-post with consent + OAuth.
"""
from __future__ import annotations

from datetime import datetime, timezone

from db.video_engine import list_scheduled_posts, update_scheduled_post
from services.reel_queue import enqueue_reel
from services.social_publish import SocialPublishService


def _parse_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def process_due_schedules(username: str, *, plan: str, limit: int = 3) -> list[str]:
    """Create reel jobs for due schedules; attempt auto-post when allowed."""
    logs: list[str] = []
    now = datetime.now(timezone.utc)
    svc = SocialPublishService(username)

    for post in list_scheduled_posts(username):
        if post.get("status") not in ("planned", "scheduled", "queued"):
            continue
        due = _parse_iso(str(post.get("scheduled_at") or ""))
        if due and due > now:
            continue

        post_id = post["id"]
        update_scheduled_post(post_id, status="creating")

        prompt = post.get("prompt_template") or "MaByte Reel"
        platform = post.get("platform") or "tiktok"
        job_id = post.get("job_id") or ""

        if not job_id:
            from pricing import GEN_AI, get_reel_video_cost

            cost = get_reel_video_cost(5, mode=GEN_AI)
            job = enqueue_reel(
                username,
                prompt=prompt,
                platform=platform,
                duration_sec=5,
                mode=GEN_AI,
                cost_tokens=0,
                charge_id=f"sched_{post_id}",
            )
            job_id = job["id"]
            update_scheduled_post(post_id, job_id=job_id, status="queued")

        auto_post = int(post.get("auto_post") or 0) == 1
        consent = int(post.get("user_consent") or 0) == 1

        if auto_post and consent and svc.is_connected(platform):
            ok, msg = svc.publish_job(job_id, dry_run=False, user_consent=True)
            update_scheduled_post(
                post_id,
                status="posted" if ok else "failed",
                error_message="" if ok else msg,
            )
            logs.append(f"{post_id}: {msg}")
        else:
            update_scheduled_post(post_id, status="scheduled")
            logs.append(f"{post_id}: wartet auf Rendering/Post")

    return logs
