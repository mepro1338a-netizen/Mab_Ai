"""
Video Generation Engine — Studio (günstig) vs. KI-Video (Qualität, höhere Token-Kosten).
"""
from __future__ import annotations

import uuid
from pathlib import Path

from config import DATA_DIR, VIDEO_PROVIDER
from db.video_engine import (
    add_video_output,
    create_video_job,
    get_latest_output,
    get_video_job,
    update_video_job,
)
from pricing import GEN_AI, GEN_AI_HD, GEN_STUDIO, get_video_generation_cost
from services.access_control import plan_rank
from services.video_metadata import generate_post_metadata
from services.video_prompt import build_ai_video_prompt
from services.video_providers import (
    VideoGenRequest,
    ai_provider_available,
    get_ai_provider,
    get_studio_provider,
    provider_status,
)

VIDEO_EXPORT_DIR = DATA_DIR / "video_engine" / "exports"

PLATFORM_MAP = {
    "tiktok": "tiktok",
    "instagram_reels": "instagram_reels",
    "youtube_shorts": "youtube_shorts",
    "TikTok": "tiktok",
    "Instagram Reels": "instagram_reels",
    "YouTube Shorts": "youtube_shorts",
    "YouTube": "youtube_shorts",
    "Instagram": "instagram_reels",
}


def normalize_platform(platform: str) -> str:
    return PLATFORM_MAP.get(platform, platform.lower().replace(" ", "_"))


def max_duration_for_plan(plan: str, studio_type: str, *, mode: str = GEN_AI) -> int:
    rank = plan_rank(plan)
    if studio_type == "reel":
        if mode == GEN_STUDIO:
            return 5 if rank < 1 else 6
        if rank < 1:
            return 0
        return 7
    if mode == GEN_STUDIO:
        return 12 if rank < 1 else 20
    if rank < 1:
        return 0
    if rank < 2:
        return 30
    if rank < 3:
        return 60
    return 90


def can_generate_video(plan: str) -> bool:
    return plan_rank(plan) >= 1


def can_use_ai_video(plan: str) -> bool:
    return plan_rank(plan) >= 1


def can_use_automation(plan: str, automation_unlocked: bool) -> bool:
    return plan_rank(plan) >= 2 and automation_unlocked


def estimate_cost(
    studio_type: str,
    duration_sec: int,
    *,
    mode: str = GEN_AI,
    quality: str = "standard",
) -> int:
    return get_video_generation_cost(
        studio_type, duration_sec, mode=mode, quality=quality
    )


def user_export_dir(username: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (username or "anon"))
    path = VIDEO_EXPORT_DIR / safe
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_provider(mode: str) -> tuple[object | None, str | None]:
    if mode == GEN_STUDIO:
        return get_studio_provider(), None
    provider, err = get_ai_provider()
    if not provider:
        return None, err
    return provider, None


def run_video_job(
    username: str,
    *,
    studio_type: str,
    prompt: str,
    platform: str,
    duration_sec: int,
    plan: str,
    mode: str = GEN_AI,
    quality: str = "standard",
    auto_metadata: bool = True,
    existing_job_id: str | None = None,
) -> tuple[dict | None, str | None]:
    if mode != GEN_STUDIO and not can_use_ai_video(plan):
        return None, "KI-Video ab Pro-Plan. Studio-Export ist günstiger verfügbar."

    if mode != GEN_STUDIO and not ai_provider_available():
        return None, (
            "KI-Video temporär nicht verfügbar. Nutze MaByte Studio oder "
            "kontaktiere Support (API-Keys auf dem Server)."
        )

    duration_sec = min(
        int(duration_sec),
        max_duration_for_plan(plan, studio_type, mode=mode) or duration_sec,
    )
    if max_duration_for_plan(plan, studio_type, mode=mode) == 0:
        return None, "Upgrade auf Pro für KI-Videos."

    provider, perr = resolve_provider(mode)
    if not provider:
        return None, perr or "Kein Video-Provider."

    provider_key = getattr(provider, "name", VIDEO_PROVIDER)

    if existing_job_id:
        job_id = existing_job_id
        job = get_video_job(job_id)
        if not job or job.get("username") != username:
            return None, "Job nicht gefunden."
        update_video_job(job_id, status="rendering", provider=provider_key)
    else:
        charge_id = f"chg_{uuid.uuid4().hex}"
        job = create_video_job(
            username,
            studio_type=studio_type,
            prompt=prompt,
            platform=normalize_platform(platform),
            duration_sec=duration_sec,
            provider=provider_key,
            cost_tokens=0,
            charge_id=charge_id,
            auto_metadata=auto_metadata,
            status="draft",
        )
        job_id = job["id"]
        update_video_job(job_id, status="rendering")

    if auto_metadata:
        title, caption, hashtags, _ = generate_post_metadata(
            prompt, platform=platform, duration_sec=duration_sec
        )
        update_video_job(job_id, title=title, caption=caption, hashtags=hashtags)

    out_file = user_export_dir(username) / f"{job_id}.mp4"
    hd = mode == GEN_AI_HD or quality == "hd"
    if mode == GEN_STUDIO:
        en_prompt = prompt
    else:
        en_prompt = build_ai_video_prompt(
            prompt,
            platform=normalize_platform(platform),
            duration_sec=duration_sec,
            hd=hd,
        )

    result = provider.generate(
        VideoGenRequest(
            prompt=en_prompt,
            duration_sec=duration_sec,
            aspect="9:16",
            platform=normalize_platform(platform),
        ),
        out_path=str(out_file),
    )

    if not result.ok or not result.file_path:
        update_video_job(
            job_id,
            status="failed",
            error_message=result.error or result.message or "Generierung fehlgeschlagen",
            provider=result.provider or provider_key,
        )
        return get_job_bundle(job_id), result.error or "Generierung fehlgeschlagen"

    fpath = Path(result.file_path)
    size = fpath.stat().st_size if fpath.exists() else 0
    add_video_output(
        job_id,
        file_path=str(fpath),
        file_url=result.file_url or "",
        file_size=size,
    )
    final_status = "ready_to_publish" if studio_type == "reel" else "ready"
    update_video_job(
        job_id,
        status=final_status,
        provider=result.provider or provider_key,
        error_message="",
    )
    return get_job_bundle(job_id), None


def get_job_bundle(job_id: str) -> dict | None:
    job = get_video_job(job_id)
    if not job:
        return None
    job["output"] = get_latest_output(job_id)
    return job


def engine_status() -> dict:
    return {
        "providers": provider_status(),
        "ai_ready": ai_provider_available(),
        "active_provider": VIDEO_PROVIDER,
    }
