import streamlit as st

from database import (
    get_user,
    create_support_message,
    list_usage,
    list_purchases,
)

from ui_helpers import require_login, sync_session_user


def render_dashboard():
    require_login()

    user = get_user(st.session_state.user)
    sync_session_user(user)

    st.title("📊 User Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("User", st.session_state.user)
    col2.metric("Plan", st.session_state.plan)
    col3.metric("Tokens", st.session_state.tokens)

    st.markdown('<div class="page-card">', unsafe_allow_html=True)
    st.markdown("### Letzte Nutzung")

    usage = list_usage(st.session_state.user)

    if usage:
        st.dataframe(usage[:20], use_container_width=True)
    else:
        st.info("Noch keine Nutzung vorhanden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_support():
    require_login()

    st.title("🆘 Support")

    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    subject = st.text_input("Betreff", key="support_subject")
    message = st.text_area("Nachricht", key="support_msg", height=180)

    category = st.selectbox(
        "Kategorie",
        ["Allgemein", "Account", "Payment", "Technik", "Bug"],
        key="support_category",
    )

    if st.button("Ticket senden", key="ticket_send"):
        if not subject or not message:
            st.error("Bitte alles ausfüllen.")
        else:
            ok, response = create_support_message(
                username=st.session_state.user,
                email=st.session_state.email,
                category=category,
                subject=subject,
                message=message,
            )

            if ok:
                st.success(response)
            else:
                st.error(response)

    st.markdown("</div>", unsafe_allow_html=True)


def render_premium():
    st.title("💳 Buy Premium")

    plans = [
        (
            "pro",
            "Pro",
            "9.99€ / Monat",
            "1200 Tokens<br>Image Generator<br>Coding Area<br>Music Generator<br>Short Reels",
        ),
        (
            "grand",
            "Grand",
            "49.99€ / Monat",
            "4000 Tokens<br>Alles aus Pro<br>AI Video Generator<br>Stärkere Workflows",
        ),
        (
            "elite",
            "Elite",
            "199€ / Monat",
            "Alles freigeschaltet<br>Höchste API-Leistung<br>Beste Qualität<br>Maximaler Zugriff",
        ),
    ]

    cols = st.columns(3)

    for col, item in zip(cols, plans):
        plan_key, title, price, features = item

        with col:
            st.markdown(
                f"""
                <div class="page-card">
                    <h2>{title}</h2>
                    <h3 style="color:#ffd700;">{price}</h3>
                    <p>{features}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(f"Buy {title}", key=f"buy_{plan_key}"):
                if not st.session_state.get("user"):
                    st.warning("Bitte zuerst einloggen.")
                    st.session_state.page = "login"
                    st.rerun()

                st.error("Stripe wird im nächsten Step final verbunden.")


def render_payment_history():
    require_login()

    st.title("💳 Zahlungsverlauf")

    purchases = list_purchases(st.session_state.user)

    if purchases:
        st.dataframe(purchases, use_container_width=True)
    else:
        st.info("Noch keine Zahlungen vorhanden.")