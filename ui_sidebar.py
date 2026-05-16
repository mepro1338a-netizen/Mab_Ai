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


def refresh_user():
    user = get_user(st.session_state.get("user"))
    if user:
        sync_session_user(user)


def current_plan_key():
    return st.session_state.get("plan", "free")


def current_plan():
    return PLANS.get(current_plan_key(), PLANS["free"])


def render_dashboard():
    require_login()
    refresh_user()

    plan = current_plan()
    tokens = int(st.session_state.get("tokens", 0) or 0)

    st.title("ðŸ“Š Dashboard")
    st.write("Dein MaByte Account, Tokens, Nutzung und Plan-Status.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Plan", plan.get("label", current_plan_key()))

    with c2:
        st.metric("Tokens", tokens)

    with c3:
        st.metric("Role", st.session_state.get("role", "user"))

    with c4:
        st.metric("Plan Tokens", plan.get("tokens", 0))

    st.divider()

    st.subheader("âš¡ Token Kosten")

    token_rows = [
        {"Tool": "Memory Chat", "Kosten": TOKEN_COSTS.get("chat", 1), "Freigabe": "Alle PlÃ¤ne"},
        {"Tool": "Coding AI", "Kosten": TOKEN_COSTS.get("coding", 4), "Freigabe": "Pro+"},
        {"Tool": "Image AI", "Kosten": TOKEN_COSTS.get("image", 15), "Freigabe": "Pro+"},
        {"Tool": "Music AI", "Kosten": TOKEN_COSTS.get("music", 10), "Freigabe": "Pro+"},
        {"Tool": "Reels Creator", "Kosten": TOKEN_COSTS.get("reels", 20), "Freigabe": "Grand+"},
        {"Tool": "Video Base", "Kosten": TOKEN_COSTS.get("video_base", 10), "Freigabe": "Grand+"},
        {"Tool": "Video pro Sekunde", "Kosten": TOKEN_COSTS.get("video_second", 5), "Freigabe": "Grand+"},
    ]

    st.dataframe(
        pd.DataFrame(token_rows),
        width="stretch",
        hide_index=True,
    )

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("ðŸ§¾ Letzte Nutzung")
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

    st.title("ðŸŽ Redeem Code")
    st.write("LÃ¶se Codes ein und erhalte Tokens oder Plan-Upgrades.")

    with st.container(border=True):
        code = st.text_input("Code", placeholder="DEIN-CODE")

        if st.button("Code einlÃ¶sen", width="stretch"):
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

    st.title("ðŸ†˜ Support Tickets")
    st.write("Erstelle ein Ticket. Unser Team hilft dir weiter.")

    with st.container(border=True):
        with st.form("support_ticket_form"):
            category = st.selectbox(
                "Kategorie",
                [
                    "Account",
                    "Payment",
                    "Tokens",
                    "AI Tool",
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
                    st.warning("Bitte Betreff und Nachricht ausfÃ¼llen.")
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
            "4000 Tokens",
            "Video AI",
            "Reels Creator",
            "Auto-Posting Vorbereitung",
            "Verbesserter Support",
            "Bessere APIs",
            "Alles aus Pro",
        ]

    if plan_key == "elite":
        return [
            "14000 Tokens",
            "Leistungsstarke APIs",
            "Verbesserte VideoqualitÃ¤t",
            "Business Level",
            "Alles freigeschaltet",
            "Priorisierter Support",
        ]

    return PLANS.get(plan_key, {}).get("features", [])


def plan_card(plan_key):
    plan = PLANS[plan_key]
    current = current_plan_key() == plan_key

    with st.container(border=True):
        if current:
            st.success("Aktueller Plan")

        st.subheader(plan["label"])
        st.markdown(f"## {plan['price']}")
        st.metric("Tokens", plan["tokens"])

        st.divider()

        for feature in plan_features(plan_key):
            st.write(f"âœ… {feature}")

        st.divider()

        button_label = "Aktiv" if current else f"Buy {plan['label']}"

        if st.button(
            button_label,
            key=f"buy_{plan_key}",
            width="stretch",
            disabled=current,
        ):
            st.session_state.selected_plan = plan_key
            st.success(
                f"{plan['label']} ausgewÃ¤hlt. Stripe Checkout kann hier verbunden werden."
            )


def render_premium():
    require_login()
    refresh_user()

    st.title("ðŸ’Ž Premium")
    st.write("Upgrade deinen Account und schalte mehr AI Features frei.")

    st.info(
        "Pro = Creator Tools. Grand = Video, Reels & Auto-Posting. Elite = Business Level mit hÃ¶chster Leistung."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        plan_card("pro")

    with col2:
        plan_card("grand")

    with col3:
        plan_card("elite")
