"""High-quality EN prompts for video models (Kling / Runway / Replicate)."""
from __future__ import annotations

PLATFORM_STYLE = {
    "tiktok": "TikTok native, punchy hook in first second, high energy, mobile-first",
    "instagram_reels": "Instagram Reels aesthetic, polished, vibrant, scroll-stopping",
    "youtube_shorts": "YouTube Shorts, clear subject, strong contrast, retention-focused",
}


def build_ai_video_prompt(
    user_prompt: str,
    *,
    platform: str = "tiktok",
    duration_sec: int = 5,
    hd: bool = False,
) -> str:
    style = PLATFORM_STYLE.get(platform, "short-form vertical social video")
    quality = (
        "4K detail, cinematic lighting, shallow depth of field, smooth motion, "
        "professional color grade, sharp focus, film grain subtle"
        if hd
        else "cinematic lighting, smooth camera motion, sharp focus, clean composition"
    )
    return (
        f"{user_prompt.strip()}. "
        f"Style: {style}. Duration feel: {duration_sec} seconds. "
        f"{quality}. Vertical 9:16. No text overlays, no logos, no watermarks."
    )[:950]
