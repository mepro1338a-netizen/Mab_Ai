"""Internal metadata generation (caption, title, hashtags) — not shown as main product."""
from __future__ import annotations

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL


def generate_post_metadata(
    prompt: str,
    *,
    platform: str,
    duration_sec: int,
) -> tuple[str, str, str, str | None]:
    """Returns title, caption, hashtags, error."""
    if not (OPENAI_API_KEY or "").strip():
        title = prompt.strip()[:60] or "MaByte"
        return title, prompt[:280], "#MaByte #MaByteAI #shorts #reels", None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        user = f"""
Plattform: {platform}
Länge: {duration_sec}s
Konzept: {prompt}

Erstelle kurz:
TITLE: (max 80 Zeichen)
CAPTION: (max 220 Zeichen, mit Emoji sparsam)
HASHTAGS: (8-12 Tags, mit #)
"""
        r = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Du bist Social Media Editor. Nur die drei Blöcke ausgeben."},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
        )
        text = (r.choices[0].message.content or "").strip()
        title, caption, tags = prompt[:60], prompt[:200], "#MaByte #MaByteAI"
        for line in text.splitlines():
            u = line.strip()
            if u.upper().startswith("TITLE:"):
                title = u.split(":", 1)[-1].strip()[:80]
            elif u.upper().startswith("CAPTION:"):
                caption = u.split(":", 1)[-1].strip()[:280]
            elif u.upper().startswith("HASHTAGS:"):
                tags = u.split(":", 1)[-1].strip()[:400]
        return title, caption, tags, None
    except Exception as exc:
        return prompt[:60], prompt[:200], "#mabyte", str(exc)
