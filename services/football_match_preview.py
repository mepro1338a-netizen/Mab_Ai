"""
AI Match Preview — narrative, tactics, probabilities (OpenAI + fallback).
"""
from __future__ import annotations

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL


def _fallback_preview(club: str, opponent: str, context: dict) -> str:
    return f"""
# AI Match Preview · {club} vs {opponent}

## Narrative Summary
{club} trifft auf {opponent} — ein Spiel mit hoher Aufmerksamkeit für Creator und Analysten.

## Injuries & Availability
*(API-Daten laden für Live-Liste — Pro Feature)*

## Form Analysis
{context.get('form_home', 'Heim in solider Form')} · {context.get('form_away', 'Auswärts unter Druck')}

## Momentum
{context.get('momentum', 'Ausgeglichen — beide Teams mit Offensivmomenten.')}

## Tactical Insight
Erwarte kompaktes Pressing von {club}, {opponent} nutzt Transitionen.

## Key Player Impact
Entscheidend: Formstärke der Offensivspieler und Set-Piece-Qualität.

## Over/Under Probability
O/U 2.5: **58% Over** (modellbasierte Schätzung, keine Garantie)

## BTTS Probability
Beide treffen: **62%** (edukative Schätzung)

## Creator Angle
Hook: „Warum dieses {club}-Spiel alles ändert“ — Reel vor Anpfiff posten.
"""


def _build_prompt(club: str, opponent: str, context: dict) -> str:
    return f"""
Erstelle eine professionelle AI Football Match Preview für Creator, Wett-Analysten und Fußballseiten.

Heim: {club}
Auswärts: {opponent}
Plattform-Fokus: {context.get('platform', 'Multi')}
Kontext API: {context.get('api_advice', '')}
Form Heim: {context.get('form_home', '')}
Form Auswärts: {context.get('form_away', '')}
Prognose Heim/Unentschieden/Auswärts: {context.get('home_pct', '')}% / {context.get('draw_pct', '')}% / {context.get('away_pct', '')}%

Liefere exakt diese Abschnitte (Markdown):

# AI Match Preview

## Narrative Summary
## Injuries
## Form Analysis
## Momentum
## Tactical Insight
## Key Player Impact
## Over/Under Probability
## BTTS Probability
## Creator Angle

Ton: professionell, datengetrieben, keine Wettempfehlung, keine Garantien.
"""


def generate_match_preview(
    club: str,
    opponent: str,
    *,
    context: dict | None = None,
) -> tuple[str, str]:
    """Returns (content, source)."""
    ctx = context or {}
    if not (OPENAI_API_KEY or "").strip():
        return _fallback_preview(club, opponent, ctx), "fallback"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist MaByte Football Intelligence — Elite-Analyst für "
                        "Creator und Daten-Fans. Deutsch, strukturiert."
                    ),
                },
                {"role": "user", "content": _build_prompt(club, opponent, ctx)},
            ],
            temperature=0.65,
            max_tokens=2800,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or _fallback_preview(club, opponent, ctx), "openai"
    except Exception:
        return _fallback_preview(club, opponent, ctx), "fallback"
