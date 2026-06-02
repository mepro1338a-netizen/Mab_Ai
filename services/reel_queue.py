"""Reel queue + scheduler — enqueue jobs, process queue, due schedules."""
from __future__ import annotations

from datetime import datetime, timezone

from database import get_user, save_usage, update_tokens
from db.video_engine import list_scheduled_posts, update_scheduled_post
from db.app import create_reel_job, list_queued_reel_jobs, update_reel_job
from db.video_engine import get_video_job
from pricing import GEN_AI, get_reel_video_cost
from services.social_publish import SocialPublishService
from services.video_engine import run_video_job


def _refund_tokens(username: str, cost: int, prompt: str) -> None:
    if cost <= 0:
        return
    user = get_user(username)
    if not user:
        return
    update_tokens(username, int(user.get("tokens") or 0) + int(cost))
    save_usage(
        username=username,
        tool="reel_video",
        prompt=str(prompt)[:1000],
        tokens_used=0,
        cost_tokens=-int(cost),
        api_provider="refund",
        status="refunded",
    )


def enqueue_reel(
    username: str,
    *,
    prompt: str,
    platform: str,
    duration_sec: int,
    mode: str,
    cost_tokens: int,
    charge_id: str,
    auto_metadata: bool = True,
) -> dict:
    return create_reel_job(
        username,
        prompt=prompt,
        platform=platform,
        duration_sec=duration_sec,
        cost_tokens=cost_tokens,
        charge_id=charge_id,
        generation_mode=mode,
        auto_metadata=auto_metadata,
    )


def process_reel_queue(
    username: str,
    *,
    plan: str,
    max_jobs: int = 1,
) -> list[dict]:
    """Process up to max_jobs queued reels — returns processed job summaries."""
    processed: list[dict] = []
    queued = list_queued_reel_jobs(username, limit=max_jobs)
    for row in queued:
        job_id = row["id"]
        job = get_video_job(job_id)
        if not job or job.get("status") != "queued":
            continue
        mode = job.get("generation_mode") or GEN_AI
        try:
            bundle, err = run_video_job(
            username,
            studio_type="reel",
            prompt=job.get("prompt") or "",
            platform=job.get("platform") or "tiktok",
            duration_sec=int(job.get("duration_sec") or 5),
            plan=plan,
            mode=mode,
            quality="standard",
            auto_metadata=bool(job.get("auto_metadata")),
            existing_job_id=job_id,
            )
        except Exception as exc:
            err = "Rendering fehlgeschlagen. Bitte erneut versuchen."
            bundle = None
            update_reel_job(
                job_id,
                status="failed",
                error_message=str(exc)[:400],
            )
            processed.append({"id": job_id, "ok": False, "error": err})
            continue
        if err:
            retries = int(job.get("retry_count") or 0) + 1
            max_r = int(job.get("max_retries") or 2)
            if retries < max_r:
                update_reel_job(job_id, status="queued", retry_count=retries, error_message=err)
            else:
                update_reel_job(job_id, status="failed", retry_count=retries, error_message=err)
                _refund_tokens(
                    username,
                    int(job.get("cost_tokens") or 0),
                    job.get("prompt") or "",
                )
            processed.append({"id": job_id, "ok": False, "error": err})
        else:
            update_reel_job(job_id, status="ready_to_publish")
            processed.append({"id": job_id, "ok": True, "bundle": bundle})
    return processed


def reel_cost(duration_sec: int, mode: str) -> int:
    return get_reel_video_cost(duration_sec, mode=mode)


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
            try:
                ok, msg = svc.publish_job(job_id, dry_run=False, user_consent=True)
            except Exception:
                ok, msg = False, "Auto-Post fehlgeschlagen."
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
