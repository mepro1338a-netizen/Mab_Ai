"""
Token pricing — Studio (günstig, wenig API-Kosten) vs. KI-Video (teurer, deckt Replicate/FAL + Marge).
1€ ≈ 100 Tokens (siehe config.TOKEN_ECONOMY).
"""
from __future__ import annotations

REEL_SCRIPT_COST = 90
AUTOMATION_UNLOCK_COST = 1000

BASE_IMAGE_COST = 35
BASE_MUSIC_COST = 120
BASE_CODING_COST = 20

# Legacy alias
REEL_VIDEO_COST = 100

# Modi
GEN_STUDIO = "studio"
GEN_AI = "ai"
GEN_AI_HD = "ai_hd"


def _tc(key: str, default: int) -> int:
    try:
        from config import TOKEN_COSTS

        return int(TOKEN_COSTS.get(key, default))
    except Exception:
        return default


def get_reel_script_cost() -> int:
    return REEL_SCRIPT_COST


def get_reel_video_cost(seconds: int = 7, *, mode: str = GEN_AI) -> int:
    """Reel: Studio günstig · KI 90–110+ Tokens."""
    sec = int(seconds)
    if mode == GEN_STUDIO:
        base = _tc("reel_studio_base", 22)
        return base + max(0, sec - 3) * _tc("reel_studio_per_sec", 3)
    if mode == GEN_AI_HD:
        base = _tc("reel_ai_hd_7s", 130) if sec >= 7 else _tc("reel_ai_5s", 95)
        return base
    # GEN_AI
    if sec >= 7:
        return _tc("reel_ai_7s", 110)
    return _tc("reel_ai_5s", 90)


def get_video_studio_cost(
    seconds: int = 15,
    *,
    quality: str = "standard",
    include_clip: bool = False,
    mode: str = GEN_AI,
) -> int:
    sec = int(seconds)
    if mode == GEN_STUDIO:
        cost = _tc("video_studio_base", 28) + max(0, sec - 5) * _tc("video_studio_per_sec", 2)
    elif mode == GEN_AI_HD:
        cost = _tc("video_ai_base", 130) + max(0, sec - 5) * _tc("video_ai_per_sec", 22)
        cost = int(cost * float(_tc("video_ai_hd_multiplier", 145)) / 100)
    else:
        cost = _tc("video_ai_base", 120) + max(0, sec - 5) * _tc("video_ai_per_sec", 18)
        if quality == "hd":
            cost = int(cost * float(_tc("video_quality_high", 135)) / 100)

    if include_clip:
        cost += _tc("video_ai_clip_addon", 0)
    return max(int(cost), 20)


def get_video_generation_cost(
    studio_type: str,
    duration_sec: int,
    *,
    mode: str = GEN_AI,
    quality: str = "standard",
) -> int:
    if studio_type == "reel":
        return get_reel_video_cost(duration_sec, mode=mode)
    return get_video_studio_cost(duration_sec, quality=quality, mode=mode)


def cost_label(mode: str) -> str:
    labels = {
        GEN_STUDIO: "MaByte Studio (günstig)",
        GEN_AI: "KI-Video (empfohlen)",
        GEN_AI_HD: "KI-Video HD (Premium)",
    }
    return labels.get(mode, mode)


def get_automation_unlock_cost() -> int:
    return AUTOMATION_UNLOCK_COST


def get_image_cost(quality: str = "standard", size: str = "1024") -> int:
    cost = BASE_IMAGE_COST
    if quality == "hd":
        cost += 30
    size_key = str(size).strip()
    addons = {"512": -5, "1024": 0, "1536": 20, "2048": 40}
    cost += addons.get(size_key, 0)
    return max(cost, 25)


def get_music_cost(length: str = "short") -> int:
    cost = BASE_MUSIC_COST
    if length == "medium":
        cost += 80
    if length == "long":
        cost += 150
    return cost


def get_coding_cost(complexity: str = "normal") -> int:
    cost = BASE_CODING_COST
    if complexity == "advanced":
        cost += 35
    if complexity == "fullstack":
        cost += 90
    return cost
