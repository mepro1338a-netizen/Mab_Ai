import streamlit as st

from db_manager import execute, fetch_all
from database import get_user, list_usage
from redeem_tracking import redeem_code_tracked
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

    st.markdown("""
    <div class="page-card">
        <span class="badge">ACCOUNT</span>
        <h1>📊 Dashboard</h1>
        <p>Deine Account-Daten, Tokens und letzte Nutzung.</p>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
    <div class="page-card">
        <span class="badge">REDEEM</span>
        <h1>🎁 Redeem Code</h1>
        <p>Gib hier deinen Premium-, Token- oder Bonus-Code ein.</p>
    </div>
    """, unsafe_allow_html=True)

    code = st.text_input("Code eingeben", key="redeem_page_code")

    if st.button("🎁 Code einlösen", key="redeem_page_btn"):
        if not code.strip():
            st.error("Bitte Code eingeben.")
        else:
            ok, msg = redeem_code_tracked(
                st.session_state.user,
                code.strip(),
            )

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

    st.markdown("""
    <div class="page-card">
        <span class="badge">SUPPORT</span>
        <h1>🆘 Support Center</h1>
        <p>Erstelle Tickets und kommuniziere mit dem Team.</p>
    </div>
    """, unsafe_allow_html=True)

    tab_new, tab_my = st.tabs([
        "➕ Neues Ticket",
        "🎫 Meine Tickets",
    ])

    with tab_new:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)

        subject = st.text_input("Betreff", key="support_subject")

        category = st.selectbox(
            "Kategorie",
            [
                "Allgemein",
                "Account",
                "Payment",
                "Technik",
                "Bug",
            ],
            key="support_category",
        )

        message = st.text_area(
            "Nachricht",
            key="support_msg",
            height=180,
        )

        if st.button("Ticket senden", key="ticket_send"):
            if not subject.strip() or not message.strip():
                st.error("Bitte alles ausfüllen.")
            else:
                execute("""
                INSERT INTO support_tickets (
                    username,
                    email,
                    category,
                    subject,
                    message,
                    status
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

        st.markdown("</div>", unsafe_allow_html=True)

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
                status = ticket.get("status", "open")

                icon = "🟢" if status == "open" else "⚫"

                with st.expander(
                    f"{icon} #{ticket['id']} · {ticket['subject']} · {status}"
                ):
                    st.markdown(f"**Kategorie:** {ticket['category']}")
                    st.markdown(f"**Erstellt:** {ticket['created_at']}")

                    st.markdown("""
                    <div class="page-card">
                        <b>Deine ursprüngliche Nachricht</b>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write(ticket["message"])

                    replies = fetch_all("""
                    SELECT *
                    FROM support_replies
                    WHERE ticket_id=%s
                    ORDER BY created_at ASC
                    """, (ticket["id"],))

                    if replies:
                        st.markdown("### Verlauf")

                        for reply in replies:
                            role_badge = reply.get("sender_role", "user")
                            sender = reply.get("sender", "Unbekannt")

                            st.markdown(
                                f"""
                                <div class="page-card">
                                    <b>{sender}</b>
                                    <span style="color:#ffd700;">
                                        ({role_badge})
                                    </span><br>

                                    <small>
                                        {reply.get("created_at")}
                                    </small>

                                    <p style="margin-top:12px;">
                                        {reply.get("message")}
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("Noch keine Antwort vom Team.")

                    if status != "closed":
                        reply_text = st.text_area(
                            "Antwort hinzufügen",
                            key=f"user_reply_{ticket['id']}",
                            height=120,
                        )

                        if st.button(
                            "Antwort senden",
                            key=f"user_reply_btn_{ticket['id']}"
                        ):
                            if not reply_text.strip():
                                st.error("Bitte Antwort eingeben.")
                            else:
                                execute("""
                                INSERT INTO support_replies (
                                    ticket_id,
                                    sender,
                                    sender_role,
                                    message
                                )
                                VALUES (%s, %s, %s, %s)
                                """, (
                                    ticket["id"],
                                    st.session_state.user,
                                    st.session_state.role,
                                    reply_text,
                                ))

                                execute("""
                                UPDATE support_tickets
                                SET status='open'
                                WHERE id=%s
                                """, (ticket["id"],))

                                st.success("Antwort gesendet.")
                                st.rerun()
                    else:
                        st.warning("Dieses Ticket ist geschlossen.")


def render_premium():
    st.markdown("""
    <div class="page-card">
        <span class="badge">PREMIUM</span>
        <h1>💳 Premium</h1>
        <p>Upgrade deinen Account und schalte mehr AI Features frei.</p>
    </div>
    """, unsafe_allow_html=True)

    plans = [
        (
            "pro",
            "Pro",
            "9.99€ / Monat",
            "1200 Tokens<br>Image AI<br>Coding AI<br>Music AI<br>Reels Creator"
        ),
        (
            "grand",
            "Grand",
            "49.99€ / Monat",
            "4000 Tokens<br>Alles aus Pro<br>Video AI<br>Stärkere Workflows"
        ),
        (
            "elite",
            "Elite",
            "199€ / Monat",
            "Alles freigeschaltet<br>Maximale API-Leistung"
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
                    <h3 style="color:#ffd700;">
                        {price}
                    </h3>
                    <p>{features}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Buy {title}",
                key=f"buy_{plan_key}"
            ):
                st.error(
                    "Stripe verbinden wir später mit deiner Domain."
                )
