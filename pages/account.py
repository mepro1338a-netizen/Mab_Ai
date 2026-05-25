import html

import pandas as pd
import streamlit as st

from config import PLANS, TOKEN_COSTS, DAILY_LIMITS
from database import (
    get_user,
    redeem_code,
    create_support_message,
    list_support_messages,
    list_usage,
    list_purchases,
)
from ui.premium_foundation import inject_beta_global_css, render_empty_state
from ui.styles import inject_css, page_layout_css
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
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(14,16,36,.94), rgba(8,10,22,.98)) !important;
    border: 1px solid rgba(168,85,247,.14) !important;
    border-radius: 24px !important;
}
""")


def _nav(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def render_dashboard():
    require_login()
    refresh_user()
    _dashboard_css()

    plan_key = current_plan_key()
    plan = current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)
    fb_plan = str(st.session_state.get("football_plan") or "none")
    fb_label = fb_plan.replace("football_", "").title() if fb_plan != "none" else "Kein Plan"
    user = st.session_state.get("user", "User")

    st.markdown(
        f"""
<div class="dash-hero">
    <div class="dash-kicker">MaByte · Account Command</div>
    <div class="dash-title">Dashboard</div>
    <div class="dash-sub">
        Willkommen, <strong>{html.escape(str(user))}</strong> — Plan, Tokens, Football Premium
        und Workspace-Status in einem Überblick.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    stats = [
        ("MaByte Plan", plan.get("label", plan_key)),
        ("Tokens", f"{tokens:,}".replace(",", ".")),
        ("Football", fb_label),
        ("Tier", plan.get("badge", "Starter")),
        ("Rolle", st.session_state.get("role", "user")),
    ]
    cards = "".join(
        f'<div class="dash-stat"><div class="lbl">{html.escape(l)}</div>'
        f'<div class="val">{html.escape(v)}</div></div>'
        for l, v in stats
    )
    st.markdown(f'<div class="dash-stat-grid">{cards}</div>', unsafe_allow_html=True)

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


def render_redeem():
    require_login()

    st.title("Redeem Center")
    st.caption("Codes einlösen und Tokens oder Plan-Upgrades freischalten.")

    with st.container(border=True):
        code = st.text_input("Code", placeholder="DEIN-CODE")

        if st.button("Code einlösen", width="stretch"):
            if not code:
                st.warning("Bitte Code eingeben.")
                return

            ok, msg = redeem_code(st.session_state.get("user"), code)

            if ok:
                refresh_user()
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def render_support():
    require_login()

    premium_foundation_css(1100, 88)
    render_page_hero(
        "Support Center",
        "Tickets & Hilfe",
        "Professioneller Support für Account, Zahlung, Football Premium und technische Fragen.",
    )

    with st.container(border=True):
        with st.form("support_ticket_form"):
            category = st.selectbox(
                "Kategorie",
                [
                    "Account",
                    "Payment",
                    "Football Premium",
                    "Tokens",
                    "Workspace",
                    "Bug",
                    "Sonstiges",
                ],
            )

            subject = st.text_input("Betreff")
            message = st.text_area("Nachricht", height=160)

            submitted = st.form_submit_button(
                "Ticket erstellen",
                width="stretch",
            )

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
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.divider()

    st.subheader("Meine Tickets")

    tickets = list_support_messages()

    own_tickets = [
        t for t in tickets
        if t.get("username") == st.session_state.get("user")
    ]

    if own_tickets:
        for ticket in own_tickets:
            status = str(ticket.get("status") or "open")
            with st.container(border=True):
                h1, h2 = st.columns([3, 1])
                with h1:
                    st.markdown(f"**#{ticket.get('id')} · {ticket.get('subject', 'Ticket')}**")
                with h2:
                    render_status_badge(status)
                st.caption(
                    f"{ticket.get('category', '')} · {str(ticket.get('created_at', ''))[:16]}"
                )
                st.write(ticket.get("message", ""))
    else:
        render_empty_state(
            "Noch keine Tickets",
            "Erstelle oben ein Ticket — wir melden uns im Admin Panel.",
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
