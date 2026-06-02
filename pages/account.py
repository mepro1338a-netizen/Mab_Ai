"""Profile page (minimal): usage, limits, payments."""

from __future__ import annotations

import html

import streamlit as st

from config import PLANS, TOKEN_COSTS
from database import get_user, list_purchases
from ui.dashboard_ui import (
    inject_dashboard_css,
    render_daily_limits,
    render_header,
    render_recent_activity,
    render_stats,
)
from ui.premium_foundation import render_empty_state
from ui_core import require_login, sync_session_user


def _osg_normalize(text: str) -> str:
    import re

    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _osg_sanitize_user_message(text: str, max_len: int = 500) -> str:
    import re

    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", (text or "").strip())
    return cleaned[:max_len]


def _osg_detect_nav_target(query: str) -> str | None:
    q = _osg_normalize(query)
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
        "creator": ["creator", "studio", "shorts", "video"],
        "video": ["video studio", "video"],
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


def _osg_format_reply_html(text: str) -> str:
    """Minimal markdown-like bold to HTML, escaped."""
    import re

    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = safe.replace("\n", "<br>")
    return safe


def _osg_build_guide_reply(
    query: str,
    *,
    current_page: str = "home",
    plan: str = "free",
    football_plan: str = "none",
    tokens: int = 0,
) -> dict:
    """Returns {text, navigate, page} — never executes privileged ops."""
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
        "creator": {"label": "Creator Studio", "hint": "Shorts & Video — ein Workspace."},
        "video": {"label": "Creator Studio", "hint": "Shorts & Video — Video-Modus."},
        "reels": {"label": "Creator Studio", "hint": "Shorts & Video — Shorts-Modus."},
        "music": {"label": "Music Studio", "hint": "Musik / Audio-Generierung."},
        "coding": {"label": "Code Studio", "hint": "Developer OS — Coding mit AI."},
        "automation_lab": {"label": "Automations", "hint": "Agent-Flows und Automation Lab."},
    }

    BETA_TIPS = [
        "Production Beta: Melde Bugs über Support mit Kategorie «Bug».",
        "Elite Football: Odds Lab mit EV, Confidence und Bankroll-Hinweis (nur Analyse).",
        "OAuth: Google-Login braucht exakte Redirect-URI in der Console.",
        "Railway: DATA_DIR=/data und APP_BASE_URL=https://mabyte.de setzen.",
    ]

    q = _osg_sanitize_user_message(query)
    qn = _osg_normalize(q)

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

    target = _osg_detect_nav_target(q)
    if target and target in NAV_PAGES:
        meta = NAV_PAGES[target]
        return {
            "text": f"Ich bringe dich zu **{meta['label']}**.\n\n{meta['hint']}",
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

    cur = NAV_PAGES.get(current_page, NAV_PAGES["home"])
    pages_list = ", ".join(NAV_PAGES[p]["label"] for p in list(NAV_PAGES)[:8])
    return {
        "text": (
            f"Du bist auf **{cur['label']}**. {cur['hint']}\n\n"
            "Frag mich z. B.: «Football», «Premium», «Support», «Beta Status».\n\n"
            f"Workspaces: {pages_list} …"
        ),
        "navigate": None,
        "page": None,
    }


def render_os_guide_dashboard() -> None:
    """Mab AI Guide — shown on Dashboard only."""
    if not st.session_state.get("logged_in"):
        return

    st.session_state.setdefault("os_guide_history", [])
    st.session_state.setdefault("os_guide_last_reply", "")

    st.markdown(
        """
<div class="os-guide-panel">
    <div class="os-guide-kicker">Mab AI · OS Guide</div>
    <div class="os-guide-title">Production Beta Assistant</div>
    <div class="os-guide-sub">Navigation, Premium, Football & Support — sicher, ohne Admin-Rechte.</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    QUICK_PROMPTS = [
        ("Wo ist Football?", "football"),
        ("Premium upgraden", "premium"),
        ("Support Ticket", "support"),
        ("Tokens & Plan", "dashboard"),
        ("Beta Status", "beta"),
    ]
    from ui.prompt_ui import prompt_submit_button, prompt_text_input

    chips = st.columns(5)
    for i, (label, action) in enumerate(QUICK_PROMPTS):
        with chips[i % 5]:
            if st.button(label, key=f"os_dash_chip_{action}", width="stretch"):
                st.session_state.os_guide_pending_query = label
                st.rerun()

    c1, c2 = st.columns([1.2, 1])
    with c1:
        pending = st.session_state.pop("os_guide_pending_query", None)
        user_q = prompt_text_input(
            placeholder="z.B. Wo finde ich Odds Lab?",
            label="Frage an den Guide",
            key="os_guide_dash_input",
        )
        if prompt_submit_button("Senden", key="os_guide_dash_ask"):
            pending = user_q or pending

        if pending:
            reply = _osg_build_guide_reply(
                _osg_sanitize_user_message(str(pending)),
                current_page=str(st.session_state.get("page") or "dashboard"),
                plan=str(st.session_state.get("plan") or "free"),
                football_plan=str(st.session_state.get("football_plan") or "none"),
                tokens=int(st.session_state.get("tokens") or 0),
            )
            st.session_state.os_guide_last_reply = reply.get("text") or ""
            hist = list(st.session_state.get("os_guide_history") or [])
            hist.append({"q": str(pending)[:120], "a": st.session_state.os_guide_last_reply[:400]})
            st.session_state.os_guide_history = hist[-8:]
            nav = reply.get("navigate")
            if nav:
                st.session_state.page = nav
                st.rerun()

    with c2:
        last = st.session_state.get("os_guide_last_reply")
        if last:
            st.markdown(
                f'<div class="os-guide-reply">{_osg_format_reply_html(last)}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="os-guide-reply os-guide-empty">Stelle eine Frage oder wähle einen Quick-Link.</div>',
                unsafe_allow_html=True,
            )
        if st.button("Premium öffnen", key="os_guide_dash_support", width="stretch"):
            st.session_state.page = "premium"
            st.rerun()


def _refresh_user() -> None:
    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)


def _current_plan_key() -> str:
    return str(st.session_state.get("plan", "free") or "free")


def _current_plan() -> dict:
    return dict(PLANS.get(_current_plan_key(), PLANS["free"]))


def _nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def render_dashboard() -> None:
    require_login()
    _refresh_user()
    inject_dashboard_css()

    plan_key = _current_plan_key()
    plan = _current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = (
        fb_plan.replace("football_", "").title()
        if fb_plan not in ("none", "", "free")
        else "—"
    )
    user = str(st.session_state.get("user", "User"))

    st.markdown('<div class="mb-dash" aria-hidden="true"></div>', unsafe_allow_html=True)
    render_header(user=user, greeting=f"Profil · {html.escape(user)} — Nutzung, Limits und Zahlungen.")
    render_stats(
        plan_label=str(plan.get("label", plan_key)),
        tokens=tokens,
        football_label=fb_label,
        tier=str(plan.get("badge", "Starter")),
    )

    if st.button("Zurück zum Dashboard (Home)", key="dash_go_home", width="stretch"):
        _nav("home")

    with st.expander("Mab AI · OS Guide", expanded=False):
        render_os_guide_dashboard()

    with st.container(border=True):
        render_daily_limits(plan_key)

    with st.expander("Token-Kosten (Referenz)", expanded=False):
        token_rows = [
            {"Workspace": "AI Assistant", "Action": "Prompt", "Cost": TOKEN_COSTS.get("chat", 1)},
            {"Workspace": "Developer OS", "Action": "Coding", "Cost": TOKEN_COSTS.get("coding", 10)},
            {"Workspace": "Creative", "Action": "Image", "Cost": TOKEN_COSTS.get("image", 10)},
            {"Workspace": "Music", "Action": "Song", "Cost": TOKEN_COSTS.get("music", 50)},
            {"Workspace": "Video", "Action": "Base", "Cost": TOKEN_COSTS.get("video_base", 10)},
            {"Workspace": "Football", "Action": "Report", "Cost": TOKEN_COSTS.get("football_report", 80)},
            {"Workspace": "Automation", "Action": "Job", "Cost": TOKEN_COSTS.get("automation_job", 100)},
        ]
        st.dataframe(token_rows, width="stretch", hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            render_recent_activity(str(st.session_state.get("user") or ""), limit=12)

    with col_b:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:10px;">Zahlungen</div>',
                unsafe_allow_html=True,
            )
            payments = list_purchases(st.session_state.get("user"))
            if payments:
                blocks = []
                for row in payments[:10]:
                    plan_l = str(row.get("plan", row.get("product", "—")))
                    amt = str(row.get("amount", row.get("status", "")))
                    when = str(row.get("created_at", ""))[:16]
                    blocks.append(
                        f'<div class="dash-activity"><div class="t">{html.escape(plan_l)}</div>'
                        f'<div class="d">{html.escape(amt)} · {html.escape(when)}</div></div>'
                    )
                st.markdown("".join(blocks), unsafe_allow_html=True)
            else:
                render_empty_state("Keine Zahlungen", "Upgrades erscheinen nach Stripe Checkout.")

