import streamlit as st
import pandas as pd

from config import PLANS, TOKEN_COSTS
from database import (
    get_user,
    redeem_code,
    create_support_message,
    list_support_messages,
    list_usage,
    list_purchases,
)
from ui_helpers import require_login, sync_session_user


def render_dashboard():
    require_login()

    user = get_user(st.session_state.get("user"))

    if user:
        sync_session_user(user)

    st.title("📊 Dashboard")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Plan", st.session_state.get("plan", "free"))

    with c2:
        st.metric("Tokens", st.session_state.get("tokens", 0))

    with c3:
        st.metric("Role", st.session_state.get("role", "user"))

    st.divider()

    st.subheader("Token Kosten")

    token_rows = [
        {"Tool": "Chat", "Kosten": TOKEN_COSTS.get("chat", 1)},
        {"Tool": "Coding AI", "Kosten": TOKEN_COSTS.get("coding", 4)},
        {"Tool": "Image AI", "Kosten": TOKEN_COSTS.get("image", 15)},
        {"Tool": "Music AI", "Kosten": TOKEN_COSTS.get("music", 10)},
        {"Tool": "Reels Creator", "Kosten": TOKEN_COSTS.get("reels", 20)},
        {"Tool": "Video Base", "Kosten": TOKEN_COSTS.get("video_base", 10)},
        {"Tool": "Video pro Sekunde", "Kosten": TOKEN_COSTS.get("video_second", 5)},
    ]

    st.dataframe(
        pd.DataFrame(token_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Letzte Nutzung")

    usage = list_usage(st.session_state.get("user"))

    if usage:
        st.dataframe(pd.DataFrame(usage), use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Nutzung vorhanden.")

    st.subheader("Payments")

    payments = list_purchases(st.session_state.get("user"))

    if payments:
        st.dataframe(pd.DataFrame(payments), use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Zahlungen vorhanden.")


def render_redeem():
    require_login()

    st.title("🎁 Redeem Code")
    st.write("Löse Codes ein und erhalte Tokens oder Plan-Upgrades.")

    code = st.text_input("Code", placeholder="DEIN-CODE")

    if st.button("Code einlösen", use_container_width=True):
        if not code:
            st.warning("Bitte Code eingeben.")
            return

        ok, msg = redeem_code(st.session_state.get("user"), code)

        if ok:
            user = get_user(st.session_state.get("user"))

            if user:
                sync_session_user(user)

            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def render_support():
    require_login()

    st.title("🆘 Support Tickets")
    st.write("Erstelle ein Ticket. Unser Team hilft dir weiter.")

    with st.form("support_ticket_form"):
        category = st.selectbox(
            "Kategorie",
            ["Account", "Payment", "Tokens", "AI Tool", "Bug", "Sonstiges"],
        )

        subject = st.text_input("Betreff")
        message = st.text_area("Nachricht", height=160)

        submitted = st.form_submit_button("Ticket erstellen", use_container_width=True)

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
        st.dataframe(pd.DataFrame(own_tickets), use_container_width=True, hide_index=True)
    else:
        st.info("Du hast noch keine Tickets.")


def plan_features(plan_key):
    if plan_key == "pro":
        return [
            "600 Tokens",
            "Image AI",
            "Coding AI",
            "Music AI",
            "Standard Support",
        ]

    if plan_key == "grand":
        return [
            "2500 Tokens",
            "Video AI",
            "Reels Creator",
            "Verbesserter Support",
            "Bessere APIs",
            "Alles aus Pro",
        ]

    if plan_key == "elite":
        return [
            "12000 Tokens",
            "Leistungsstarke APIs",
            "Verbesserte Videoqualität",
            "Business Level",
            "Alles freigeschaltet",
            "Priorisierter Support",
        ]

    return PLANS.get(plan_key, {}).get("features", [])


def plan_card(plan_key):
    plan = PLANS[plan_key]

    with st.container(border=True):
        st.subheader(plan["label"])
        st.markdown(f"## {plan['price']}")
        st.metric("Tokens", plan["tokens"])

        st.divider()

        for feature in plan_features(plan_key):
            st.write(f"✅ {feature}")

        st.divider()

        if st.button(f"Buy {plan['label']}", key=f"buy_{plan_key}", use_container_width=True):
            st.session_state.selected_plan = plan_key
            st.success(f"{plan['label']} ausgewählt. Stripe Checkout kann hier verbunden werden.")


def render_premium():
    require_login()

    st.title("💎 Premium")
    st.write("Upgrade deinen Account und schalte mehr AI Features frei.")

    col1, col2, col3 = st.columns(3)

    with col1:
        plan_card("pro")

    with col2:
        plan_card("grand")

    with col3:
        plan_card("elite")