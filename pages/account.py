import streamlit as st
import pandas as pd

from config import PLANS, TOKEN_COSTS, DAILY_LIMITS
from database import (
    get_user,
    redeem_code,
    create_support_message,
    list_support_messages,
    list_usage,
    list_purchases,
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


def render_dashboard():
    require_login()
    refresh_user()

    plan_key = current_plan_key()
    plan = current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)

    st.title("ðŸ“Š Account Command Center")
    st.caption("Plan, Tokens, Nutzung, Limits und Workspace Access.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Plan", plan.get("label", plan_key))

    with c2:
        st.metric("Tokens", tokens)

    with c3:
        st.metric("Tier", plan.get("badge", "Starter"))

    with c4:
        st.metric("Role", st.session_state.get("role", "user"))

    st.divider()

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("ðŸ§© Workspace Access")

            features = plan.get("features", [])

            rows = [
                ["AI Assistant", "chat"],
                ["Developer OS", "coding"],
                ["Creative Workspace", "image"],
                ["Music Studio", "music"],
                ["Content Engine", "reels"],
                ["Media Studio", "video"],
                ["Football Intelligence", "football"],
                ["Automation Lab", "automation"],
            ]

            for label, feature in rows:
                allowed = "all" in features or feature in features
                st.write(("âœ… " if allowed else "ðŸ”’ ") + label)

    with right:
        with st.container(border=True):
            st.subheader("âš¡ Current Limits")

            limits = DAILY_LIMITS.get(plan_key, DAILY_LIMITS["free"])

            st.write(f"Chat: {limits.get('chat', 0)} / Tag")
            st.write(f"Coding: {limits.get('coding', 0)} / Tag")
            st.write(f"Images: {limits.get('image', 0)} / Tag")
            st.write(f"Reels: {limits.get('reels', 0)} / Tag")
            st.write(f"Videos: {limits.get('video', 0)} / Tag")
            st.write(f"Football Reports: {limits.get('football_report', 0)} / Tag")
            st.write(f"Automation Jobs: {limits.get('automation_job', 0)} / Tag")

    st.divider()

    st.subheader("ðŸ’° Token Costs")

    token_rows = [
        {"Workspace": "AI Assistant", "Action": "Prompt", "Cost": TOKEN_COSTS.get("chat", 1)},
        {"Workspace": "Developer OS", "Action": "Coding Prompt", "Cost": TOKEN_COSTS.get("coding", 10)},
        {"Workspace": "Creative Workspace", "Action": "Image Prompt", "Cost": TOKEN_COSTS.get("image", 10)},
        {"Workspace": "Music Studio", "Action": "Song Concept", "Cost": TOKEN_COSTS.get("music", 50)},
        {"Workspace": "Content Engine", "Action": "Reel Package", "Cost": TOKEN_COSTS.get("reels", 20)},
        {"Workspace": "Media Studio", "Action": "Video Base", "Cost": TOKEN_COSTS.get("video_base", 10)},
        {"Workspace": "Media Studio", "Action": "Video Second", "Cost": TOKEN_COSTS.get("video_second", 5)},
        {"Workspace": "Football Intelligence", "Action": "Report", "Cost": TOKEN_COSTS.get("football_report", 80)},
        {"Workspace": "Automation Lab", "Action": "Automation Job", "Cost": TOKEN_COSTS.get("automation_job", 100)},
    ]

    st.dataframe(
        pd.DataFrame(token_rows),
        width="stretch",
        hide_index=True,
    )

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("ðŸ§¾ Latest Usage")
        usage = list_usage(st.session_state.get("user"))

        if usage:
            st.dataframe(
                pd.DataFrame(usage).head(20),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("Noch keine Nutzung vorhanden.")

    with col_b:
        st.subheader("ðŸ’³ Payments")
        payments = list_purchases(st.session_state.get("user"))

        if payments:
            st.dataframe(
                pd.DataFrame(payments),
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("Noch keine Zahlungen vorhanden.")


def render_redeem():
    require_login()

    st.title("ðŸŽ Redeem Center")
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

    st.title("ðŸ†˜ Support Center")
    st.caption("Tickets erstellen, Bugs melden und Hilfe bekommen.")

    with st.container(border=True):
        with st.form("support_ticket_form"):
            category = st.selectbox(
                "Kategorie",
                ["Account", "Payment", "Tokens", "Workspace", "Bug", "Sonstiges"],
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
        st.dataframe(
            pd.DataFrame(own_tickets),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("Du hast noch keine Tickets.")


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
            st.write(f"âœ… {item}")

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

    st.title("ðŸ’Ž MaByte Premium")
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
        st.subheader("ðŸš€ Premium Roadmap")
        st.write("Stripe Checkout, automatische Plan-Upgrades und Webhooks werden als nächster Schritt verbunden.")
        st.write("Bis dahin können Pläne über Admin oder Redeem Codes freigeschaltet werden.")
