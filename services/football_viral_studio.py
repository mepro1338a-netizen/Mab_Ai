"""
Viral Football Reel Generator — hooks, captions, voiceover, export package.
"""
from __future__ import annotations

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL


def _fallback_package(club: str, opponent: str, tone: str) -> str:
    return f"""
# Viral Reel Package · {club} vs {opponent}

## Viral Hooks
1. {club} spielt heute um ALLES gegen {opponent}
2. Niemand redet über DIESE Statistik…
3. POV: Du hast das Ergebnis schon gesehen

## TikTok Caption
{club} vs {opponent} — kommentier deine Prognose. {tone} Energy.

## YouTube Shorts Title
{club} vs {opponent}: Die Wahrheit vor Anpfiff

## Instagram Reel Caption
Matchday. {club}. {opponent}. Speichern & teilen.

## Hashtags
#{club.replace(' ', '')} #{opponent.replace(' ', '')} #football #reels #matchday #bundesliga #ucl

## Voiceover Script
„{club} trifft auf {opponent} — und hier ist, warum dieses Spiel viral geht…“

## Thumbnail Text
{club.upper()} VS {opponent.upper()}

## Export Workflow
1. Hook in Reel Studio · 2. Voice generieren · 3. 9:16 Export · 4. Publish Center
"""


def generate_viral_reel_package(
    club: str,
    opponent: str,
    *,
    platform: str = "TikTok",
    tone: str = "Viral",
    match_context: str = "",
) -> tuple[str, str]:
    if not (OPENAI_API_KEY or "").strip():
        return _fallback_package(club, opponent, tone), "fallback"

    prompt = f"""
Erstelle ein virales Fußball-Reel-Paket für Creator.

Match: {club} vs {opponent}
Plattform: {platform}
Ton: {tone}
Kontext: {match_context}

Abschnitte:
# Viral Reel Package
## Viral Hooks (5)
## TikTok Caption
## YouTube Shorts Title
## Instagram Reel Caption
## Hashtags (15+)
## Voiceover Script (Fußball-Kommentator, DE)
## Thumbnail Text
## Export Workflow (Schritte Reel Studio)
"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Elite Football Social Growth Strategist. Deutsch, viral, ethisch.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=2400,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or _fallback_package(club, opponent, tone), "openai"
    except Exception:
        return _fallback_package(club, opponent, tone), "fallback"
