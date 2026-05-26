"""
Video Studio — OpenAI production package + optional Replicate clip.
"""
from __future__ import annotations

import os
from typing import Any

import requests

from config import (
    OPENAI_API_KEY,
    OPENAI_TEXT_MODEL,
    REPLICATE_API_TOKEN,
    REPLICATE_VIDEO_MODEL,
)

try:
    import replicate
except Exception:
    replicate = None


def api_status() -> dict[str, bool]:
    return {
        "openai": bool((OPENAI_API_KEY or "").strip()),
        "replicate": bool((REPLICATE_API_TOKEN or "").strip() and (REPLICATE_VIDEO_MODEL or "").strip()),
    }


def build_en_clip_prompt(user_prompt: str, *, style: str, platform: str) -> str:
    return (
        f"{user_prompt.strip()}. "
        f"Style: {style}. Platform: {platform}. "
        "Cinematic vertical video, smooth motion, professional lighting, no text overlay."
    )[:900]


def generate_production_package(
    user_prompt: str,
    *,
    seconds: int,
    platform: str,
    style: str,
) -> tuple[str | None, str | None]:
    if not (OPENAI_API_KEY or "").strip():
        return None, "OPENAI_API_KEY fehlt — bitte in Railway Variables setzen."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        system = (
            "Du bist MaByte Video Studio. Erstelle professionelle, umsetzbare "
            "Video-Produktionspakete auf Deutsch. Strukturiert, konkret, creator-ready."
        )
        user = f"""
Erstelle ein vollständiges VIDEO-PRODUKTIONSPAKET.

Konzept: {user_prompt}
Ziel-Länge: {seconds} Sekunden
Plattform: {platform}
Stil: {style}

Liefere exakt diese Abschnitte (Markdown):

## Storyboard
(Shot-für-Shot, Zeitcodes)

## Kamera & Bewegung
## Voiceover-Skript
## On-Screen Text / Captions
## Thumbnail-Konzept
## Export & Upload-Checkliste
## KI-Video-Prompt (EN)
(Ein optimierter Prompt für Kling/Runway/Replicate, copy-paste)

## Hashtags & Titelvorschläge
"""
        response = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.65,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return None, "Leere Antwort von OpenAI."
        return text, None
    except Exception as exc:
        return None, f"OpenAI Fehler: {exc}"


def _normalize_replicate_output(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)) and output:
        return _normalize_replicate_output(output[0])
    url = getattr(output, "url", None)
    if callable(url):
        try:
            return str(url())
        except Exception:
            pass
    return str(output)


def generate_replicate_clip(
    en_prompt: str,
    *,
    seconds: int = 5,
) -> tuple[str | None, str | None]:
    """Returns public URL or local path string on success."""
    if not replicate:
        return None, "Replicate-Paket nicht installiert."
    if not (REPLICATE_API_TOKEN or "").strip():
        return None, "REPLICATE_API_TOKEN fehlt in Railway Variables."
    if not (REPLICATE_VIDEO_MODEL or "").strip():
        return None, "REPLICATE_VIDEO_MODEL fehlt in Railway Variables."

    try:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        payload: dict[str, Any] = {"prompt": en_prompt[:900]}
        if "kling" in REPLICATE_VIDEO_MODEL.lower():
            payload.setdefault("duration", min(max(seconds, 5), 10))

        output = replicate.run(REPLICATE_VIDEO_MODEL, input=payload)
        url = _normalize_replicate_output(output)
        if not url:
            return None, "Replicate hat kein Video zurückgegeben."
        if url.startswith("http"):
            return url, None
        return url, None
    except Exception as exc:
        return None, f"Replicate Fehler: {exc}"


def download_video_url(url: str) -> tuple[bytes | None, str | None]:
    try:
        resp = requests.get(url, timeout=180)
        if resp.status_code >= 400:
            return None, f"Video-Download fehlgeschlagen (HTTP {resp.status_code})"
        return resp.content, None
    except Exception as exc:
        return None, f"Download Fehler: {exc}"
