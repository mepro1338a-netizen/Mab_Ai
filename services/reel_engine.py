"""
AI Reel Script Engine — OpenAI with graceful fallback when API unavailable.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL

REEL_MODES = ("hype", "emotional", "funny")
REEL_PLATFORMS = ("TikTok", "Instagram Reels", "YouTube Shorts")


@dataclass
class ReelScriptRequest:
    topic: str
    platform: str = "TikTok"
    match_context: str = ""
    mode: str = "hype"
    duration_sec: int = 30
    cta: str = "Folge für mehr Fußball-Content"
    language: str = "de"


@dataclass
class ReelScriptResult:
    ok: bool
    content: str
    source: str = "openai"  # openai | fallback
    error: str = ""
    sections: dict[str, str] = field(default_factory=dict)


def _mode_instruction(mode: str) -> str:
    m = (mode or "hype").lower()
    return {
        "hype": "Energiegeladen, schnelle Schnitte, FOMO, Stadion-Feeling, starke Superlative.",
        "emotional": "Storytelling, persönlich, Spannungsbogen, Gänsehaut-Momente, ruhigere Payoff.",
        "funny": "Witzig, relatable Memes, trockener Humor, überraschende Punchlines — ohne Beleidigungen.",
    }.get(m, "Viral, fußballaffin, hohe Retention in den ersten 2 Sekunden.")


def _system_prompt() -> str:
    return (
        "Du bist MaByte Reel Studio — viraler Shortform-Stratege für Fußball auf TikTok, "
        "Instagram Reels und YouTube Shorts. Antworte auf Deutsch, strukturiert, copy-paste ready."
    )


def _build_script_user_prompt(req: ReelScriptRequest) -> str:
    match_block = f"\nMatch / Story:\n{req.match_context}\n" if req.match_context.strip() else ""
    return f"""
Erstelle ein komplettes virales Fußball-Reel-Paket.

Thema: {req.topic}
Plattform: {req.platform}
Modus: {req.mode} — {_mode_instruction(req.mode)}
Ziel-Länge: {req.duration_sec} Sekunden
CTA: {req.cta}
{match_block}

Liefere exakt diese Abschnitte (Markdown-Überschriften):

# Viral Score
(1–10 + 1 Satz Begründung)

# Hook Strength
(1–10)

# Viral Hook
(1 Zeile, max 12 Wörter)

# Full Script
(Sprecher-Text mit Zeitstempeln 0s, 3s, 7s …)

# Scene Breakdown
(3–6 Szenen: Visual + Text-Overlay + Dauer)

# On Screen Text
(3 kurze Overlays)

# Caption
(1 Absatz, emoji sparsam)

# Hashtags
(12–18 relevante Tags)

# Thumbnail Text
(3–5 Wörter, groß lesbar)

# CTA
({req.cta} — optimiert)

# Match Storytelling
(kurzer narrativer Bogen, auch ohne echtes Match nutzbar)
"""


def _build_hook_prompt(req: ReelScriptRequest, count: int = 5) -> str:
    return f"""
Generiere {count} virale Hook-Varianten für ein Fußball-Reel.

Thema: {req.topic}
Plattform: {req.platform}
Modus: {req.mode} — {_mode_instruction(req.mode)}
{('Match: ' + req.match_context) if req.match_context else ''}

Format:
# Hooks
1. …
(jeweils Hook + 1 Satz warum es viral geht)
"""


def _build_caption_prompt(script_excerpt: str, platform: str) -> str:
    return f"""
Erstelle Auto-Captions (SRT-Stil) für ein 9:16 Fußball-Reel.

Plattform: {platform}
Skript-Auszug:
{script_excerpt[:2000]}

Liefere:
# SRT Captions
(zeitgestempelte Zeilen)

# Burn-in Style
(Schrift, Position, Highlight-Wörter)

# Keywords für Algorithmus
"""


def _build_voiceover_prompt(req: ReelScriptRequest, script: str) -> str:
    return f"""
Schreibe Voiceover für Fußball-Kommentator-Stil (deutsch).

Modus: {req.mode}
Thema: {req.topic}

Skript-Basis:
{script[:1500]}

Liefere:
# Voiceover Text
# Pace & Emphasis
# ElevenLabs Tags (optional)
# OpenAI TTS Hinweis (Stimme: energetic male)
"""


def _fallback_script(req: ReelScriptRequest) -> ReelScriptResult:
    hook = f"Wusstest du das zu {req.topic}?"
    body = (
        f"# Viral Score\n7/10 — starkes Fußball-Thema.\n\n"
        f"# Hook Strength\n8/10\n\n"
        f"# Viral Hook\n{hook}\n\n"
        f"# Full Script\n"
        f"0s — {hook}\n"
        f"3s — Hier kommt der Twist zu {req.topic}.\n"
        f"7s — Die Statistik, die niemand erwartet.\n"
        f"12s — Deshalb explodiert dieses Reel gerade.\n"
        f"18s — {req.cta}\n\n"
        f"# Scene Breakdown\n"
        f"1. Close-up Spieler · 2s\n2. Stat-Overlay · 3s\n3. Stadion B-Roll · 4s\n"
        f"4. Zoom Punch · 2s\n5. CTA Card · 3s\n\n"
        f"# On Screen Text\nPOV: Du kennst die Wahrheit\n"
        f"# Caption\n{req.topic} — kommentier deine Meinung.\n\n"
        f"# Hashtags\n#fußball #reels #tiktok #shorts #mabyte #bundesliga #ucl\n\n"
        f"# Thumbnail Text\n{req.topic[:24].upper()}\n\n"
        f"# CTA\n{req.cta}\n\n"
        f"# Match Storytelling\nVom Underdog-Moment zur viralen These in 20 Sekunden.\n"
    )
    return ReelScriptResult(ok=True, content=body, source="fallback")


def _call_openai(user_prompt: str, *, max_tokens: int = 2200) -> tuple[bool, str, str]:
    if not (OPENAI_API_KEY or "").strip():
        return False, "", "OPENAI_API_KEY nicht gesetzt"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,
            max_tokens=max_tokens,
        )
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            return False, "", "Leere Antwort vom Modell"
        return True, text, ""
    except Exception as exc:
        return False, "", str(exc)


class ReelEngine:
    """OpenAI-powered reel content generation with offline templates."""

    def generate_script(self, req: ReelScriptRequest) -> ReelScriptResult:
        ok, text, err = _call_openai(_build_script_user_prompt(req))
        if ok:
            return ReelScriptResult(ok=True, content=text, source="openai")
        fb = _fallback_script(req)
        fb.error = err
        return fb

    def generate_hooks(self, req: ReelScriptRequest, count: int = 5) -> ReelScriptResult:
        ok, text, err = _call_openai(_build_hook_prompt(req, count), max_tokens=1200)
        if ok:
            return ReelScriptResult(ok=True, content=text, source="openai")
        hooks = "\n".join(
            f"{i}. {req.topic} — Version {i} ({req.mode})"
            for i in range(1, count + 1)
        )
        return ReelScriptResult(
            ok=True,
            content=f"# Hooks\n{hooks}\n\n*(Offline — {err or 'API nicht verfügbar'})*",
            source="fallback",
            error=err,
        )

    def generate_captions(self, script_excerpt: str, platform: str) -> ReelScriptResult:
        ok, text, err = _call_openai(
            _build_caption_prompt(script_excerpt, platform),
            max_tokens=1500,
        )
        if ok:
            return ReelScriptResult(ok=True, content=text, source="openai")
        return ReelScriptResult(
            ok=True,
            content=(
                "# SRT Captions\n"
                "00:00:00,000 --> 00:00:02,500\nWusstest du das?\n\n"
                "00:00:02,500 --> 00:00:06,000\nHier kommt der Twist.\n\n"
                "# Burn-in Style\nWeiß, fett, unten Drittel\n"
            ),
            source="fallback",
            error=err,
        )

    def generate_voiceover_pack(self, req: ReelScriptRequest, script: str) -> ReelScriptResult:
        ok, text, err = _call_openai(_build_voiceover_prompt(req, script), max_tokens=1400)
        if ok:
            return ReelScriptResult(ok=True, content=text, source="openai")
        return ReelScriptResult(
            ok=True,
            content=(
                f"# Voiceover Text\n"
                f"Leute, {req.topic} — und das ändert alles. {req.cta}\n\n"
                f"# Pace & Emphasis\nSchnell starten, Pause vor CTA.\n\n"
                f"# Provider\nElevenLabs: kommentator_de · OpenAI TTS: onyx\n"
            ),
            source="fallback",
            error=err,
        )


def voice_catalog() -> list[dict[str, str]]:
    """Prepared voices — actual TTS wired later."""
    return [
        {"id": "fb_commentator_de", "label": "Fußball-Kommentator (DE)", "provider": "elevenlabs"},
        {"id": "hype_male", "label": "Hype Male", "provider": "elevenlabs"},
        {"id": "calm_female", "label": "Calm Female", "provider": "openai"},
        {"id": "onyx_tts", "label": "OpenAI Onyx", "provider": "openai"},
    ]


def export_script_json(result: ReelScriptResult) -> str:
    return json.dumps(
        {"ok": result.ok, "source": result.source, "content": result.content},
        ensure_ascii=False,
        indent=2,
    )
