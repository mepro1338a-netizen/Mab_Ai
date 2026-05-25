import html

import pandas as pd
import streamlit as st

from config import PLANS, TOKEN_COSTS, DAILY_LIMITS
from database import (
    get_user,
    redeem_code,
    create_support_message,
    list_support_messages,
    list_ticket_replies,
    add_ticket_reply,
    list_usage,
    list_purchases,
)
from ui.premium_foundation import (
    inject_beta_global_css,
    premium_foundation_css,
    render_empty_state,
    render_page_hero,
    render_status_badge,
)
from redeem_tracking import list_redeem_redemptions, redeem_code_tracked
from ui.styles import inject_css, page_layout_css
from ui.os_helper import render_os_guide_dashboard
from ui.prompt_ui import (
    inject_ma_prompt_css,
    ma_chat_input,
    prompt_text_area,
    render_os_hero,
    render_os_ready_hint,
    render_quickstart_grid,
)
from ui_core import require_login, sync_session_user


def refresh_user():
    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)


def current_plan_key():
    return st.session_state.get("plan", "free")


def current_plan():
    return PLANS.get(current_plan_key(), PLANS["free"])


def plan_is_current(plan_key):
    return current_plan_key() == plan_key


def usage_count(tool):
    usage = list_usage(st.session_state.get("user"))
    return len([u for u in usage if str(u.get("tool", "")) == tool])


def _dashboard_css() -> None:
    inject_beta_global_css()
    inject_css(page_layout_css(1180, 88, 42) + """
.dash-hero {
    border-radius: 32px;
    padding: 34px 38px;
    margin-bottom: 24px;
    background:
        radial-gradient(circle at 90% 10%, rgba(168,85,247,.26), transparent 36%),
        radial-gradient(circle at 4% 0%, rgba(96,165,250,.18), transparent 34%),
        linear-gradient(135deg, rgba(10,14,34,.98), rgba(6,8,20,.99));
    border: 1px solid rgba(255,231,163,.12);
    box-shadow: 0 30px 72px rgba(0,0,0,.36);
}
.dash-kicker {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .26em;
    text-transform: uppercase;
}
.dash-title {
    color: #ffe7a3 !important;
    font-size: 40px;
    font-weight: 1000;
    letter-spacing: -1.8px;
    margin-top: 10px;
}
.dash-sub {
    color: #94a3b8 !important;
    font-size: 15px;
    margin-top: 10px;
    max-width: 680px;
    line-height: 1.55;
}
.dash-stat-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 22px;
}
@media (max-width: 1100px) {
    .dash-stat-grid { grid-template-columns: repeat(2, 1fr); }
}
.dash-stat {
    border-radius: 20px;
    padding: 16px 18px;
    background: linear-gradient(145deg, rgba(18,14,34,.9), rgba(8,7,18,.98));
    border: 1px solid rgba(168,85,247,.18);
}
.dash-stat .lbl {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.dash-stat .val {
    color: #ffe7a3 !important;
    font-size: 24px;
    font-weight: 1000;
    margin-top: 8px;
}
.dash-ws-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}
.dash-ws-item {
    border-radius: 16px;
    padding: 14px 16px;
    border: 1px solid rgba(255,255,255,.06);
    background: rgba(12,16,32,.65);
}
.dash-ws-item.on {
    border-color: rgba(34,197,94,.35);
    background: rgba(6,78,59,.2);
}
.dash-ws-item.off {
    opacity: .75;
}
.dash-ws-item .name {
    color: #f8fafc !important;
    font-size: 14px;
    font-weight: 900;
}
.dash-ws-item .st {
    font-size: 11px;
    font-weight: 800;
    margin-top: 4px;
}
.dash-ws-item.on .st { color: #86efac !important; }
.dash-ws-item.off .st { color: #64748b !important; }
.dash-limit-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,.05);
    color: #e2e8f0 !important;
    font-size: 13px;
    font-weight: 700;
}
.dash-limit-row span:last-child {
    color: #ffe7a3 !important;
    font-weight: 1000;
}
.dash-activity {
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 8px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.06);
}
.dash-activity .t {
    color: #f8fafc !important;
    font-size: 14px;
    font-weight: 900;
}
.dash-activity .d {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 4px;
}
.os-guide-panel {
    border-radius: 22px;
    padding: 18px 20px;
    margin-bottom: 14px;
    background:
        radial-gradient(circle at 100% 0%, rgba(168,85,247,.2), transparent 42%),
        linear-gradient(135deg, rgba(18,12,36,.96), rgba(8,8,18,.98));
    border: 1px solid rgba(168,85,247,.22);
}
.os-guide-kicker {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .2em;
    text-transform: uppercase;
}
.os-guide-title {
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
    margin-top: 6px;
}
.os-guide-sub {
    color: #94a3b8 !important;
    font-size: 13px;
    margin-top: 6px;
    line-height: 1.45;
}
.os-guide-reply {
    border-radius: 16px;
    padding: 14px 16px;
    min-height: 120px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.07);
    color: #cbd5e1 !important;
    font-size: 13px;
    line-height: 1.55;
}
.os-guide-empty { color: #64748b !important; font-style: italic; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(14,16,36,.94), rgba(8,10,22,.98)) !important;
    border: 1px solid rgba(168,85,247,.14) !important;
    border-radius: 24px !important;
}
""")


def _nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def _forward_prompt_to_chat(text: str) -> None:
    st.session_state.chat_pending_prompt = text
    st.session_state.page = "chat"
    st.rerun()


def render_dashboard():
    require_login()
    refresh_user()
    _dashboard_css()
    inject_ma_prompt_css()

    plan_key = current_plan_key()
    plan = current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = fb_plan.replace("football_", "").title() if fb_plan != "none" else "Kein Plan"
    user = st.session_state.get("user", "User")

    render_os_hero()
    render_os_ready_hint()
    quick = render_quickstart_grid("dash")
    if quick:
        _forward_prompt_to_chat(quick)

    pending = st.session_state.pop("dash_pending_prompt", None)
    prompt = ma_chat_input("Frag MaByte...")
    if pending:
        _forward_prompt_to_chat(pending)
    if prompt:
        _forward_prompt_to_chat(prompt)

    with st.expander("Mab AI · OS Guide", expanded=False):
        render_os_guide_dashboard()

    with st.expander("Account & Workspaces", expanded=True):
        st.markdown(
            f"""
<div class="dash-hero" style="padding:22px;margin-bottom:16px;">
    <div class="dash-kicker">Account</div>
    <div class="dash-title" style="font-size:28px;">{html.escape(str(user))}</div>
    <div class="dash-sub">Plan, Tokens, Football — Übersicht</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        stats = [
            ("MaByte Plan", plan.get("label", plan_key)),
            ("Tokens", f"{tokens:,}".replace(",", ".")),
            ("Football", fb_label),
            ("Tier", plan.get("badge", "Starter")),
        ]
        cards = "".join(
            f'<div class="dash-stat"><div class="lbl">{html.escape(l)}</div>'
            f'<div class="val">{html.escape(v)}</div></div>'
            for l, v in stats
        )
        st.markdown(
            f'<div class="dash-stat-grid" style="grid-template-columns:repeat(4,minmax(0,1fr));">{cards}</div>',
            unsafe_allow_html=True,
        )

    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("AI Assistant", key="dash_go_chat", width="stretch"):
            _nav("chat")
    with qa2:
        if st.button("Football AI", key="dash_go_fb", width="stretch"):
            _nav("football")
    with qa3:
        if st.button("Premium", key="dash_go_prem", width="stretch"):
            _nav("premium")
    with qa4:
        if st.button("Projekte", key="dash_go_proj", width="stretch"):
            _nav("projects")

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:12px;">Workspace Matrix</div>',
                unsafe_allow_html=True,
            )
            features = plan.get("features", [])
            rows = [
                ("AI Assistant", "chat"),
                ("Developer OS", "coding"),
                ("Creative Workspace", "image"),
                ("Music Studio", "music"),
                ("Reels Studio", "reels"),
                ("Video Studio", "video"),
                ("Football Intelligence", "football"),
                ("Automation Lab", "automation"),
            ]
            items = []
            for label, feature in rows:
                allowed = "all" in features or feature in features
                cls = "on" if allowed else "off"
                st_txt = "Freigeschaltet" if allowed else "Upgrade nötig"
                items.append(
                    f'<div class="dash-ws-item {cls}">'
                    f'<div class="name">{html.escape(label)}</div>'
                    f'<div class="st">{st_txt}</div></div>'
                )
            st.markdown(
                f'<div class="dash-ws-grid">{"".join(items)}</div>',
                unsafe_allow_html=True,
            )

    with right:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:12px;">Tageslimits</div>',
                unsafe_allow_html=True,
            )
            limits = DAILY_LIMITS.get(plan_key, DAILY_LIMITS["free"])
            limit_rows = [
                ("Chat", limits.get("chat", 0)),
                ("Coding", limits.get("coding", 0)),
                ("Images", limits.get("image", 0)),
                ("Reels", limits.get("reels", 0)),
                ("Videos", limits.get("video", 0)),
                ("Football Reports", limits.get("football_report", 0)),
                ("Automation", limits.get("automation_job", 0)),
            ]
            lr = "".join(
                f'<div class="dash-limit-row"><span>{html.escape(k)}</span>'
                f'<span>{html.escape(str(v))} / Tag</span></div>'
                for k, v in limit_rows
            )
            st.markdown(lr, unsafe_allow_html=True)

    st.divider()

    with st.expander("Token-Kosten (Referenz)", expanded=False):
        token_rows = [
            {"Workspace": "AI Assistant", "Action": "Prompt", "Cost": TOKEN_COSTS.get("chat", 1)},
            {"Workspace": "Developer OS", "Action": "Coding", "Cost": TOKEN_COSTS.get("coding", 10)},
            {"Workspace": "Creative", "Action": "Image", "Cost": TOKEN_COSTS.get("image", 10)},
            {"Workspace": "Music", "Action": "Song", "Cost": TOKEN_COSTS.get("music", 50)},
            {"Workspace": "Reels", "Action": "Package", "Cost": TOKEN_COSTS.get("reels", 20)},
            {"Workspace": "Video", "Action": "Base", "Cost": TOKEN_COSTS.get("video_base", 10)},
            {"Workspace": "Football", "Action": "Report", "Cost": TOKEN_COSTS.get("football_report", 80)},
            {"Workspace": "Automation", "Action": "Job", "Cost": TOKEN_COSTS.get("automation_job", 100)},
        ]
        st.dataframe(pd.DataFrame(token_rows), width="stretch", hide_index=True)

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:10px;">Letzte Aktivität</div>',
                unsafe_allow_html=True,
            )
            usage = list_usage(st.session_state.get("user"))
            if usage:
                blocks = []
                for row in usage[:12]:
                    tool = str(row.get("tool", "system")).replace("_", " ").title()
                    created = str(row.get("created_at", ""))[:16]
                    blocks.append(
                        f'<div class="dash-activity"><div class="t">{html.escape(tool)}</div>'
                        f'<div class="d">{html.escape(created)}</div></div>'
                    )
                st.markdown("".join(blocks), unsafe_allow_html=True)
            else:
                render_empty_state("Noch leer", "Starte einen Workspace — Aktivität erscheint hier.")

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


def _redeem_extra_css() -> None:
    inject_css("""
.redeem-terminal {
    border-radius: 22px;
    padding: 20px 22px;
    margin-bottom: 14px;
    background:
        radial-gradient(circle at 100% 0%, rgba(168,85,247,.18), transparent 42%),
        linear-gradient(160deg, rgba(14,12,28,.96), rgba(8,8,18,.98));
    border: 1px solid rgba(255,231,163,.14);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
}
.redeem-terminal .rt-label {
    color: #c084fc !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .22em;
    text-transform: uppercase;
}
.redeem-terminal .rt-title {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
    margin-top: 8px;
}
.redeem-terminal .rt-hint {
    color: #64748b !important;
    font-size: 12px;
    margin-top: 8px;
    line-height: 1.5;
}
.redeem-type-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
}
.redeem-type {
    border-radius: 16px;
    padding: 14px 16px;
    border: 1px solid rgba(255,255,255,.07);
    background: rgba(12,16,32,.72);
}
.redeem-type .name {
    color: #f8fafc !important;
    font-size: 14px;
    font-weight: 900;
}
.redeem-type .desc {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-top: 5px;
    line-height: 1.45;
}
.redeem-type.tokens { border-color: rgba(96,165,250,.28); }
.redeem-type.plan { border-color: rgba(168,85,247,.32); }
.redeem-type.football { border-color: rgba(34,197,94,.28); }
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(196,181,253,.35) !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    letter-spacing: .04em !important;
    min-height: 48px !important;
    box-shadow: 0 12px 28px rgba(124,58,237,.28) !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    border-color: rgba(255,231,163,.45) !important;
    filter: brightness(1.06);
}
.stTextInput input {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
}
""")


def _user_redeem_history(username: str, limit: int = 12) -> list[dict]:
    rows = list_redeem_redemptions()
    out = []
    for row in rows:
        if len(row) < 6:
            continue
        if str(row[1]) != username:
            continue
        out.append(
            {
                "id": row[0],
                "code": row[2],
                "created_at": row[5],
            }
        )
        if len(out) >= limit:
            break
    return out


def render_redeem():
    require_login()
    refresh_user()
    _dashboard_css()
    _redeem_extra_css()

    plan_key = current_plan_key()
    plan = current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = fb_plan.replace("football_", "").title() if fb_plan != "none" else "Kein Plan"
    user = st.session_state.get("user", "User")
    plan_label = plan.get("label", plan_key.title())

    st.markdown(
        f"""
<div class="dash-hero">
    <div class="dash-kicker">MaByte · License Activation</div>
    <div class="dash-title">Redeem Center</div>
    <div class="dash-sub">
        Einlöse-Codes für <strong>Tokens</strong>, <strong>Plan-Upgrades</strong> und
        <strong>Football Premium</strong> — sofort auf deinen Account gebucht.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    cards = [
        ("Tokens", f"{tokens:,}".replace(",", ".")),
        ("MaByte Plan", plan_label),
        ("Football", fb_label),
    ]
    stat_html = "".join(
        f'<div class="dash-stat"><div class="lbl">{html.escape(l)}</div>'
        f'<div class="val">{html.escape(v)}</div></div>'
        for l, v in cards
    )
    st.markdown(
        f'<div class="dash-stat-grid" style="grid-template-columns:repeat(3,minmax(0,1fr));">{stat_html}</div>',
        unsafe_allow_html=True,
    )

    col_main, col_info = st.columns([1.15, 0.85], gap="large")

    with col_main:
        st.markdown(
            """
<div class="redeem-terminal">
    <div class="rt-label">Activation Terminal</div>
    <div class="rt-title">Code einlösen</div>
    <div class="rt-hint">Gib deinen Code ein — Groß-/Kleinschreibung wird ignoriert. Ein Code pro Einlösung.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            with st.form("redeem_code_form", clear_on_submit=True):
                code = st.text_input(
                    "Lizenz-Code",
                    placeholder="MABYTE-XXXX-XXXX",
                    help="Code vom Admin, Partner oder Aktion.",
                )
                submitted = st.form_submit_button(
                    "Code aktivieren",
                    width="stretch",
                    type="primary",
                )
                if submitted:
                    if not (code or "").strip():
                        st.warning("Bitte einen Code eingeben.")
                    else:
                        ok, msg = redeem_code(st.session_state.get("user"), code)
                        if ok:
                            redeem_code_tracked(
                                st.session_state.get("user"),
                                (code or "").strip().upper(),
                            )
                            refresh_user()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with col_info:
        with st.container(border=True):
            st.markdown(
                '<div class="dash-kicker" style="margin-bottom:12px;">Was Codes freischalten</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """
<div class="redeem-type-grid">
    <div class="redeem-type tokens">
        <div class="name">Token Boost</div>
        <div class="desc">Guthaben für AI Workspaces — Chat, Bild, Video, Music, Reels.</div>
    </div>
    <div class="redeem-type plan">
        <div class="name">MaByte Plan</div>
        <div class="desc">Pro, Grand oder Elite — höhere Limits und Workspace-Freigaben.</div>
    </div>
    <div class="redeem-type football">
        <div class="name">Football Premium</div>
        <div class="desc">Starter, Pro oder Elite — Odds Lab, AI Engine und Match Center.</div>
    </div>
</div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("Codes werden im Admin Panel erstellt. Bei Problemen: Support-Ticket.")

    st.markdown(
        '<div class="dash-kicker" style="margin:18px 0 10px 0;">Einlösungs-Verlauf</div>',
        unsafe_allow_html=True,
    )

    history = _user_redeem_history(str(user))
    if history:
        for row in history:
            code_mask = html.escape(str(row.get("code") or "—"))
            when = html.escape(str(row.get("created_at") or "")[:16])
            st.markdown(
                f"""
<div class="dash-activity" style="border-left:3px solid rgba(168,85,247,.45);">
    <div class="t">{code_mask}</div>
    <div class="d">Eingelöst · {when}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
    else:
        render_empty_state(
            "Noch keine Einlösungen",
            "Nach der ersten Aktivierung erscheint dein Verlauf hier.",
        )


def _support_css() -> None:
    premium_foundation_css(1100, 88)


def _priority_badge(priority: str) -> str:
    p = (priority or "normal").lower()
    colors = {
        "low": ("#64748b", "#cbd5e1"),
        "normal": ("#4c1d95", "#e9d5ff"),
        "high": ("#b45309", "#fde68a"),
        "urgent": ("#991b1b", "#fecaca"),
    }
    bg, fg = colors.get(p, colors["normal"])
    return (
        f'<span style="display:inline-flex;padding:4px 10px;border-radius:999px;'
        f'font-size:10px;font-weight:900;background:{bg};color:{fg}!important;">'
        f'{html.escape(p.upper())}</span>'
    )


def _render_ticket_timeline(ticket: dict) -> None:
    tid = int(ticket.get("id") or 0)
    events = [
        {
            "when": str(ticket.get("created_at") or "")[:16],
            "who": "Du",
            "body": str(ticket.get("message") or ""),
            "kind": "Erstellt",
        }
    ]
    for rep in list_ticket_replies(tid):
        events.append(
            {
                "when": str(rep.get("created_at") or "")[:16],
                "who": "MaByte Team" if int(rep.get("is_staff") or 0) else "Du",
                "body": str(rep.get("body") or ""),
                "kind": "Antwort",
            }
        )
    for ev in events:
        border = "#22c55e" if ev["who"] == "MaByte Team" else "rgba(168,85,247,.45)"
        st.markdown(
            f"""
<div class="dash-activity" style="border-left:3px solid {border};margin-bottom:8px;">
    <div class="t">{html.escape(ev['kind'])} · {html.escape(ev['who'])}</div>
    <div class="d">{html.escape(ev['when'])}</div>
    <div style="color:#cbd5e1;font-size:13px;line-height:1.55;margin-top:8px;">{html.escape(ev['body'][:600])}</div>
</div>
            """,
            unsafe_allow_html=True,
        )


def render_support():
    require_login()
    _dashboard_css()
    _support_css()

    render_page_hero(
        "MaByte · Support OS",
        "Ticket Center",
        "Prioritäten, Status-Timeline und Team-Antworten — Production Beta Support für Mab AI.",
    )

    tickets = list_support_messages()
    own_tickets = [t for t in tickets if t.get("username") == st.session_state.get("user")]
    open_count = sum(
        1 for t in own_tickets if str(t.get("status") or "open") in ("open", "in_progress")
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tickets", len(own_tickets))
    with c2:
        st.metric("Offen", open_count)
    with c3:
        st.metric("Geschlossen", len(own_tickets) - open_count)
    with c4:
        urgent = sum(1 for t in own_tickets if str(t.get("priority") or "") == "urgent")
        st.metric("Dringend", urgent)

    with st.container(border=True):
        st.markdown(
            '<div class="dash-kicker" style="margin-bottom:12px;">Neues Ticket</div>',
            unsafe_allow_html=True,
        )
        with st.form("support_ticket_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                category = st.selectbox(
                    "Kategorie",
                    [
                        "Account",
                        "Payment",
                        "Football Premium",
                        "Tokens",
                        "Workspace",
                        "Bug",
                        "Beta / Launch",
                        "Sonstiges",
                    ],
                )
            with c2:
                priority = st.selectbox(
                    "Priorität",
                    ["normal", "high", "urgent", "low"],
                    index=0,
                    help="Bei Launch-Blockern: urgent.",
                )
            with c3:
                subject = st.text_input("Betreff", placeholder="Kurze Zusammenfassung")
            message = prompt_text_area(
                placeholder="Frag MaByte… Support-Anliegen beschreiben…",
                key="support_ticket_msg",
                height=160,
            )
            submitted = st.form_submit_button("Ticket erstellen", width="stretch", type="primary")

            if submitted:
                if not subject or not message:
                    st.warning("Bitte Betreff und Nachricht ausfüllen.")
                else:
                    ok, msg = create_support_message(
                        st.session_state.get("user"),
                        st.session_state.get("email", ""),
                        category,
                        subject,
                        message,
                        priority=priority,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown(
        '<div class="dash-kicker" style="margin:16px 0 10px 0;">Meine Tickets · Timeline</div>',
        unsafe_allow_html=True,
    )

    if own_tickets:
        for ticket in own_tickets:
            status = str(ticket.get("status") or "open")
            prio = str(ticket.get("priority") or "normal")
            with st.expander(
                f"#{ticket.get('id')} · {ticket.get('subject', 'Ticket')} · {status}",
                expanded=status in ("open", "in_progress"),
            ):
                st.markdown(_priority_badge(prio), unsafe_allow_html=True)
                render_status_badge(status)
                _render_ticket_timeline(ticket)
                if status != "closed":
                    with st.form(f"ticket_reply_{ticket.get('id')}"):
                        extra = st.text_area("Nachricht ergänzen", height=100)
                        if st.form_submit_button("Senden", width="stretch"):
                            if extra.strip():
                                ok, rmsg = add_ticket_reply(
                                    int(ticket.get("id")),
                                    st.session_state.get("user"),
                                    extra.strip(),
                                    is_staff=False,
                                )
                                if ok:
                                    st.success(rmsg)
                                    st.rerun()
                                else:
                                    st.error(rmsg)
    else:
        render_empty_state(
            "Noch keine Tickets",
            "Erstelle oben ein Ticket — unser Team antwortet im Admin Panel.",
        )


def plan_card(plan_key):
    plan = PLANS[plan_key]
    current = plan_is_current(plan_key)

    with st.container(border=True):
        if current:
            st.success("Aktueller Plan")

        st.subheader(plan.get("label", plan_key))
        st.caption(plan.get("badge", ""))
        st.markdown(f"## {plan.get('price', '')}")
        st.write(plan.get("description", ""))

        st.metric("Tokens", plan.get("tokens", 0))

        st.divider()

        for item in plan.get("highlights", []):
            st.write(f"- {item}")

        st.divider()

        button_label = "Aktiv" if current else f"{plan.get('label', plan_key)} auswählen"

        if st.button(
            button_label,
            key=f"buy_{plan_key}",
            width="stretch",
            disabled=current,
        ):
            st.session_state.selected_plan = plan_key
            st.success(
                f"{plan.get('label', plan_key)} ausgewählt. Stripe Checkout wird später verbunden."
            )


def render_premium():
    require_login()
    refresh_user()

    st.title("MaByte Premium")
    st.caption("Upgrade dein AI Operating System mit Workspaces, Limits und Agent Capacity.")

    st.info("Pro = Creator OS. Grand = Content Engine & Automation. Elite = Full AI Operating System.")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        plan_card("free")

    with c2:
        plan_card("pro")

    with c3:
        plan_card("grand")

    with c4:
        plan_card("elite")

    st.divider()

    with st.container(border=True):
        st.subheader("Premium Roadmap")
        st.write("Stripe Checkout, automatische Plan-Upgrades und Webhooks werden als nächster Schritt verbunden.")
        st.write("Bis dahin können Pläne über Admin oder Redeem Codes freigeschaltet werden.")
