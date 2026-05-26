"""Reel jobs — queue layer on video_jobs (studio_type=reel)."""
from __future__ import annotations

from typing import Any

from db.video_engine import (
    create_video_job,
    get_latest_output,
    get_video_job,
    list_video_jobs,
    update_video_job,
)

REEL_STATUSES = (
    "draft",
    "queued",
    "rendering",
    "ready",
    "ready_to_publish",
    "scheduled",
    "posted",
    "failed",
)


def create_reel_job(
    username: str,
    *,
    prompt: str,
    platform: str,
    duration_sec: int,
    provider: str = "",
    cost_tokens: int = 0,
    charge_id: str | None = None,
    generation_mode: str = "ai",
    auto_metadata: bool = True,
    user_consent: int = 0,
    auto_post: int = 0,
    scheduled_at: str = "",
) -> dict[str, Any]:
    job = create_video_job(
        username,
        studio_type="reel",
        prompt=prompt,
        platform=platform,
        duration_sec=duration_sec,
        provider=provider,
        cost_tokens=cost_tokens,
        charge_id=charge_id,
        auto_metadata=auto_metadata,
        status="queued",
    )
    fields: dict[str, Any] = {"generation_mode": generation_mode}
    if user_consent:
        fields["user_consent"] = 1
    if auto_post:
        fields["auto_post"] = 1
    if scheduled_at:
        fields["scheduled_at"] = scheduled_at
    update_video_job(job["id"], **fields)
    return get_video_job(job["id"]) or job


def get_reel_job(job_id: str) -> dict[str, Any] | None:
    job = get_video_job(job_id)
    if job and job.get("studio_type") == "reel":
        job["output"] = get_latest_output(job_id)
        return job
    return None


def list_reel_jobs(username: str, *, status: str | None = None, limit: int = 50) -> list[dict]:
    jobs = list_video_jobs(username, studio_type="reel", limit=limit)
    if status:
        jobs = [j for j in jobs if j.get("status") == status]
    return jobs


def list_queued_reel_jobs(username: str, limit: int = 10) -> list[dict]:
    return list_reel_jobs(username, status="queued", limit=limit)


def update_reel_job(job_id: str, **fields: Any) -> None:
    update_video_job(job_id, **fields)
