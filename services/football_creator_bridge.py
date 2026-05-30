"""Creator bridge — Reel template from match intelligence (no full render pipeline)."""
from __future__ import annotations

from typing import Any

from services.football_viral_studio import generate_viral_reel_package


def build_reel_template_from_intel(
    detail: dict[str, Any],
    intel: dict[str, Any] | None = None,
    *,
    platform: str = "TikTok",
) -> dict[str, str]:
    """Compact reel handoff for Creator Studio — works without video render."""
    card = detail.get("card") or {}
    home = str(card.get("home") or "Heim")
    away = str(card.get("away") or "Auswärts")
    league = str(card.get("league") or "Fußball")
    score = str(card.get("score") or "vs")
    rec = (intel or {}).get("recommendation") or {}
    pick = str(rec.get("main_pick") or "Matchday-Analyse")
    conf = rec.get("confidence")
    conf_txt = f"{float(conf):.0f}%" if conf is not None else "—"

    reasons = (intel or {}).get("reasons_short") or []
    ctx = f"{league} · {score} · Tipp: {pick} (Conf {conf_txt})"
    if reasons:
        ctx += " · " + " | ".join(reasons[:2])

    pkg, src = generate_viral_reel_package(
        home,
        away,
        platform=platform,
        tone="Premium Intelligence",
        match_context=ctx[:500],
    )

    plat_key = {
        "TikTok": "TikTok",
        "YouTube Shorts": "YouTube Shorts",
        "Instagram Reels": "Instagram Reel",
    }.get(platform, platform)

    return {
        "package": pkg,
        "source": src,
        "home": home,
        "away": away,
        "platform": plat_key,
        "hook": f"{home} vs {away} — {pick}",
        "status_note": (
            "Reel-Vorlage erstellt. Video-Rendering im Creator Studio."
            if src == "fallback"
            else "Reel-Vorlage bereit — Creator Studio öffnen zum Rendern."
        ),
    }
