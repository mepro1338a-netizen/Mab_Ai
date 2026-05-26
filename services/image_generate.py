"""
MaByte Image Studio — echte Bildgenerierung (OpenAI / Stability).
"""
from __future__ import annotations

import base64
from typing import Any

import requests

from config import (
    IMAGE_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_IMAGE_MODEL,
    STABILITY_API_KEY,
    STABILITY_IMAGE_MODEL,
)


def map_preset_to_api_size(preset: dict[str, str]) -> str:
    """API-Football presets -> OpenAI gpt-image size strings."""
    aspect = str(preset.get("aspect") or "1:1")
    if aspect == "9:16":
        return "1024x1536"
    if aspect == "16:9":
        return "1536x1024"
    if aspect == "4:5":
        return "1024x1536"
    return "1024x1024"


def map_quality(quality: str) -> str:
    return "high" if quality == "hd" else "medium"


def build_visual_prompt(
    user_prompt: str,
    *,
    style: str = "",
    use_case: str = "",
) -> str:
    """Kurzer EN-Prompt fuer das Bildmodell (kein Text-Paket)."""
    style_bit = f", {style} style" if style else ""
    case_bit = f", {use_case} composition" if use_case else ""
    return (
        f"{user_prompt.strip()}{style_bit}{case_bit}. "
        "High quality digital artwork, sharp focus, professional lighting. "
        "No watermark, no blurry artifacts."
    )[:3900]


def _generate_openai(prompt: str, *, size: str, quality: str) -> tuple[bytes | None, str | None]:
    if not (OPENAI_API_KEY or "").strip():
        return None, "OPENAI_API_KEY fehlt — Bildgenerierung nicht verfuegbar."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        result = client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=prompt[:4000],
            size=size,
            quality=quality,
            n=1,
        )
        if not result.data:
            return None, "Keine Bilddaten von OpenAI erhalten."

        item = result.data[0]
        if getattr(item, "b64_json", None):
            return base64.b64decode(item.b64_json), None

        url = getattr(item, "url", None)
        if url:
            resp = requests.get(url, timeout=120)
            if resp.status_code >= 400:
                return None, f"Bild-Download fehlgeschlagen (HTTP {resp.status_code})"
            return resp.content, None

        return None, "OpenAI lieferte weder Bild noch URL."
    except Exception as exc:
        return None, str(exc)[:500]


def _generate_stability(prompt: str) -> tuple[bytes | None, str | None]:
    if not (STABILITY_API_KEY or "").strip():
        return None, "STABILITY_API_KEY fehlt."

    url = f"https://api.stability.ai/v2beta/stable-image/generate/{STABILITY_IMAGE_MODEL}"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*",
    }
    data = {"prompt": prompt[:4000], "output_format": "png"}

    try:
        response = requests.post(
            url,
            headers=headers,
            files={"none": ""},
            data=data,
            timeout=120,
        )
        if response.status_code >= 400:
            return None, (response.text or f"Stability HTTP {response.status_code}")[:500]
        return response.content, None
    except Exception as exc:
        return None, str(exc)[:500]


def generate_image_bytes(
    prompt: str,
    *,
    size: str = "1024x1024",
    quality: str = "medium",
) -> tuple[bytes | None, str | None]:
    """
    Returns (png/jpeg bytes, error_message).
    """
    provider = (IMAGE_PROVIDER or "openai").strip().lower()
    if provider == "stability":
        return _generate_stability(prompt)
    return _generate_openai(prompt, size=size, quality=quality)


def generate_from_studio_options(
    user_prompt: str,
    *,
    preset: dict[str, Any],
    quality: str = "standard",
    style: str = "",
    use_case: str = "",
) -> tuple[bytes | None, str | None, str]:
    visual = build_visual_prompt(user_prompt, style=style, use_case=use_case)
    api_size = map_preset_to_api_size(preset)
    api_quality = map_quality(quality)
    data, err = generate_image_bytes(visual, size=api_size, quality=api_quality)
    return data, err, visual
