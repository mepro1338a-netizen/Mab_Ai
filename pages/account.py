import streamlit as st
from db_manager import fetch_all, fetch_one, execute
from database import get_user, list_usage, redeem_code
from ui_helpers import require_login, sync_session_user


def init_support_tables():
    execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id SERIAL PRIMARY KEY,
        username TEXT,
        email TEXT,
        category TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    execute("""
    CREATE TABLE IF NOT EXISTS support_replies (
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER,
        sender TEXT,
        sender_role TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


def render_dashboard():
    require_login()

    user = get_user(st.session_state.user)
    sync_session_user(user)

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">ACCOUNT</span>
            <h1>📊 Dashboard</h1>
            <p>Deine Account-Daten, Tokens und letzte Nutzung.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("User", st.session_state.user)
    c2.metric("Plan", st.session_state.plan)
    c3.metric("Tokens", st.session_state.tokens)

    st.markdown("### Letzte Nutzung")
    usage = list_usage(st.session_state.user)

    if usage:
        st.dataframe(usage[:20], use_container_width=True)
    else:
        st.info("Noch keine Nutzung vorhanden.")


def render_redeem():
    require_login()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">REDEEM</span>
            <h1>🎁 Redeem Code</h1>
            <p>Gib hier deinen Premium-, Token- oder Bonus-Code ein.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    code = st.text_input("Code eingeben", key="redeem_page_code")

    if st.button("🎁 Code einlösen", key="redeem_page_btn"):
        if not code.strip():
            st.error("Bitte Code eingeben.")
        else:
            ok, msg = redeem_code(st.session_state.user, code.strip())

            if ok:
                user = get_user(st.session_state.user)
                sync_session_user(user)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def render_support():
    require_login()
    init_support_tables()

    st.markdown(
        """
        <div class="page-card">
            <span class="badge">SUPPORT</span>
            <h1>🆘 Support Center</h1>
            <p>Erstelle Tickets und lies Antworten vom Team.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_new, tab_my = st.tabs(["Neues Ticket", "Meine Tickets"])

    with tab_new:
        subject = st.text_input("Betreff", key="support_subject")
        message = st.text_area("Nachricht", key="support_msg", height=180)
        category = st.selectbox(
            "Kategorie",
            ["Allgemein", "Account", "Payment", "Technik", "Bug"],
            key="support_category",
        )

        if st.button("Ticket senden", key="ticket_send"):
            if not subject.strip() or not message.strip():
                st.error("Bitte alles ausfüllen.")
            else:
                execute("""
                INSERT INTO support_tickets (
                    username, email, category, subject, message, status
                )
                VALUES (%s, %s, %s, %s, %s, 'open')
                """, (
                    st.session_state.user,
                    st.session_state.email,
                    category,
                    subject,
                    message,
                ))

                st.success("Ticket wurde erstellt.")
                st.rerun()

    with tab_my:
        tickets = fetch_all("""
        SELECT *
        FROM support_tickets
        WHERE username=%s
        ORDER BY created_at DESC
        """, (st.session_state.user,))

        if not tickets:
            st.info("Noch keine Tickets vorhanden.")
        else:
            for ticket in tickets:
                with st.expander(
                    f"#{ticket['id']} · {ticket['subject']} · {ticket['status']}"
                ):
                    st.markdown(f"**Kategorie:** {ticket['category']}")
                    st.markdown(f"**Erstellt:** {ticket['created_at']}")
                    st.markdown("### Deine Nachricht")
                    st.write(ticket["message"])

                    replies = fetch_all("""
                    SELECT *
                    FROM support_replies
                    WHERE ticket_id=%s
                    ORDER BY created_at ASC
                    """, (ticket["id"],))

                    if replies:
                        st.markdown("### Antworten")
                        for reply in replies:
                            st.markdown(
                                f"""
                                <div class="page-card">
                                    <b>{reply['sender']}</b> · {reply['sender_role']}<br>
                                    <small>{reply['created_at']}</small>
                                    <p>{reply['message']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("Noch keine Antwort vom Team.")


def render_premium():
    st.markdown(
        """
        <div class="page-card">
            <span class="badge">PREMIUM</span>
            <h1>💳 Premium</h1>
            <p>Upgrade deinen Account und schalte mehr AI Features frei.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plans = [
        ("pro", "Pro", "9.99€ / Monat", "1200 Tokens<br>Image AI<br>Coding AI<br>Music AI<br>Reels Creator"),
        ("grand", "Grand", "49.99€ / Monat", "4000 Tokens<br>Alles aus Pro<br>Video AI<br>Stärkere Workflows"),
        ("elite", "Elite", "199€ / Monat", "Alles freigeschaltet<br>Maximale API-Leistung<br>Priorität"),
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

                st.error("Stripe verbinden wir im nächsten Schritt.")