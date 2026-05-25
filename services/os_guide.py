"""Rule-based MaByte OS guide — safe navigation, no privileged actions."""
from __future__ import annotations

import html
import re
from typing import Any

# Pages the guide can navigate to (must match ui.py router keys)
NAV_PAGES: dict[str, dict[str, str]] = {
    "home": {"label": "Mission Control", "hint": "Startseite und Workspace-Übersicht."},
    "chat": {"label": "AI Assistant", "hint": "Chat mit Mab AI — Tokens werden verbraucht."},
    "projects": {"label": "Projects", "hint": "Projekte und gespeicherte Outputs."},
    "football": {"label": "Football AI", "hint": "Match Center, AI Engine, Odds Lab (Elite)."},
    "premium": {"label": "Premium", "hint": "Pläne upgraden — Stripe Checkout."},
    "dashboard": {"label": "Dashboard", "hint": "Account, Tokens, Limits."},
    "support": {"label": "Support", "hint": "Tickets für Bugs, Zahlung, Football."},
    "redeem": {"label": "Redeem", "hint": "Codes für Tokens oder Plan-Upgrades."},
    "image": {"label": "Image Studio", "hint": "Bildgenerierung — Token-Kosten beachten."},
    "video": {"label": "Video Studio", "hint": "Video-Workspace (nicht Reels)."},
    "reels": {"label": "Reels Studio", "hint": "Kurzformat-Reels — eigener Workspace."},
    "music": {"label": "Music Studio", "hint": "Musik / Audio-Generierung."},
    "coding": {"label": "Code Studio", "hint": "Developer OS — Coding mit AI."},
    "automation_lab": {"label": "Automations", "hint": "Agent-Flows und Automation Lab."},
}

QUICK_PROMPTS = [
    ("Wo ist Football?", "football"),
    ("Premium upgraden", "premium"),
    ("Support Ticket", "support"),
    ("Tokens & Plan", "dashboard"),
    ("Beta Status", "beta"),
]

BETA_TIPS = [
    "Production Beta: Melde Bugs über Support mit Kategorie «Bug».",
    "Elite Football: Odds Lab mit EV, Confidence und Bankroll-Hinweis (nur Analyse).",
    "OAuth: Google-Login braucht exakte Redirect-URI in der Console.",
    "Railway: DATA_DIR=/data und APP_BASE_URL=https://mabyte.de setzen.",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def sanitize_user_message(text: str, max_len: int = 500) -> str:
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", (text or "").strip())
    return cleaned[:max_len]


def detect_nav_target(query: str) -> str | None:
    q = _normalize(query)
    if not q:
        return None
    aliases = {
        "home": ["home", "start", "mission", "dashboard start"],
        "chat": ["chat", "assistant", "ai", "mab ai", "fragen"],
        "football": ["football", "soccer", "odds", "match", "liga"],
        "premium": ["premium", "upgrade", "stripe", "zahlung", "abo"],
        "support": ["support", "ticket", "hilfe", "bug", "problem"],
        "redeem": ["redeem", "code", "einlösen", "gutschein"],
        "dashboard": ["dashboard", "account", "tokens", "plan", "profil"],
        "projects": ["project", "projekte"],
        "image": ["bild", "image"],
        "video": ["video studio"],
        "reels": ["reels", "tiktok", "short"],
        "music": ["music", "musik", "song"],
        "coding": ["code", "coding", "developer"],
        "automation_lab": ["automation", "agent", "workflow"],
    }
    for page, keys in aliases.items():
        for k in keys:
            if k in q:
                return page
    return None


def build_guide_reply(
    query: str,
    *,
    current_page: str = "home",
    plan: str = "free",
    football_plan: str = "none",
    tokens: int = 0,
) -> dict[str, Any]:
    """Returns {text, navigate, page} — never executes privileged ops."""
    q = sanitize_user_message(query)
    qn = _normalize(q)

    if qn in ("beta", "beta status", "production", "launch"):
        tips = "\n".join(f"• {t}" for t in BETA_TIPS)
        return {
            "text": (
                "**MaByte Production Beta**\n\n"
                f"Aktueller Workspace: `{current_page}` · Plan `{plan}` · "
                f"Football `{football_plan}` · {tokens:,} Tokens.\n\n"
                f"{tips}\n\n"
                "Bei Blockern: Support-Ticket mit Priorität «Hoch»."
            ),
            "navigate": None,
            "page": None,
        }

    target = detect_nav_target(q)
    if target and target in NAV_PAGES:
        meta = NAV_PAGES[target]
        return {
            "text": (
                f"Ich bringe dich zu **{meta['label']}**.\n\n"
                f"{meta['hint']}"
            ),
            "navigate": target,
            "page": target,
        }

    if any(w in qn for w in ("sicher", "security", "oauth", "login")):
        return {
            "text": (
                "**Sicherheit (Beta)**\n\n"
                "• Sessions sind login-gebunden; Admin nur mit Rolle.\n"
                "• OAuth-State wird validiert — kein Auto-Linking bei E-Mail-Konflikt.\n"
                "• Premium-Features werden serverseitig geprüft (`football_access`).\n"
                "• Keine Passwörter oder Secrets im Chat eingeben."
            ),
            "navigate": None,
            "page": None,
        }

    if any(w in qn for w in ("elite", "odds", "value", "ev")):
        return {
            "text": (
                "**Football Elite · Odds Lab**\n\n"
                "Unter Football → Odds Lab: Live-Quoten, implizite Wahrscheinlichkeit, "
                "EV/Edge, Confidence und konservative Bankroll-Hinweise (nur Bildung, keine Wetten)."
            ),
            "navigate": "football",
            "page": "football",
        }

    # Default help for current page
    cur = NAV_PAGES.get(current_page, NAV_PAGES["home"])
    pages_list = ", ".join(NAV_PAGES[p]["label"] for p in list(NAV_PAGES)[:8])
    return {
        "text": (
            f"Du bist auf **{cur['label']}**. {cur['hint']}\n\n"
            f"Frag mich z. B.: «Football», «Premium», «Support», «Beta Status».\n\n"
            f"Workspaces: {pages_list} …"
        ),
        "navigate": None,
        "page": None,
    }


def format_reply_html(text: str) -> str:
    """Minimal markdown-like bold to HTML, escaped."""
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = safe.replace("\n", "<br>")
    return safe
